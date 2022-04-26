import time
from typing import Tuple
from urllib.parse import urlparse

from ripper.health_check_manager import HealthCheckManager
from ripper import common
from ripper.constants import *
from ripper.stats.target_stats_manager import TargetStatsManager
from ripper.time_interval_manager import TimeIntervalManager

Attack = 'Attack'


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
    index: int = 0
    """Target index for statistic."""

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
    attack_method: str
    """Current attack method."""
    http_method: str
    """HTTP method used in HTTP packets"""

    min_random_packet_len: int
    """Minimum size for random packet length."""
    max_random_packet_len: int
    """Limit for random packet length."""

    attack_threads: list[Attack] = None
    """Attack-related threads."""

    health_check_manager: HealthCheckManager = None
    time_interval_manager: TimeIntervalManager = None

    stats: TargetStatsManager = None
    """All the statistics collected separately by protocols and operations."""

    @staticmethod
    def validate_format(target_uri: str) -> bool:
        try:
            result = urlparse(target_uri)
            return all([result.scheme, result.netloc])
        except:
            return False

    def guess_attack_method(self):
        if self.scheme == 'http' or self.scheme == 'https':
            return 'http-flood'
        elif self.scheme == 'tcp':
            return 'tcp-flood'
        elif self.scheme == 'udp':
            return 'udp-flood'
        return None

    def __init__(self, target_uri: str, attack_method: str = None, http_method: str = ARGS_DEFAULT_HTTP_ATTACK_METHOD,
                 min_random_packet_len: int = None, max_random_packet_len: int = None):
        self.attack_threads = []
        self.http_method = http_method
        self.time_interval_manager = TimeIntervalManager()

        self.host_ip = DEFAULT_CURRENT_IP_VALUE
        self.country = GEOIP_NOT_DEFINED

        parts = urlparse(target_uri)
        self.scheme = parts.scheme
        # TODO rename host to hostname
        self.host = parts.hostname
        self.port = parts.port if parts.port is not None else default_scheme_port(parts.scheme)
        path = parts.path if parts.path else '/'
        query = parts.query if parts.query else ''
        self.http_path = path if not query else f'{path}?{query}'
        self.attack_method = attack_method if attack_method else self.guess_attack_method()

        self.health_check_manager = HealthCheckManager(target=self)
        self.stats = TargetStatsManager(target=self)

        if self.attack_method in ['http-flood', 'http-bypass']:
            self.min_random_packet_len = 0 if min_random_packet_len is None else min_random_packet_len
            self.max_random_packet_len = 0 if max_random_packet_len is None else max_random_packet_len
        else:
            self.min_random_packet_len = DEFAULT_MIN_RND_PACKET_LEN if min_random_packet_len is None else min_random_packet_len
            self.max_random_packet_len = DEFAULT_MAX_RND_PACKET_LEN if max_random_packet_len is None else max_random_packet_len
        self.min_random_packet_len = max(self.min_random_packet_len, 0)
        self.max_random_packet_len = max(self.max_random_packet_len, self.min_random_packet_len)

    def init(self):
        """Initialize target: get IPv4, country code and make initial checks."""
        self.host_ip = common.get_ipv4(self.host)
        self.country = common.get_country_by_ipv4(self.host_ip)
        self.is_cloud_flare_protection = common.detect_cloudflare(self.uri)

    def add_attack_thread(self, attack: Attack):
        self.attack_threads.append(attack)

    def hostip_port_tuple(self) -> Tuple[str, int]:
        return self.host_ip, self.port

    def validate(self):
        """Validates target."""
        if self.host_ip is None or not common.is_ipv4(self.host_ip):
            raise Exception(f'Cannot get IPv4 for HOST: {self.host}. Could not connect to the target HOST.')
        # XXX Should we call validate attack here as well?
        return True

    def cloudflare_status(self) -> str:
        """Get human-readable status for CloudFlare target HOST protection."""
        return 'Protected' if self.is_cloud_flare_protection else 'Not protected'

    @property
    def http_url(self) -> str:
        """Get fully qualified HTTP URL for target HOST - http(s)://host:port/path"""
        http_protocol = 'https://' if self.port == 443 else 'http://'

        return f"{http_protocol}{self.host}:{self.port}{self.http_path}"

    @property
    def uri(self) -> str:
        """Get fully qualified URI for target HOST - schema://host:port"""

        return f"{self.scheme}://{self.host}:{self.port}{self.http_path}"

    def stop_attack_threads(self):
        for attack in self.attack_threads:
            attack.stop()

    ###############################################
    # Connection validators
    ###############################################
    def validate_connection(self, period_sec: int = SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC) -> bool:
        """
        Check if there was successful connection for last time with interval of `period_sec`.
        Args:
            period_sec: Time interval in seconds to check for successful connection.
        """
        period_ns = period_sec * 1000000 * 1000
        return self.stats.packets.connections_check_time + period_ns > time.time_ns()
