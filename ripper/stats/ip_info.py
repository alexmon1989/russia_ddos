from ripper.constants import DEFAULT_CURRENT_IP_VALUE
from ripper.common import get_country_by_ipv4


class IpInfo:
    """All the info about IP addresses and Geo info."""
    country: str = None
    """Country code based on your public IPv4 address."""
    start_ip: str = None
    """My IPv4 address within script starting."""
    current_ip: str = None
    """My current IPv4 address. It can be changed during script run."""

    def __init__(self, ip: str):
        self.start_ip = ip
        self.current_ip = self.start_ip
        self.country = get_country_by_ipv4(self.start_ip)

    @property
    def ip_masked(self) -> str:
        """
        Get my initial IPv4 address with masked octets.

        127.0.0.1 -> 127.***.***.***
        """
        parts = self.start_ip.split('.')
        if not parts[0].isdigit():
            return DEFAULT_CURRENT_IP_VALUE

        if len(parts) > 1 and parts[0].isdigit():
            return f'{parts[0]}.***.***.***'
        else:
            return parts[0]

    # TODO make property
    def is_ip_changed(self) -> bool:
        """:return: True is start ip doesn't equal to current ip"""
        return self.start_ip != self.current_ip
