from ripper.constants import DEFAULT_CURRENT_IP_VALUE


class IpInfo:
    """All the info about IP addresses and Geo info."""
    my_country: str = None
    """Country code based on your public IPv4 address."""
    my_start_ip: str = None
    """My IPv4 address within script starting."""
    my_current_ip: str = None
    """My current IPv4 address. It can be changed during script run."""

    def my_ip_masked(self) -> str:
        """
        Get my initial IPv4 address with masked octets.

        127.0.0.1 -> 127.*.*.*
        """
        parts = self.my_start_ip.split('.')
        if not parts[0].isdigit():
            return DEFAULT_CURRENT_IP_VALUE

        if len(parts) > 1 and parts[0].isdigit():
            return f'{parts[0]}.*.*.*'
        else:
            return parts[0]
