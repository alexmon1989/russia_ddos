import os
import time
from rich.console import Console

from _version import __version__

import ripper.common
from ripper.github_updates_checker import Version
from ripper.constants import *
from ripper.proxy_manager import ProxyManager
from ripper.socket_manager import SocketManager
from ripper.stats.context_stats_manager import ContextStatsManager
from ripper.stats.ip_info import IpInfo
from ripper.context.events_journal import EventsJournal
from ripper.targets_manager import TargetsManager
from ripper.headers_provider import HeadersProvider
from ripper.time_interval_manager import TimeIntervalManager
from ripper.duration_manager import DurationManager
from ripper.context.target import Target

events_journal = EventsJournal()


class Context:
    """Class (Singleton) for passing a context to a parallel processes."""

    targets_manager: TargetsManager = None

    # ==== Input params ====
    proxy_list: str
    """File with proxies in ip:port:username:password or ip:port line format."""
    proxy_type: str
    """Type of proxy to work with. Supported types: socks5, socks4, http."""
    dry_run: bool = False
    """Is dry run mode."""

    # ==== Statistics ====
    latest_version: Version = None
    current_version: Version = None
    my_ip_info: IpInfo = None
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
    time_interval_manager: TimeIntervalManager = None
    duration_manager: DurationManager = None
    logger: Console = None
    stats: ContextStatsManager = None

    is_health_check: bool
    """Controls health check availability. Turn on: 1, turn off: 0."""

    is_verbose: bool = True
    """Do not print messages to stdout"""

    @staticmethod
    def _getattr(obj, name: str, default):
        value = getattr(obj, name, default)

        return value if value is not None else default

    def __init__(self, args):
        self.current_version = Version(__version__)
        attack_method = getattr(args, 'attack_method', None)
        self.is_verbose = getattr(args, 'verbose', True)
        self.logger = Console(width=MIN_SCREEN_WIDTH, quiet=not self.is_verbose)

        self.targets_manager = TargetsManager(_ctx=self)

        self.logger.log('Getting your current Public IPv4 address...')
        self.my_ip_info = IpInfo(ripper.common.get_current_ip())
        self.logger.log(f'Your start Public IPv4 is: {self.my_ip_info.ip_masked}')

        self.headers_provider = HeadersProvider()
        self.sock_manager = SocketManager()
        self.proxy_manager = ProxyManager()
        self.time_interval_manager = TimeIntervalManager()
        self.time_interval_manager.reset_start_time()
        self.is_health_check = bool(getattr(args, 'health_check', ARGS_DEFAULT_HEALTH_CHECK))
        self.dry_run = getattr(args, 'dry_run', False)
        self.sock_manager.socket_timeout = self._getattr(args, 'socket_timeout', ARGS_DEFAULT_SOCK_TIMEOUT)
        self.proxy_type = getattr(args, 'proxy_type', ARGS_DEFAULT_PROXY_TYPE)
        self.proxy_list = getattr(args, 'proxy_list', None)

        # to avoid situation when vCPU might be 0
        self.cpu_count = max(os.cpu_count(), 1)

        self.connections_check_time = time.time_ns()

        if self.proxy_list and attack_method != 'udp-flood':
            self.proxy_manager.set_proxy_type(self.proxy_type)
            try:
                self.proxy_manager.update_proxy_list_from_file(self.proxy_list)
            except Exception as e:
                events_journal.exception(e)
                events_journal.error('Proxy list read operation failed.')

        # Proxies are slower, so wee needs to increase timeouts 2x times
        if self.proxy_manager.proxy_list_initial_len:
            self.sock_manager.socket_timeout *= 2

        if args and getattr(args, 'targets_list', None):
            targets_file: str = getattr(args, 'targets_list', None)
            message = f'Downloading targets from {targets_file}...' if targets_file.startswith('http') else 'Reading targets from file...'
            self.logger.log(message)
            input_targets = ripper.common.read_file_lines(targets_file)
            self.logger.log(f'Loaded list with {len(input_targets)} targets')
        else:
            #  args and getattr(args, 'targets', None):
            input_targets = getattr(args, 'targets', [])

        _http_method = getattr(args, 'http_method', ARGS_DEFAULT_HTTP_ATTACK_METHOD).upper()
        _min_random_packet_len = getattr(args, 'min_random_packet_len', None)
        _max_random_packet_len = getattr(args, 'max_random_packet_len', None)
        for target_uri in input_targets:
            if target_uri.__contains__('#') or not target_uri.__contains__('://'):
                continue
            with self.logger.status('Configure attacks...') as status:
                status.update(f'   Configuring attack for [cyan]{target_uri}[/]', spinner='aesthetic')
                target = Target(
                    target_uri=target_uri,
                    attack_method=attack_method,
                    # TODO move http_method to target_uri to allow each target have its own method
                    http_method=_http_method,
                    min_random_packet_len=_min_random_packet_len,
                    max_random_packet_len=_max_random_packet_len,
                )
                self.targets_manager.add_target(target)

        arg_threads_count = getattr(args, 'threads_count', ARGS_DEFAULT_THREADS_COUNT)
        if arg_threads_count == 'auto':
            self.targets_manager.set_auto_threads_distribution()
        else:
            threads_count = int(arg_threads_count) if not self.dry_run else 1
            self.targets_manager.set_threads_count(threads_count)

        self.stats = ContextStatsManager(_ctx=self)
        self.duration_manager = DurationManager(
            duration_seconds=getattr(args, 'duration', None),
            _ctx=self,
        )

    def validate(self):
        """Validates context before Run script. Order is matter!"""
        if self.targets_manager.targets_count() < 1:
            self.logger.log(NO_MORE_TARGETS_LEFT_ERR_MSG)
            return False

        # try:
        #     for target in self.targets_manager.targets:
        #         target.validate()
        # except Exception as e:
        #     self.logger.log(str(e))
        #     exit(1)

        if self.my_ip_info.start_ip is None or not ripper.common.is_ipv4(self.my_ip_info.start_ip):
            self.logger.log(
                'Cannot get your public IPv4 address. Check your VPN connection.')
            return False
        
        return True
