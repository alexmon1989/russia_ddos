import threading
from collections import defaultdict
from datetime import datetime

from ripper.constants import *


class PacketsStats:
    """Class for TCP/UDP statistic collection."""
    total_sent: int = 0
    """Total packets sent by TCP/UDP."""
    total_sent_prev: int = 0
    """Total packets sent by TCP/UDP (previous state)."""
    total_sent_bytes: int = 0
    """Total sent bytes by TCP/UDP connect."""
    connections_check_time: int = 0
    """Connection last check time."""
    _lock: threading.Lock

    def __init__(self):
        self._lock = threading.Lock()

    def sync_packets_sent(self):
        """Sync previous packets sent stats with current packets sent stats."""
        with self._lock:
            self.total_sent_prev = self.total_sent

    def status_sent(self, sent_bytes: int = 0):
        """
        Collect sent packets statistic.
        :param sent_bytes sent packet size in bytes.
        """
        with self._lock:
            self.total_sent += 1
            self.total_sent_bytes += sent_bytes


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
    _lock: threading.Lock

    def __init__(self):
        self._lock = threading.Lock()

    def get_success_rate(self) -> int:
        """Calculate Success Rate for connection."""
        if self.success == 0:
            return 0

        return int(self.success / (self.success + self.failed) * 100)

    def sync_success(self):
        """Sync previous success state with current success state."""
        with self._lock:
            self.success_prev = self.success

    def set_state_in_progress(self):
        """Set connection State - in progress."""
        with self._lock:
            self.in_progress = True

    def set_state_is_connected(self):
        """Set connection State - is connected."""
        with self._lock:
            self.in_progress = False

    def status_success(self):
        """Collect successful connections."""
        with self._lock:
            self.success += 1

    def status_failed(self):
        """Collect failed connections."""
        with self._lock:
            self.failed += 1


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

    def collect_packets_success(self, sent_bytes: int = 0):
        self.packets.status_sent(sent_bytes)


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
