from typing import List, Literal, Optional

import requests


def get_all_dns_record(zone_id: str, email: str, api_key: str) -> List[dict] | None:
    """
    Get all DNS records

    Parameters
    ----------
    zone_id : str
        Zone ID
    email : str
        Email of the account
    api_key : str
        API key

    Returns
    -------
    List[Dict[str, str]]
        List of DNS records
    """
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
    headers = {
        'X-Auth-Email': email,
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    r = requests.get(url, headers=headers)
    print(r.text)
    if r.status_code == 200:
        return r.json()['result']
    else:
        return None


def create_dns_record(zone_id: str,
                      email: str,
                      api_key: str,
                      rec_type: Literal['A', 'AAAA', 'CNAME', 'HTTPS', 'TXT', 'SRV', 'LOC', 'MX', 'NS', 'CERT',
                                        'DNSKEY', 'DS', 'NAPTR', 'SMIMEA', 'SSHFP', 'SVCB', 'TLSA', 'URI'],
                      name: str,
                      content: str,
                      ttl: int | None,
                      priority: Optional[int] = None,
                      proxied: bool = False) -> dict:
    """
    Create a DNS record

    Parameters
    ----------
    zone_id : str
        Zone ID
    email : str
        Email of the account
    api_key : str
        API key
    rec_type : Literal['A', 'AAAA', 'CNAME', 'HTTPS', 'TXT', 'SRV', 'LOC', 'MX', 'NS', 'CERT', 'DNSKEY', 'DS', 'NAPTR', 'SMIMEA', 'SSHFP', 'SVCB', 'TLSA', 'URI']
        Record type
    name : str
        Record name
    content : str
        Record content
    ttl : int | None
        TTL
    priority : int | None
        Priority
    proxied : bool
        Whether the record is proxied

    Returns
    -------
    dict
        Response
    """
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records'
    headers = {
        'X-Auth-Email': email,
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    if ttl is None:
        ttl = 1
    else:
        if not (60 <= ttl <= 86400):
            raise ValueError('TTL must be between 60 and 86400')
    data = {
        'type': rec_type,
        'name': name,
        'content': content,
        'ttl': ttl,
        'proxied': proxied
    }
    if priority is not None:
        data['priority'] = priority
    r = requests.post(url, headers=headers, json=data)
    print(r.text)
    return r.json()['result']


def update_dns_record(zone_id: str,
                      email: str,
                      api_key: str,
                      identifier: str,
                      rec_type: Literal['A', 'AAAA', 'CNAME', 'HTTPS', 'TXT', 'SRV', 'LOC', 'MX', 'NS', 'CERT',
                                        'DNSKEY', 'DS', 'NAPTR', 'SMIMEA', 'SSHFP', 'SVCB', 'TLSA', 'URI'],
                      name: str,
                      content: str,
                      ttl: int | None,
                      proxied: bool = False) -> dict:
    """
    Update a DNS record

    Parameters
    ----------
    zone_id : str
        Zone ID
    email : str
        Email of the account
    api_key : str
        API key
    identifier : str
        Record identifier
    rec_type : Literal['A', 'AAAA', 'CNAME', 'HTTPS', 'TXT', 'SRV', 'LOC', 'MX', 'NS', 'CERT', 'DNSKEY', 'DS', 'NAPTR', 'SMIMEA', 'SSHFP', 'SVCB', 'TLSA', 'URI']
        Record type
    name : str
        Record name
    content : str
        Record content
    ttl : int | None
        TTL
    proxied : bool
        Whether the record is proxied

    Returns
    -------
    dict
        Response
    """
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{identifier}'
    headers = {
        'X-Auth-Email': email,
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    if ttl is None:
        ttl = 1
    else:
        if not (60 <= ttl <= 86400):
            raise ValueError('TTL must be between 60 and 86400')
    data = {
        'type': rec_type,
        'name': name,
        'content': content,
        'ttl': ttl,
        'proxied': proxied
    }
    r = requests.put(url, headers=headers, json=data)
    print(r.text)
    return r.json()['result']


def delete_dns_record(zone_id: str, email: str, api_key: str, identifier: str) -> dict:
    """
    Delete a DNS record

    Parameters
    ----------
    zone_id : str
        Zone ID
    email : str
        Email of the account
    api_key : str
        API key
    identifier : str
        Record identifier

    Returns
    -------
    dict
        Response
    """
    url = f'https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{identifier}'
    headers = {
        'X-Auth-Email': email,
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    r = requests.delete(url, headers=headers)
    print(r.text)
    return r.json()['result']
