import datetime
import json
import time
from typing import List

from flask import Flask, Response, request

from data import *
from config import Config
from service import RegisteredServices

from cloudflare_v4_api import dns


class EndPointAction:
    def __init__(self, action: callable):
        self.action = action

    def __call__(self, *args, **kwargs) -> Response:
        response = self.action(*args, **kwargs)
        return response


class FlaskAppWrapper:
    def __init__(self, name: str):
        self.app = Flask(name)

    def run(self):
        self.app.run()

    def add_endpoint(self, endpoint: str, endpoint_name, handler: callable, method: List[str]) -> None:
        self.app.add_url_rule(endpoint, endpoint_name, EndPointAction(handler), methods=method)


class Server:
    def __init__(self, name: str, config: Config, registered_services: RegisteredServices):
        self.config = config
        self.registered_services = registered_services
        self.app = FlaskAppWrapper(name)
        self.app.add_endpoint('/api/srv/reg', 'register_service', self.register_service, ['POST'])
        self.app.add_endpoint('/api/srv/renew', 'get_dns_record', self.get_dns_record, ['POST'])
        self.app.add_endpoint('/api/dns/get', 'get_dns_record', self.get_dns_record, ['GET', 'POST'])
        self.app.add_endpoint('/api/dns/add', 'add_(or_update)_dns_record', self.add_or_update_dns_record, ['POST'])
        self.app.add_endpoint('/api/dns/update', '(add_or_)update_dns_record', self.add_or_update_dns_record, ['POST'])
        self.app.add_endpoint('/api/dns/delete', 'delete_dns_record', self.delete_dns_record, ['GET', 'POST'])
        self.app.add_endpoint('/', 'show_service_status', self.get_service_status, ['GET', 'POST'])

    def _register_service(self, name: str, service_type: ServiceType, description: str, valid: bool, data: dict) -> Response:
        valid_until = int(time.time() + self.config.valid_period)
        srv = Service(name, service_type, description, int(time.time()), valid, valid_until, data)
        if self.registered_services.is_registered(name, service_type):
            if self.registered_services.same_service(name, srv):
                self.registered_services.get_service(name).valid_until = valid_until
                return Response('Service already registered', status=200)
            else:
                prev_srv = self.registered_services.get_service(name)
                srv.create_time = prev_srv.create_time
                self.registered_services.change_service(name, srv)
                return Response('Service updated', status=200)
        else:
            self.registered_services.register_service(name, srv)
            return Response('Service registered', status=200)

    def _auth_get_dom(self):
        if request.method == 'GET':
            values = request.args
        else:
            values = request.get_json()
        token = values.get('token', 'none')
        if not self.config.evaluate_access_token(token):
            return Response('Unauthorized', status=401)
        domain = values['domain']
        if not self.config.has_dns_api(domain):
            return Response('Domain Zone not found', status=404)
        return domain, values

    def register_service(self) -> Response:
        values = request.get_json()
        token = values.get('token', 'none')
        if not self.config.evaluate_access_token(token):
            return Response('Unauthorized', status=401)
        name = values['name']
        service_type = ServiceType(values['type'])
        valid = bool(values['valid'])
        description = values.get('description', '')
        data = values.get('data', {})
        return self._register_service(name, service_type, description, data)

    def get_dns_record(self) -> Response:
        res = self._auth_get_dom()
        if isinstance(res, Response):
            return res
        domain, values = res
        dom_info = self.config.get_dns_api(domain)
        dns_result = dns.get_all_dns_record(dom_info.zone_id, dom_info.email, dom_info.api_key)
        if dns_result is None:
            return Response('Error', status=500)
        else:
            resp = Response(status=200)
            resp.content_type = 'application/json'
            resp.data = json.dumps(dns_result)
            return resp

    def add_or_update_dns_record(self) -> Response:
        res = self._auth_get_dom()
        if isinstance(res, Response):
            return res
        domain, values = res
        dom_info = self.config.get_dns_api(domain)
        dns_result = dns.get_all_dns_record(dom_info.zone_id, dom_info.email, dom_info.api_key)
        if dns_result is None:
            return Response('Error', status=500)
        else:
            rec_type = values['type']
            content = values['content']
            ttl = values.get('ttl', None)
            if ttl is not None:
                ttl = int(ttl)
            priority = values.get('priority', None)
            if priority is not None:
                priority = int(priority)
            proxied = values.get('proxied', False)

            # if domain in dns_result:
            has_dns = False
            rec_id = ''
            for dns_record in dns_result:
                if dns_record['name'] == domain:
                    has_dns = True
                    rec_id = dns_record['id']
                    break
            if has_dns:
                # update dns
                resp = dns.update_dns_record(dom_info.zone_id, dom_info.email, dom_info.api_key,
                                             rec_id, rec_type, domain, content, ttl, proxied)
            else:
                # add dns
                resp = dns.create_dns_record(dom_info.zone_id, dom_info.email, dom_info.api_key,
                                             rec_type, domain, content, ttl, priority, proxied)
            if resp is None:
                return Response('Error', status=500)
            else:
                ret = Response(status=200)
                ret.content_type = 'application/json'
                ret.data = json.dumps({'type': 'update' if has_dns else 'add', 'result': resp})
                return ret

    def delete_dns_record(self) -> Response:
        res = self._auth_get_dom()
        if isinstance(res, Response):
            return res
        domain, values = res
        dom_info = self.config.get_dns_api(domain)
        dns_result = dns.get_all_dns_record(dom_info.zone_id, dom_info.email, dom_info.api_key)
        if dns_result is None:
            return Response('Error', status=500)
        else:
            rec_id = ''
            for dns_record in dns_result:
                if dns_record['name'] == domain:
                    rec_id = dns_record['id']
                    break
            if rec_id == '':
                return Response('DNS Record not found', status=404)
            else:
                resp = dns.delete_dns_record(dom_info.zone_id, dom_info.email, dom_info.api_key, rec_id)
                if resp is None:
                    return Response('Error', status=500)
                else:
                    ret = Response(status=200)
                    ret.content_type = 'application/json'
                    ret.data = json.dumps(resp)
                    return ret

    def get_service_status(self) -> Response:
        if request.method == 'GET':
            values = request.args
        else:
            values = request.get_json()
        token = values.get('token', 'none')
        show_detail = True
        if not self.config.evaluate_access_token(token):
            show_detail = False
        result = {}
        for name, srv in self.registered_services.services.items():
            if srv is ServiceType.DNS and not show_detail:
                continue
            status = 'offline' if srv.valid else ('online' if srv.valid_until > time.time() else 'unknown/expired')
            r = {
                'type': srv.type.name,
                'description': srv.description,
                'status': status,
            }
            if show_detail:
                r['create_time'] = datetime.datetime.fromtimestamp(srv.create_time).strftime('%Y-%m-%d %H:%M:%S')
                r['data'] = srv.data
            result[name] = r
        resp = Response(status=200)
        resp.content_type = 'application/json'
        resp.data = json.dumps(result)
        return resp

    def run(self):
        self.app.run()


def main():
    config = Config()
    if not config.load():
        print('CFG error')
        return
    registered_services = RegisteredServices()
    registered_services.load()
    print(config.access_token)
    server = Server(__name__, config, registered_services)
    server.run()


if __name__ == '__main__':
    main()
