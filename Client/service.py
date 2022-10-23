import socket
import time

import requests

from config import Config

from data import Service, ServiceType, METHODS
from evaluate import get_local_ip


def handle_dns(service: Service, config: Config) -> bool:
    """
    Handle DNS service when ip not match this host

    Parameters
    ----------
    service : Service
        The service to handle
    config : Config
        The configuration that contains the server URL, etc.

    Returns
    -------
    bool
        True if success
    """
    try:
        this_ip = get_local_ip(service.method['param'][-1])
    except socket.gaierror:
        return False
    url = f'{config.server_url}/api/dns/update'
    rec_type = 'A' if service.method['param'][-1] == 4 else 'AAAA'
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        'token': config.access_token,
        'domain': service.data['domain'],
        'type': rec_type,
        'content': this_ip,
    }
    if 'ttl' in service.data:
        data['ttl'] = service.data['ttl']
    if 'proxied' in service.data:
        data['proxied'] = service.data['proxied']
    if 'priority' in service.data:
        data['priority'] = service.data['priority']
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code == 200:
        return True
    return False


def notify_server(service: Service, config: Config, status: bool, first_run: bool = False) -> bool:
    """
    Notify the server that this service's status

    Parameters
    ----------
    service : Service
        The service to notify
    config : Config
        The configuration that contains the server URL, etc.
    status : bool
        The status of the service
    first_run : bool = False
        Whether this is the first run, by default False

    Returns
    -------
    bool
        True if success
    """
    url = f'{config.server_url}/api/srv/{"renew" if not first_run else "reg"}'
    headers = {
        'Content-Type': 'application/json',
    }
    data = {
        'token': config.access_token,
        'name': service.name,
        'type': service.type.value,
        'valid': status,
    }
    if first_run:
        data['description'] = service.description
        data['data'] = service.data
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code == 200:
        return True
    return False


class Services:
    def __init__(self, config: Config):
        self.config = config
        self.services_dict = config.services
        self.services = {}
        self.parse_services()
        self.evaluate_services(first_run=True)

    def parse_services(self) -> None:
        for service in self.services_dict:
            service['type'] = ServiceType(service['type'])
            service['valid_until'] = int(time.time() + service['valid_period'])
            self.services[service['name']] = Service(**service)

    def evaluate_services(self, first_run: bool = False) -> None:
        for name, srv in self.services.items():
            if time.time() < srv.valid_until and not first_run:
                continue
            res = METHODS[srv.method['name']](*srv.method['param'])
            if res:
                srv.valid_until = int(time.time() + srv.valid_period)
            else:
                if srv.type == ServiceType.DNS:
                    res = handle_dns(srv, self.config)
            notify_server(srv, self.config, res, first_run)
