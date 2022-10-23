import os
import json

CFG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')


class Config:
    def __init__(self):
        self.config = {}
        self.load_config()
        self.server_url = self.config['general']['server']['url']
        self.sleep_interval = self.config['general']['local']['sleep_interval']
        self.require_root = self.config['general']['local']['require_root']
        self.access_token = self.config['auth']['access_token']
        self.services = self.config['services']

    def load_config(self, path: str = CFG_FILE_PATH) -> None:
        with open(path, 'r') as f:
            self.config = json.load(f)
