import time
from typing import Tuple
from urllib.parse import urlparse

from ripper.headers_provider import HeadersProvider
from ripper.health_check_manager import HealthCheckManager, HealthStatus
from ripper import common
from ripper.constants import *
from ripper.stats.target_stats_manager import TargetStatsManager
from ripper.context.events_journal import EventsJournal
from ripper.time_interval_manager import TimeIntervalManager

Attack = 'Attack'
events_journal = EventsJournal()


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
    attack_method: str
    """Current attack method."""
    http_method: str
    """HTTP method used in HTTP packets"""
    
    attack_threads: list[Attack] = None
    """Attack-related threads."""
    
    health_check_manager: HealthCheckManager = None
    interval_manager: TimeIntervalManager = None

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

    def __init__(self, target_uri: str, attack_method: str = None, http_method: str = ARGS_DEFAULT_HTTP_ATTACK_METHOD):
        self.attack_threads = []
        self.http_method = http_method
        headers_provider = HeadersProvider()
        self.interval_manager = TimeIntervalManager()

        parts = urlparse(target_uri)
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

        self.attack_method = attack_method if attack_method else self.guess_attack_method()

        self.health_check_manager = HealthCheckManager(target=self)
        self.stats = TargetStatsManager(target=self)

    def add_attack_thread(self, attack: Attack):
        self.attack_threads.append(attack)

    def hostip_port_tuple(self) -> Tuple[str, int]:
        return (self.host_ip, self.port)

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
    def url(self) -> str:
        """Get fully qualified URI for target HOST - schema://host:port"""
        http_protocol = 'https://' if self.port == 443 else 'http://'

        return f"{http_protocol}{self.host}:{self.port}{self.http_path}"

    def stop_attack_threads(self):
        for attack in self.attack_threads:
            attack.stop()

    ###############################################
    # Connection validators
    ###############################################
    def validate_attack(self) -> bool:
        """
        Checks if attack is valid.
        Attack is valid if target accepted traffic within
        last SUCCESSFUL_CONNECTIONS_CHECK_PERIOD seconds (about 3 minutes)
        :return: True if valid.
        """
        if self.health_check_manager.status == HealthStatus.dead:
            return False
        if self.attack_method == 'tcp':
            return self.check_successful_tcp_attack()
        return self.check_successful_connections()

    def check_successful_connections(self) -> bool:
        """
        Checks if there are no successful connections more than SUCCESSFUL_CONNECTIONS_CHECK_PERIOD sec.
        Returns True if there was successful connection for last NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC sec.
        """
        now_ns = time.time_ns()
        lower_bound = max(self.interval_manager.get_start_time_ns(),
                        self.stats.connect.last_check_time)
        diff_sec = common.ns2s(now_ns - lower_bound)

        if self.stats.connect.success == self.stats.connect.success_prev:
            if diff_sec > SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC:
                events_journal.error(NO_SUCCESSFUL_CONNECTIONS_ERR_MSG, target=self)
                return diff_sec <= NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC
        else:
            self.stats.connect.last_check_time = now_ns
            self.stats.connect.sync_success()

        return True

    def check_successful_tcp_attack(self) -> bool:
        """
        Checks if there are changes in sent bytes count.
        Returns True if there was successful connection for last NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC sec.
        """
        now_ns = time.time_ns()
        lower_bound = max(self.interval_manager.get_start_time_ns(),
                        self.stats.packets.connections_check_time)
        diff_sec = common.ns2s(now_ns - lower_bound)

        if self.stats.packets.total_sent == self.stats.packets.total_sent:
            if diff_sec > SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC:
                events_journal.error(NO_SUCCESSFUL_CONNECTIONS_ERR_MSG, target=self)

                return diff_sec <= NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC
        else:
            self.stats.packets.connections_check_time = now_ns

        return True
