import os
import time
from datetime import datetime
from collections import defaultdict
from xmlrpc.client import Boolean
from rich.console import Console

from ripper import common
from ripper.constants import *
from ripper.proxy_manager import ProxyManager
from ripper.socket_manager import SocketManager
from ripper.headers_provider import HeadersProvider
from ripper.context.errors import *
from ripper.context.stats import *
from ripper.context.target import *
from ripper.actions.attack import attack_method_factory

class Context:
    """Class (Singleton) for passing a context to a parallel processes."""

    target: Target = None

    # ==== Input params ====
    threads: int
    """The number of threads."""
    max_random_packet_len: int
    """Limit for Random Packet Length."""
    random_packet_len: bool
    """Is Random Packet Length enabled."""
    attack_method: str
    """Current attack method."""
    proxy_list: str
    """File with proxies in ip:port:username:password or ip:port line format."""
    proxy_type: str
    """Type of proxy to work with. Supported types: socks5, socks4, http."""
    http_method: str
    """HTTP method used in HTTP packets"""

    # ==== Statistic ====
    Statistic: Statistic = Statistic()
    """All the statistics collected separately by protocols and operations."""
    IpInfo: IpInfo = IpInfo()
    """All the info about IP addresses and GeoIP information."""
    errors: dict[str, Errors] = defaultdict(dict[str, Errors])
    """All the errors during script run."""

    # ==========================================================================

    cpu_count: int
    """vCPU cont of current machine."""

    # ==== Internal variables ====
    headers: HeadersProvider = None
    """HTTP Headers used to make Requests."""

    # External API and services info
    sock_manager: SocketManager = SocketManager()
    proxy_manager: ProxyManager = ProxyManager()
    logger: Console = Console(width=MIN_SCREEN_WIDTH)

    # Health-check
    is_health_check: bool
    """Controls health check availability. Turn on: 1, turn off: 0."""
    connections_check_time: int
    fetching_host_statuses_in_progress: bool = False
    last_host_statuses_update: datetime = None
    health_check_method: str
    host_statuses = {}

    _stopwatch: datetime = None
    """Internal stopwatch."""

    @staticmethod
    def _getattr(obj, name: str, default):
        value = getattr(obj, name, default)

        return value if value is not None else default

    def check_timer(self, sec: int) -> bool:
        """
        Check if time in seconds elapsed from last check.
        :param sec: Amount of seconds which needs to check
        :return: True if specified seconds elapsed, False - if not elapsed
        """
        if not self._stopwatch:
            self._stopwatch = self.Statistic.start_time
        delta = (datetime.now() - self._stopwatch).total_seconds()
        if int(delta) < sec:
            return False
        else:
            self._stopwatch = datetime.now()
            return True

    def get_start_time_ns(self) -> int:
        """Get start time in nanoseconds."""
        if not self.Statistic.start_time:
            return 0
        return int(self.Statistic.start_time.timestamp() * 1000000 * 1000)

    def add_error(self, error: Errors):
        """
        Add Error to Errors collection without duplication.
        If Error exists in collection - it updates the error counter.
        """
        if self.errors.__contains__(error.uuid):
            self.errors[error.uuid].count += 1
            self.errors[error.uuid].time = error.time
        else:
            self.errors[error.uuid] = error

    def remove_error(self, error_code: str):
        """Remove Error from collection by Error Code."""
        if self.errors.__contains__(error_code):
            self.errors.__delitem__(error_code)

    def has_errors(self) -> bool:
        """Check if Errors are exists."""
        return len(self.errors) > 0

    def validate(self):
        """Validates context before Run script. Order is matter!"""
        try:
            self.target.validate()
        except Exception as e:
            self.logger.log(str(e))
            exit(1)

        if self.IpInfo.my_start_ip is None or not common.is_ipv4(self.IpInfo.my_start_ip):
            self.logger.log(f'Cannot get your public IPv4 address. Check your VPN connection.')
            exit(1)

    def __new__(cls, args):
        """Singleton realization."""
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def get_attack_method_from_args(self, args):
        args_attack_method = getattr(args, 'attack_method', '')
        if args and args_attack_method:
            return args_attack_method
        if self.target:
            if self.target.scheme == 'http':
                return 'http-flood'
            elif self.target.scheme == 'tcp':
                return 'tcp-flood'
            elif self.target.scheme == 'udp':
                return 'udp-flood'
        return None
        
    def __init__(self, args):
        # self.host = getattr(args, 'host', '')
        # self.port = getattr(args, 'port', ARGS_DEFAULT_PORT)
        # self.http_path = getattr(args, 'http_path', ARGS_DEFAULT_HTTP_REQUEST_PATH)
        if args and getattr(args, 'target'):
            self.target = Target(getattr(args, 'target', ''))
        # if args and 
        # self.attack_method = getattr(args, 'attack_method', ARGS_DEFAULT_ATTACK_METHOD).lower()
        self.attack_method = self.get_attack_method_from_args(args)
        self.http_method = getattr(args, 'http_method', ARGS_DEFAULT_HTTP_ATTACK_METHOD).upper()

        self.threads = getattr(args, 'threads', ARGS_DEFAULT_THREADS)
        self.random_packet_len = bool(getattr(args, 'random_packet_len', ARGS_DEFAULT_RND_PACKET_LEN))
        self.max_random_packet_len = int(getattr(args, 'max_random_packet_len', ARGS_DEFAULT_MAX_RND_PACKET_LEN))
        self.is_health_check = bool(getattr(args, 'health_check', ARGS_DEFAULT_HEALTH_CHECK))

        self.sock_manager.socket_timeout = self._getattr(args, 'socket_timeout', ARGS_DEFAULT_SOCK_TIMEOUT)
        self.proxy_type = getattr(args, 'proxy_type', ARGS_DEFAULT_PROXY_TYPE)
        self.proxy_list = getattr(args, 'proxy_list', None)

        if self.attack_method == 'http':
            self.random_packet_len = False
            self.max_random_packet_len = 0
        elif self.random_packet_len and not self.max_random_packet_len:
            self.max_random_packet_len = 1024

        self.cpu_count = max(os.cpu_count(), 1)  # to avoid situation when vCPU might be 0

        self.headers_provider = HeadersProvider()

        # Get initial info from external services
        self.IpInfo.my_start_ip = common.get_current_ip()
        self.IpInfo.my_current_ip = self.IpInfo.my_start_ip
        self.IpInfo.my_country = common.get_country_by_ipv4(self.IpInfo.my_start_ip)

        self.Statistic.start_time = datetime.now()
        self.connections_check_time = time.time_ns()
        self.health_check_method = 'ping' if self.attack_method == 'udp' else self.attack_method

        if self.proxy_list and self.attack_method != 'udp':
            self.proxy_manager.set_proxy_type(self.proxy_type)
            try:
                self.proxy_manager.update_proxy_list_from_file(self.proxy_list)
            except Exception as e:
                self.add_error(Errors('Proxy list read operation failed', e))

        # proxies are slower, so wee needs to increase timeouts 2x times
        if self.proxy_manager.proxy_list_initial_len:
            self.sock_manager.socket_timeout *= 2
