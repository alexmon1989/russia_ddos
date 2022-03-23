from typing import Tuple
from urllib.parse import urlparse

from ripper.headers_provider import HeadersProvider
from ripper import common


def default_scheme_port(scheme: str):
    scheme_lc = scheme.lower()
    if scheme_lc == 'http' or scheme_lc == 'tcp':
        return 80
    if scheme_lc == 'https':
        return 443
    if scheme_lc == 'udp':
        return 53
    return None


class Target:
    scheme: str
    """Connection scheme"""
    host: str
    """Original HOST name from input args. Can be domain name or IP address."""
    host_ip: str
    """HOST IPv4 address."""
    port: int
    """Destination Port."""
    country: str = None
    """Country code based on target public IPv4 address."""
    is_cloud_flare_protection: bool = False
    """Is Host protected by CloudFlare."""

    @staticmethod
    def validate_format(target_url: str) -> bool:
        try:
            result = urlparse(target_url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def __init__(self, target_str: str):
        headers_provider = HeadersProvider()

        parts = urlparse(target_str)
        self.scheme = parts.scheme
        # TODO rename host to hostname
        self.host = parts.hostname
        self.port = parts.port if parts.port is not None else default_scheme_port(parts.scheme)
        path = parts.path if parts.path else '/'
        query = parts.query if parts.query else ''
        self.http_path = path if not query else f'{path}?{query}'

        self.host_ip = common.get_ipv4(self.host)
        self.country = common.get_country_by_ipv4(self.host_ip)
        self.is_cloud_flare_protection = common.check_cloud_flare_protection(self.host, headers_provider.user_agents)

    def hostip_port_tuple(self) -> Tuple[str, int]:
        return (self.host_ip, self.port)

    def validate(self):
        """Validates target"""
        if self.host_ip is None or not common.is_ipv4(self.host_ip):
            raise Exception(f'Cannot get IPv4 for HOST: {self.host}. Could not connect to the target HOST.')
        return True

    def cloudflare_status(self) -> str:
        """Get human-readable status for CloudFlare target HOST protection."""
        return 'Protected' if self.is_cloud_flare_protection else 'Not protected'

    def url(self) -> str:
        """Get fully qualified URI for target HOST - schema://host:port"""
        http_protocol = 'https://' if self.port == 443 else 'http://'

        return f"{http_protocol}{self.host}:{self.port}{self.http_path}"
