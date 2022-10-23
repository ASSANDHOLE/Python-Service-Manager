import socket
import subprocess
import os
from typing import Literal

import requests


def has_root_privilege() -> bool:
    """
    Check if the current user has root privilege

    Returns
    -------
    bool
        True if the current user has root privilege, False otherwise
    """
    return os.geteuid() == 0


def get_systemd_service_status(service_name: str) -> int:
    """
    Get the status of a systemd service

    Parameters
    ----------
    service_name : str
        The name of the systemd service

    Returns
    -------
    int
        The status of the systemd service, 0 if the service is active
    """
    try:
        ret = subprocess.call(['systemctl', 'is-active', '--quiet', service_name])
        return ret
    except subprocess.CalledProcessError:
        return -1


def tcp_connect(host: str, port: int) -> bool:
    """
    Check if a TCP connection can be established to a host

    Parameters
    ----------
    host : str
        The host to connect to
    port : int
        The port to connect to

    Returns
    -------
    bool
        True if the connection can be established, False otherwise
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    try:
        sock.connect((host, port))
        return True
    except socket.error:
        return False
    finally:
        sock.close()


def http_get(url: str) -> bool:
    """
    Check if an HTTP GET request can be sent to a host

    Parameters
    ----------
    url : str
        The URL to send the request to

    Returns
    -------
    bool
        True if the request can be sent, False otherwise
    """
    try:
        r = requests.get(url, timeout=5)
        return isinstance(r.status_code, int)
    except requests.exceptions.RequestException:
        return False


def check_pid(pid: int) -> bool:
    """
    Check if a process is running

    Parameters
    ----------
    pid : int
        The PID of the process

    Returns
    -------
    bool
        True if the process is running, False otherwise
    """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def ping_test(host: str) -> bool:
    """
    Check if a host can be pinged

    Parameters
    ----------
    host : str
        The host to ping

    Returns
    -------
    bool
        True if the host can be pinged, False otherwise
    """
    try:
        ret = subprocess.call(['ping', '-c', '2', '-W', '2', host], stdout=subprocess.DEVNULL)
        return ret == 0
    except subprocess.CalledProcessError:
        return False


def file_exists(path: str) -> bool:
    """
    Check if a file exists

    Parameters
    ----------
    path : str
        The path of the file

    Returns
    -------
    bool
        True if the file exists, False otherwise
    """
    return os.path.isfile(path)


def get_local_ip(version: Literal[4, 6] = 4) -> str:
    """
    Get the local IP address

    Parameters
    ----------
    version : Literal[4, 6]
        The IP version to get

    Returns
    -------
    str
        The local IP address
    """
    inet = socket.AF_INET if version == 4 else socket.AF_INET6
    return socket.getaddrinfo(socket.gethostname(), None, inet)[0][-1][0]


def dns_equals_this(domain: str, version: Literal[4, 6] = 4) -> bool:
    """
    Check if a domain resolves to this host

    Parameters
    ----------
    domain : str
        The domain to check
    version : Literal[4, 6]
        The IP version to check

    Returns
    -------
    bool
        True if the domain resolves to this host, False otherwise
    """
    inet = socket.AF_INET if version == 4 else socket.AF_INET6
    try:
        ip = socket.getaddrinfo(domain, None, inet)[0][-1][0]
        local_ips = socket.getaddrinfo(socket.gethostname(), None, inet)
        local_ips = set([ip[-1][0] for ip in local_ips])
        return ip in local_ips
    except socket.gaierror:
        return False
