import os
import time
from datetime import datetime
from collections import defaultdict
from rich.console import Console

from ripper import common
from ripper.constants import *
from ripper.proxy_manager import ProxyManager
from ripper.socket_manager import SocketManager
from ripper.headers_provider import HeadersProvider
from ripper.context.errors import *
from ripper.context.stats import *
from ripper.context.target import *


# TODO Make it true singleton
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
    proxy_list: str
    """File with proxies in ip:port:username:password or ip:port line format."""
    proxy_type: str
    """Type of proxy to work with. Supported types: socks5, socks4, http."""
    dry_run: bool = False
    """Is dry run mode."""

    # ==== Statistic ====
    myIpInfo: IpInfo = IpInfo()
    """All the info about IP addresses and GeoIP information."""
    errors: dict[str, Errors] = defaultdict(dict[str, Errors])
    """All the errors during script run."""

    # ==========================================================================
    cpu_count: int
    """vCPU cont of current machine."""

    # ==== Internal variables ====
    headers_provider: HeadersProvider = HeadersProvider()
    """HTTP Headers used to make Requests."""

    # External API and services info
    sock_manager: SocketManager = SocketManager()
    proxy_manager: ProxyManager = ProxyManager()
    logger: Console = Console(width=MIN_SCREEN_WIDTH)

    # Health-check
    is_health_check: bool
    """Controls health check availability. Turn on: 1, turn off: 0."""

    _timer_bucket: dict[str, datetime] = defaultdict(dict[str, datetime])
    """Internal stopwatch."""

    @staticmethod
    def _getattr(obj, name: str, default):
        value = getattr(obj, name, default)

        return value if value is not None else default

    def check_timer(self, sec: int, bucket: str = None) -> bool:
        """
        Check if time in seconds elapsed from last check.
        :param sec: Amount of seconds which needs to check.
        :param bucket: Bucket name to track specific timer.
        :return: True if specified seconds elapsed, False - if not elapsed.
        """
        stopwatch = '__stopwatch__' if bucket is None else bucket

        if not self._timer_bucket[stopwatch]:
            self._timer_bucket[stopwatch] = self.target.statistic.start_time
        delta = (datetime.now() - self._timer_bucket[stopwatch]).total_seconds()
        if int(delta) < sec:
            return False
        else:
            self._timer_bucket[stopwatch] = datetime.now()
            return True

    def get_timer_seconds(self, bucket: str = None) -> int:
         stopwatch = '__stopwatch__' if bucket is None else bucket

         if self._timer_bucket[stopwatch]:
             return int((datetime.now() - self._timer_bucket[bucket]).total_seconds())

         return 0

    def get_start_time_ns(self) -> int:
        """Get start time in nanoseconds."""
        if not self.target.statistic.start_time:
            return 0
        return int(self.target.statistic.start_time.timestamp() * 1000000 * 1000)

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

        if self.myIpInfo.my_start_ip is None or not common.is_ipv4(self.myIpInfo.my_start_ip):
            self.logger.log(f'Cannot get your public IPv4 address. Check your VPN connection.')
            exit(1)

    # TODO use Singleton meta class
    def __new__(cls, args):
        """Singleton realization."""
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self, args):
        if args and getattr(args, 'target'):
            self.target = Target(
                target_uri = getattr(args, 'target', ''),
                attack_method = getattr(args, 'attack_method', None),
                http_method = getattr(args, 'http_method', ARGS_DEFAULT_HTTP_ATTACK_METHOD).upper(),
            )

        self.threads = getattr(args, 'threads', ARGS_DEFAULT_THREADS)
        self.random_packet_len = bool(getattr(args, 'random_packet_len', ARGS_DEFAULT_RND_PACKET_LEN))
        self.max_random_packet_len = int(getattr(args, 'max_random_packet_len', ARGS_DEFAULT_MAX_RND_PACKET_LEN))
        self.is_health_check = bool(getattr(args, 'health_check', ARGS_DEFAULT_HEALTH_CHECK))
        self.dry_run = getattr(args, 'dry_run', False)

        self.sock_manager.socket_timeout = self._getattr(args, 'socket_timeout', ARGS_DEFAULT_SOCK_TIMEOUT)
        self.proxy_type = getattr(args, 'proxy_type', ARGS_DEFAULT_PROXY_TYPE)
        self.proxy_list = getattr(args, 'proxy_list', None)

        if self.target.attack_method == 'http-flood':
            self.random_packet_len = False
            self.max_random_packet_len = 0
        elif self.random_packet_len and not self.max_random_packet_len:
            self.max_random_packet_len = 1024

        self.cpu_count = max(os.cpu_count(), 1)  # to avoid situation when vCPU might be 0

        # Get initial info from external services
        self.myIpInfo.my_start_ip = common.get_current_ip()
        self.myIpInfo.my_current_ip = self.myIpInfo.my_start_ip
        self.myIpInfo.my_country = common.get_country_by_ipv4(self.myIpInfo.my_start_ip)

        self.target.statistic.start_time = datetime.now()
        self.connections_check_time = time.time_ns()

        if self.proxy_list and self.target.attack_method != 'udp-flood':
            self.proxy_manager.set_proxy_type(self.proxy_type)
            try:
                self.proxy_manager.update_proxy_list_from_file(self.proxy_list)
            except Exception as e:
                self.add_error(Errors('Proxy list read operation failed', e))

        # Proxies are slower, so wee needs to increase timeouts 2x times
        if self.proxy_manager.proxy_list_initial_len:
            self.sock_manager.socket_timeout *= 2
