import time

from evaluate import has_root_privilege
from config import Config
from service import Services


def main():
    config = Config()
    if config.require_root and not has_root_privilege():
        print('This program requires root privilege')
        exit(1)
    services = Services(config)
    while True:
        time.sleep(config.sleep_interval)
        services.evaluate_services()


if __name__ == '__main__':
    main()
