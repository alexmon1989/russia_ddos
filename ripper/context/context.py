import os
import time
from rich.console import Console

from ripper import common
from ripper.constants import *
from ripper.proxy_manager import ProxyManager
from ripper.socket_manager import SocketManager
from ripper.headers_provider import HeadersProvider
from ripper.stats.context_stats_manager import ContextStatsManager
from ripper.time_interval_manager import TimeIntervalManager
from ripper.errors import *
from ripper.errors_manager import ErrorsManager
from ripper.stats.ip_info import IpInfo
from ripper.context.target import Target


class Context(metaclass=common.Singleton):
    """Class (Singleton) for passing a context to a parallel processes."""

    targets: list[Target] = None

    # ==== Input params ====
    threads_count: int
    """The number of threads."""
    max_random_packet_len: int
    """Limit for Random Packet Length."""
    random_packet_len: bool
    """Is Random Packet Length enabled."""
    proxy_list: str
    """File with proxies in ip:port:username:password or ip:port line format."""
    proxy_type: str
    """Type of proxy to work with. Supported types: socks5, socks4, http."""
    dry_run: bool = False
    """Is dry run mode."""

    # ==== Statistics ====
    myIpInfo: IpInfo = None
    """All the info about IP addresses and GeoIP information."""

    # ==========================================================================
    cpu_count: int
    """vCPU cont of current machine."""

    # ==== Internal variables ====
    headers_provider: HeadersProvider = None
    """HTTP Headers used to make Requests."""

    # External API and services info
    sock_manager: SocketManager = None
    proxy_manager: ProxyManager = None
    errors_manager: ErrorsManager = None
    interval_manager: TimeIntervalManager = None
    logger: Console = None
    stats: ContextStatsManager = None

    is_health_check: bool
    """Controls health check availability. Turn on: 1, turn off: 0."""

    @staticmethod
    def _getattr(obj, name: str, default):
        value = getattr(obj, name, default)

        return value if value is not None else default

    def validate(self):
        """Validates context before Run script. Order is matter!"""
        try:
            for target in self.targets:
                target.validate()
        except Exception as e:
            self.logger.log(str(e))
            exit(1)

        if self.myIpInfo.my_start_ip is None or not common.is_ipv4(self.myIpInfo.my_start_ip):
            self.logger.log(f'Cannot get your public IPv4 address. Check your VPN connection.')
            exit(1)
    
    def add_target(self, target):
        self.targets.append(target)
        # NOTE We will merge error on visualization step
        # self.errors_manager.add_submanager(target.errors_manager)

    def __init__(self, args):
        self.targets = []
        self.myIpInfo = IpInfo()
        self.headers_provider = HeadersProvider()
        self.sock_manager = SocketManager()
        self.proxy_manager = ProxyManager()
        self.errors_manager = ErrorsManager()
        self.interval_manager = TimeIntervalManager()
        self.logger = Console(width=MIN_SCREEN_WIDTH)

        self.threads_count = getattr(args, 'threads_count', ARGS_DEFAULT_THREADS_COUNT)
        self.random_packet_len = bool(getattr(args, 'random_packet_len', ARGS_DEFAULT_RND_PACKET_LEN))
        self.max_random_packet_len = int(getattr(args, 'max_random_packet_len', ARGS_DEFAULT_MAX_RND_PACKET_LEN))
        self.is_health_check = bool(getattr(args, 'health_check', ARGS_DEFAULT_HEALTH_CHECK))
        self.dry_run = getattr(args, 'dry_run', False)

        self.sock_manager.socket_timeout = self._getattr(args, 'socket_timeout', ARGS_DEFAULT_SOCK_TIMEOUT)
        self.proxy_type = getattr(args, 'proxy_type', ARGS_DEFAULT_PROXY_TYPE)
        self.proxy_list = getattr(args, 'proxy_list', None)

        self.cpu_count = max(os.cpu_count(), 1)  # to avoid situation when vCPU might be 0

        # Get initial info from external services
        self.myIpInfo.my_start_ip = common.get_current_ip()
        self.myIpInfo.my_current_ip = self.myIpInfo.my_start_ip
        self.myIpInfo.my_country = common.get_country_by_ipv4(self.myIpInfo.my_start_ip)

        if getattr(args, 'attack_method', None) == 'http-flood':
            self.random_packet_len = False
            self.max_random_packet_len = 0
        elif self.random_packet_len and not self.max_random_packet_len:
            self.max_random_packet_len = 1024

        self.connections_check_time = time.time_ns()

        if self.proxy_list and getattr(args, 'attack_method', None) != 'udp-flood':
            self.proxy_manager.set_proxy_type(self.proxy_type)
            try:
                self.proxy_manager.update_proxy_list_from_file(self.proxy_list)
            except Exception as e:
                self.errors_manager.add_error(ProxyListReadOperationFailedError(message=e))

        # Proxies are slower, so wee needs to increase timeouts 2x times
        if self.proxy_manager.proxy_list_initial_len:
            self.sock_manager.socket_timeout *= 2
        
        if args and getattr(args, 'targets', None):
            for target_uri in getattr(args, 'targets', []):
                target = Target(
                    target_uri = target_uri,
                    attack_method = getattr(args, 'attack_method', None),
                    # TODO move http_method to target_uri to allow each target have its own method
                    http_method = getattr(args, 'http_method', ARGS_DEFAULT_HTTP_ATTACK_METHOD).upper(),
                )
                self.add_target(target)

        self.stats = ContextStatsManager(_ctx=self)
        # We can't have less threads than targets
        self.threads_count = max(self.threads_count, len(self.targets))
