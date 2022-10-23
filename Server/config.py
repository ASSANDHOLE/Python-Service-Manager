import os
import json

from data import DnsApiConfig

CFG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')


class Config:
    def __init__(self):
        self.dns_api = {}
        self.access_token = ''
        self.valid_period = 120  # seconds

    def load(self, path: str = CFG_FILE_PATH) -> bool:
        try:
            with open(path, 'r') as f:
                raw_data = json.load(f)
        except FileNotFoundError:
            return False
        if 'auth' in raw_data and 'access_token' in raw_data['auth']:
            self.access_token = raw_data['auth']['access_token']
        else:
            raise ValueError('Invalid config file, missing access token: auth.access_token')

        if 'general' in raw_data and 'valid_period' in raw_data['general']:
            self.valid_period = int(raw_data['general']['valid_period'])

        at_least_one = False
        if 'dns' in raw_data:
            at_least_one = True
            dns = raw_data['dns']
            for k, v in dns.items():
                self.dns_api[k] = DnsApiConfig(**v)

        return at_least_one

    def evaluate_access_token(self, token: str) -> bool:
        return token == self.access_token

    def has_dns_api(self, domain: str) -> bool:
        for dom in self.dns_api.keys():
            if domain.endswith(dom):
                return True
        return False

    def get_dns_api(self, domain: str) -> DnsApiConfig | None:
        for dom, val in self.dns_api.items():
            if domain.endswith(dom):
                return val
        return None
