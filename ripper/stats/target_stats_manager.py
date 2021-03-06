from collections import defaultdict

from ripper.stats.packets_stats import PacketsStats
from ripper.stats.connection_stats import ConnectionStats
from ripper.stats.utils import Row, build_http_codes_distribution, rate_color
from ripper import common
from ripper.constants import *
from ripper.health_check_manager import HealthStatus, AvailabilityDistribution

Target = 'Target'


class TargetStatsManager:
    """Encapsulates target-related statistics."""

    target: Target = None
    """Related target"""
    packets: PacketsStats = None
    """Collect all the stats about TCP/UDP and HTTP packets."""
    http_stats = None
    """Collect stats about HTTP response codes."""
    connect: ConnectionStats = None
    """Collect all the Connections stats via Socket or HTTP Client."""

    def __init__(self, target: Target):
        self.target = target
        self.packets = PacketsStats()
        self.connect = ConnectionStats()
        self.http_stats = defaultdict(int)

    def collect_packets_success(self, sent_bytes: int = 0):
        self.packets.status_sent(sent_bytes)

    def get_availability_msg(self) -> str:
        if self.target.health_check_manager.is_forbidden:
            return f'[orange1]Your IP was blocked with anti-bot or anti DDoS[/]' \
                   f'\nCheck status - CTRL+click on [u blue link={self.target.health_check_manager.request_url}]link'

        status: HealthStatus = self.target.health_check_manager.status
        if status == HealthStatus.start_pending or status == HealthStatus.undefined:
            return f'...detecting ({self.target.health_check_manager.health_check_method.upper()} method)'

        avd: AvailabilityDistribution = self.target.health_check_manager.availability_distribution
        time_str = common.format_dt(self.target.health_check_manager.last_host_statuses_update, DATE_TIME_SHORT)
        accessible_message = f'[{time_str}] Accessible in {avd.succeeded} of {avd.total} zones ({avd.availability_percentage}%)'

        if status == HealthStatus.alive:
            return accessible_message

        if status == HealthStatus.dead:
            return f'{accessible_message}\n{TARGET_DEAD_ERR_MSG}'
    
    def get_packet_length_msg(self) -> str:
        if self.target.min_random_packet_len == self.target.max_random_packet_len:
            return f'{self.target.max_random_packet_len}'
        return f'From {self.target.min_random_packet_len} to {self.target.max_random_packet_len}'

    def build_target_details_stats(self) -> list[Row]:
        """Prepare data for global part of statistics."""
        sent_units = 'Requests' if self.target.attack_method.lower() == 'http' else 'Packets'
        conn_success_rate = self.target.stats.connect.get_success_rate()

        duration = self.target.time_interval_manager.execution_duration
        packets_rps = int(self.target.stats.packets.total_sent / duration.total_seconds())
        data_rps = int(self.target.stats.packets.total_sent_bytes / duration.total_seconds())
        is_health_check = bool(self.target.health_check_manager)

        _sent_bytes_formatted = common.convert_size(self.target.stats.packets.total_sent_bytes)
        _indent = max(
            len(str(self.target.stats.packets.total_sent)),
            len(_sent_bytes_formatted)
        )

        full_stats: list[Row] = [
            #   Description                       Status
            Row('Country, Host IP',               f'[red]{self.target.country:4}[/][cyan]{self.target.host_ip}:{self.target.port} [dim](target-{self.target.index})[/]'),
            Row('HTTP Request',                   f'[cyan]{self.target.http_method}: {self.target.http_url}', visible=self.target.attack_method.lower() == 'http-flood'),
            Row('Attack Method',                  self.target.attack_method.upper()),
            Row('Random Packet Length (bytes)',   self.get_packet_length_msg(), visible=(self.target.min_random_packet_len or self.target.max_random_packet_len)),
            Row('Threads',                        str(len(self.target.attack_threads))),
            Row('CloudFlare Protection',          ('[red]' if self.target.is_cloud_flare_protection else '[green]') + self.target.cloudflare_status(), end_section=not is_health_check),
            Row('Availability (check-host.net)',  f'{self.get_availability_msg()}', visible=is_health_check),
            Row('Sent Bytes @ AVG speed',         f'{_sent_bytes_formatted:{_indent}} @ [green]{common.convert_size(data_rps, "B/s")}'),
            Row(f'Sent {sent_units} @ AVG speed', f'{self.target.stats.packets.total_sent:{_indent},} @ [green]{packets_rps} {sent_units.lower()}/s'),
            # === Info UDP/TCP => insert Sent bytes statistic
            Row('Connections',                    f'success: [green]{self.target.stats.connect.success}[/], failed: [red]{self.target.stats.connect.failed}[/], success rate: {rate_color(conn_success_rate, " %")}', end_section=True),
            # ===================================
            Row('Status Code Distribution',       build_http_codes_distribution(self.target.stats.http_stats), end_section=True, visible=self.target.attack_method.lower() == 'http-flood'),
        ]

        return full_stats
