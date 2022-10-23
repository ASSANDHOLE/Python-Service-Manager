import os
import json

from data import Service, ServiceType

from utils import DataclassEnumJSONEncoder

DATA_STORE_PATH = os.path.join(os.path.dirname(__file__), 'data_store.json')


class RegisteredServices:
    def __init__(self):
        # name(str): data(Service)
        self.services = {}

    def load(self, path: str = DATA_STORE_PATH) -> bool:
        try:
            with open(path, 'r') as f:
                raw_data = json.load(f)
        except FileNotFoundError:
            return False
        for k, v in raw_data.items():
            v['type'] = ServiceType(v['type'])
            self.services[k] = Service(**v)
        return True

    def save(self, path: str = DATA_STORE_PATH):
        with open(path, 'w') as f:
            json.dump(self.services, f, indent=4, cls=DataclassEnumJSONEncoder)

    def is_registered(self, name: str, service_type: ServiceType) -> bool:
        return name in self.services and self.services[name].type == service_type

    def register_service(self, name: str, service: Service):
        self.services[name] = service
        print(self.services)
        self.save()

    def unregister_service(self, name: str, service_type: ServiceType):
        if name in self.services and self.services[name].type == service_type:
            del self.services[name]
            self.save()

    def same_service(self, name: str, service: Service) -> bool:
        if name in self.services:
            prev_srv = self.services[name]
            same = True
            same &= prev_srv.name == service.name
            same &= prev_srv.type == service.type
            same &= prev_srv.description == service.description
            same &= prev_srv.data == service.data
            return same
        return False

    def get_service(self, name: str) -> Service | None:
        return self.services[name] if name in self.services else None

    def change_service(self, name: str, service: Service):
        self.services[name] = service
        self.save()
