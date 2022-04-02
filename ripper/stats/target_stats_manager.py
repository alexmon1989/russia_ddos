from collections import defaultdict
from datetime import datetime

from ripper.stats.packets_stats import PacketsStats
from ripper.stats.connection_stats import ConnectionStats
from ripper.stats.utils import Row, build_http_codes_distribution, rate_color
from ripper import common
from ripper.constants import *

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
        self.packets.total_sent += 1
        self.packets.total_sent_bytes += sent_bytes

    def build_target_details_stats(self) -> list[Row]:
        """Prepare data for global part of statistics."""
        sent_units = 'Requests' if self.target.attack_method.lower() == 'http' else 'Packets'
        conn_success_rate = self.target.stats.connect.get_success_rate()

        duration = self.target.interval_manager.get_start_duration()
        packets_rps = int(self.target.stats.packets.total_sent / duration.total_seconds())
        data_rps = int(self.target.stats.packets.total_sent_bytes / duration.total_seconds())
        is_health_check = bool(self.target.health_check_manager)

        full_stats: list[Row] = [
            #   Description                  Status
            Row('Host IP | Country',         f'[cyan]{self.target.host_ip}:{self.target.port} | [red]{self.target.country}'),
            Row('HTTP Request',              f'[cyan]{self.target.http_method}: {self.target.url}', visible=self.target.attack_method.lower() == 'http-flood'),
            Row('Attack Method',             self.target.attack_method.upper()),
            Row('Threads',                   f'{self.target.threads}'),
            Row('CloudFlare DNS Protection', ('[red]' if self.target.is_cloud_flare_protection else '[green]') + self.target.cloudflare_status(), end_section=not is_health_check),
            Row('Last Availability Check',   f'[cyan]{common.format_dt(self.target.health_check_manager.last_host_statuses_update, DATE_TIME_SHORT)}', visible=(is_health_check and len(self.target.health_check_manager.host_statuses.values()))),
            Row('Host Availability',         f'{self.target.health_check_manager.get_health_status()}', visible=is_health_check, end_section=True),
            # ===================================
            Row(f'[cyan][bold]{self.target.attack_method.upper()} Statistics', end_section=True),
            # ===================================
            Row('Duration',                  f'{str(duration).split(".", 2)[0]}'),
            Row('Sent Bytes | AVG speed',    f'{common.convert_size(self.target.stats.packets.total_sent_bytes)} | [green]{common.convert_size(data_rps)}/s'),
            Row(f'Sent {sent_units} | AVG speed', f'{self.target.stats.packets.total_sent:,} | [green]{packets_rps} {sent_units.lower()}/s'),
            # === Info UDP/TCP => insert Sent bytes statistic
            Row('Connection Success',        f'[green]{self.target.stats.connect.success}'),
            Row('Connection Failed',         f'[red]{self.target.stats.connect.failed}'),
            Row('Connection Success Rate',   f'{rate_color(conn_success_rate)}{conn_success_rate}%', end_section=True),
            # ===================================
            Row('Status Code Distribution',  build_http_codes_distribution(self.target.stats.http_stats), end_section=True, visible=self.target.attack_method.lower() == 'http-flood'),
        ]

        return full_stats
