import os
import time

from datetime import datetime
from collections import defaultdict
from enum import Enum

from ripper import common
from ripper.common import is_ipv4
from ripper.constants import DEFAULT_CURRENT_IP_VALUE
from ripper.sockets import SocketManager
from ripper.proxy import read_proxy_list


def get_headers_dict(base_headers: list[str]):
    """Set headers for the request"""
    headers_dict = {}
    for line in base_headers:
        parts = line.split(':')
        headers_dict[parts[0]] = parts[1].strip()

    return headers_dict


class PacketsStats:
    """Class for TCP/UDP statistic collection."""
    total_sent: int = 0
    """Total packets sent by TCP/UDP."""
    total_sent_prev: int = 0
    """Total packets sent by TCP/UDP (previous state)"""
    total_sent_bytes: int = 0
    """Total sent bytes by TCP/UDP connect."""
    connections_check_time: int = 0
    """Connection last check time."""

    def sync_packets_sent(self):
        """Sync previous packets sent stats with current packets sent stats."""
        self.total_sent_prev = self.total_sent


class ConnectionStats:
    """Class for Connection statistic"""
    success_prev: int = 0
    """Total connections to HOST with Success status (previous state)"""
    success: int = 0
    """Total connections to HOST with Success status"""
    failed: int = 0
    """Total connections to HOST with Failed status."""
    last_check_time: int = 0
    """Last check connection time."""
    in_progress: bool = False
    """Connection state used for checking liveness of Socket."""

    def get_success_rate(self) -> int:
        """Calculate Success Rate for connection."""
        if self.success == 0:
            return 0

        return int(self.success / (self.success + self.failed) * 100)

    def sync_success(self):
        """Sync previous success state with current success state."""
        self.success_prev = self.success

    def set_state_in_progress(self):
        """Set connection State - in progress."""
        self.in_progress = True

    def set_state_is_connected(self):
        """Set connection State - is connected."""
        self.in_progress = False


class Statistic:
    """Collect all statistics."""
    packets: PacketsStats = PacketsStats()
    """Collect all the stats about TCP/UDP and HTTP packets."""
    http_stats = defaultdict(int)
    """Collect stats about HTTP response codes."""
    connect: ConnectionStats = ConnectionStats()
    """Collect all the Connections stats via Socket or HTTP Client."""
    start_time: datetime = None
    """Script start time."""


class IpInfo:
    """All the info about IP addresses and Geo info."""
    my_country: str = None
    """Country code based on your public IPv4 address."""
    target_country: str = None
    """Country code based on target public IPv4 address."""
    my_start_ip: str = None
    """My IPv4 address within script starting."""
    my_current_ip: str = None
    """My current IPv4 address. It can be changed during script run."""
    isCloudflareProtected: bool = False
    """Is Host protected by CloudFlare."""

    def cloudflare_status(self) -> str:
        """Get human-readable status for CloudFlare target HOST protection."""
        return 'Protected' if self.isCloudflareProtected else 'Not protected'

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


class ErrorCodes(Enum):
    CannotGetServerIP = 'CANNOT_GET_SERVER_IP'
    ConnectionError = 'CONNECTION_ERROR'
    HostDoesNotResponse = 'HOST_DOES_NOT_RESPONSE'
    YourIpWasChanged = 'YOUR_IP_WAS_CHANGED'
    CannotSendRequest = 'CANNOT_SEND_REQUEST'


class Errors:
    """Class with Error details."""
    code: str = None
    """Error type."""
    count: int = 0
    """Error count."""
    message: str = ''
    """Error message"""

    def __init__(self, code: str, message: str):
        self.code = code
        self.count = 1
        self.message = message


class Context:
    """Class (Singleton) for passing a context to a parallel processes."""

    # ==== Input params ====
    host: str = ''
    """Original HOST name from input args. Can be domain name or IP address."""
    host_ip: str = ''
    """HOST IPv4 address."""
    port: int = 80
    """Destination Port."""
    threads: int = 100
    """The number of threads."""
    max_random_packet_len: int = 48
    """Limit for Random Packet Length."""
    random_packet_len: bool = False
    """Is Random Packet Length enabled."""
    attack_method: str = None
    """Current attack method."""

    # ==== Statistic ====
    Statistic: Statistic = Statistic()
    """All the statistics collected separately by protocols and operations."""
    IpInfo: IpInfo = IpInfo()
    """All the info about IP addresses and GeoIP information."""
    errors: dict[str, Errors] = defaultdict(dict[str, Errors])
    """All the errors during script run."""

    # ==========================================================================

    cpu_count: int = 1
    """vCPU cont of current machine."""
    protocol: str = 'http://'
    """HTTP protocol. Can be http/https."""

    # ==== Internal variables ====
    user_agents: list = None
    """User-Agent list. RAW data for random choice."""
    base_headers: list = None
    """Base HTTP headers list for HTTP Client. RAW data for internal usage."""
    headers: dict[str, str] = defaultdict(dict[str, str])
    """HTTP Headers used to make Requests."""

    # External API and services info
    sock_manager: SocketManager = SocketManager()

    # HTTP-related
    http_method: str = 'GET'
    http_path: str = '/'

    # Health-check
    is_health_check: bool = True
    connections_check_time: int = 0
    fetching_host_statuses_in_progress: bool = False
    last_host_statuses_update: datetime = None
    health_check_method: str = ''
    host_statuses = {}

    # Proxy lists
    proxy_list: list = []
    proxy_list_initial_len: int = 0

    def get_target_url(self) -> str:
        """Get fully qualified URI for target HOST - schema://host:port"""
        return f"{self.protocol}{self.host}:{self.port}{self.http_path}"

    def get_start_time_ns(self) -> int:
        """Get start time in nano seconds"""
        return self.Statistic.start_time.timestamp() * 1000000 * 1000

    def add_error(self, error: Errors):
        """
        Add Error to Errors collection without duplication.
        If Error exists in collection - it updates the error counter.
        """
        if self.errors.__contains__(error.code):
            self.errors[error.code].count += 1
        else:
            self.errors[error.code] = error

    def remove_error(self, error_code: str):
        """Remove Error from collection by Error Code."""
        if self.errors.__contains__(error_code):
            self.errors.__delitem__(error_code)

    def validate(self):
        """Validates context before Run script. Order is matter!"""
        if self.host_ip is None or not is_ipv4(self.host_ip):
            print(f'Cannot get IPv4 for HOST: {self.host}. Could not connect to the target HOST.')
            exit(1)

        if self.IpInfo.my_start_ip is None or not is_ipv4(self.IpInfo.my_start_ip):
            print(f'Cannot get your public IPv4 address. Check your VPN connection.')
            exit(1)

    def __new__(cls):
        """Singleton realization."""
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance


def init_context(_ctx: Context, args):
    """Initialize Context from Input args."""
    _ctx.host = args[0].host
    _ctx.host_ip = common.get_ipv4(args[0].host)
    _ctx.port = args[0].port
    _ctx.protocol = 'https://' if args[0].port == 443 else 'http://'
    _ctx.threads = args[0].threads

    _ctx.attack_method = str(args[0].attack_method).lower()
    _ctx.random_packet_len = bool(args[0].random_packet_len)
    if args[0].max_random_packet_len:
        _ctx.max_random_packet_len = int(args[0].max_random_packet_len)
    elif _ctx.attack_method == 'http':
        _ctx.random_packet_len = False
        _ctx.max_random_packet_len = 0
    elif _ctx.attack_method == 'tcp':
        _ctx.max_random_packet_len = 1024

    _ctx.cpu_count = max(os.cpu_count(), 1)  # to avoid situation when vCPU might be 0

    # Get required data from files
    _ctx.user_agents = common.readfile(os.path.dirname(__file__) + '/useragents.txt')
    _ctx.base_headers = common.readfile(os.path.dirname(__file__) + '/headers.txt')
    _ctx.headers = get_headers_dict(_ctx.base_headers)

    # Get initial info from external services
    _ctx.IpInfo.my_start_ip = common.get_current_ip()
    _ctx.IpInfo.my_country = common.get_country_by_ipv4(_ctx.IpInfo.my_start_ip)
    _ctx.IpInfo.target_country = common.get_country_by_ipv4(_ctx.host_ip)
    _ctx.IpInfo.isCloudflareProtected = common.isCloudFlareProtected(_ctx.host, _ctx.user_agents)

    _ctx.Statistic.start_time = datetime.now()
    _ctx.connections_check_time = time.time_ns()
    _ctx.health_check_method = 'ping' if _ctx.attack_method == 'udp' else _ctx.attack_method
    _ctx.is_health_check = False if args[0].health_check == '0' else True

    _ctx.proxy_list = read_proxy_list(
        args[0].proxy_list) if args[0].proxy_list else None
    _ctx.proxy_list_initial_len = len(
        _ctx.proxy_list) if _ctx.proxy_list is not None else 0

    if args[0].http_method:
        _ctx.http_method = args[0].http_method.upper()
    if args[0].http_path:
        _ctx.http_path = args[0].http_path.lower()
