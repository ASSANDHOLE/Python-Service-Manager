from enum import Enum
from dataclasses import dataclass


@dataclass
class DnsApiConfig:
    """
    DNS API configuration

    Attributes
    ----------
    api_key : str
        API key
    email : str
        Email of the account
    zone_id : str
        Zone ID
    edit : bool
        Whether the api key can edit DNS records
    """

    api_key: str
    email: str
    zone_id: str
    edit: bool


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
    create_time : int = 0
        Service creation time
    valid : bool = True
        Whether the service is valid
    valid_until : int = 0
        Service valid until
    data : dict = None
        Service data, note that the data should be JSON serializable
    """

    name: str
    type: ServiceType
    description: str = ''
    create_time: int = 0
    valid: bool = True
    valid_until: int = 0
    data: dict = None
