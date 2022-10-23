from dataclasses import dataclass
from enum import Enum


class ServiceType(str, Enum):
    """
    Service type

    Attributes
    ----------
    DNS : str
        DNS service, change DNS records for changes in IP address
    HTTP : str
        HTTP service (e.g. http file server)
    HTTPS : str
        HTTPS service (e.g. https file server)
    FRPS : str
        FRP server
    FRPC : str
        FRP client
    PROXY : str
        Proxy service (usually a Xray-compatible proxy server)
    """

    DNS = 'dns'
    HTTP = 'http'
    HTTPS = 'https'
    FRPS = 'frps'
    FRPC = 'frpc'
    PROXY = 'proxy'
    ROBOT = 'robot'


@dataclass
class Service:
    """
    Service configuration

    Attributes
    ----------
    name : str
        Service name
    type : ServiceType
        Service type
    description : str = ''
        Service description
    valid_interval : int = 0
        Service valid interval (in seconds)
    valid_until : int = 0
        Service valid until
    data : dict = None
        Service data, note that the data should be JSON serializable
    method : dict = None
        Service checking method, note that the method should be JSON serializable
    """

    name: str
    type: ServiceType
    description: str = ''
    valid_interval: int = 0
    valid_until: int = 0
    data: dict = None
    method: dict = None
