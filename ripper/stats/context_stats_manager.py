from math import floor
from rich.table import Table
from rich import box

from ripper.context.target import Target
from ripper.stats.utils import Row, badge_error, badge_warn
from rich.console import Group
from ripper import common
from ripper.constants import *
from ripper.time_interval_manager import TimeIntervalManager
from ripper.context.events_journal import EventsJournal

Context = 'Context'
events_journal = EventsJournal()


class ContextStatsManager:
    _ctx: Context = None
    """Context we are working with."""

    interval_manager: TimeIntervalManager = None

    def __init__(self, _ctx: Context):
        self._ctx = _ctx
        self.interval_manager = TimeIntervalManager()

    @property
    def current_target_idx(self) -> int:
        """
        We show one target details at the same time.
        Pagination happens automatically.
        Method calculates current index of target to display based on script execution duration.
        """
        duration = self.interval_manager.get_start_duration().total_seconds()
        cnt = len(self._ctx.targets_manager.targets)
        change_interval = TARGET_STATS_AUTO_PAGINATION_INTERVAL_SECONDS
        return floor((duration/change_interval) % cnt)

    @property
    def current_target(self) -> Target:
        return self._ctx.targets_manager.targets[self.current_target_idx]

    def build_global_details_stats(self) -> list[Row]:
        """Prepare data for global part of statistics."""
        duration = self.interval_manager.get_start_duration()
        max_length = f' | Max length: {self._ctx.max_random_packet_len}' if self._ctx.max_random_packet_len else ''
        is_proxy_list = bool(self._ctx.proxy_manager.proxy_list and len(self._ctx.proxy_manager.proxy_list))

        your_ip_disclaimer = f'{badge_warn(MSG_DONT_USE_VPN_WITH_PROXY)}' if is_proxy_list else ''
        your_ip_was_changed = f'{badge_error(MSG_YOUR_IP_WAS_CHANGED)} {badge_warn(MSG_CHECK_VPN_CONNECTION)}[/]' if self._ctx.myIpInfo.is_ip_changed() else ''

        full_stats: list[Row] = [
            #   Description                  Status
            Row('Start Time, Duration',      f'{common.format_dt(self._ctx.interval_manager.start_time)}  ({str(duration).split(".", 2)[0]})'),
            Row('Your Country, Public IP',   f'[green]{self._ctx.myIpInfo.country:4}[/] [cyan]{self._ctx.myIpInfo.ip_masked:20}[/] {your_ip_disclaimer}{your_ip_was_changed}'),
            Row('Total Threads',             f'{self._ctx.threads_count}', visible=len(self._ctx.targets_manager.targets) > 1),
            Row('Proxies Count',             f'[cyan]{len(self._ctx.proxy_manager.proxy_list)} | {self._ctx.proxy_manager.proxy_list_initial_len}', visible=is_proxy_list),
            Row('Proxies Type',              f'[cyan]{self._ctx.proxy_manager.proxy_type.value}', visible=is_proxy_list),
            Row('vCPU Count',                f'{self._ctx.cpu_count}'),
            Row('Socket Timeout (seconds)',  f'{self._ctx.sock_manager.socket_timeout}'),
            Row('Random Packet Length',      f'{self._ctx.random_packet_len}{max_length}', end_section=True),
            # ===================================
        ]

        return full_stats

    def build_target_rotation_header_details_stats(self) -> list[Row]:
        cnt = len(self._ctx.targets_manager.targets)
        if cnt < 2:
            return []

        duration = self.interval_manager.get_start_duration().total_seconds()
        change_interval = TARGET_STATS_AUTO_PAGINATION_INTERVAL_SECONDS
        current_position = duration/change_interval
        next_target_in_seconds = 1 + floor(change_interval * (1 - (current_position - floor(current_position))))
        return [
            Row(f'[cyan][bold]Target ({self.current_target.uri}) {self.current_target_idx + 1}/{cnt} (next in {next_target_in_seconds})', end_section=True),
            # ===================================
        ]

    def build_details_stats_table(self) -> Table:
        details_table = Table(
            style='bold',
            box=box.HORIZONTALS,
            width=MIN_SCREEN_WIDTH,
            caption=CONTROL_CAPTION if not events_journal.get_max_event_level() else None,
            caption_style='bold',
        )

        details_table.add_column('Description')
        details_table.add_column('Status')

        rows = self.build_global_details_stats()
        rows += self.build_target_rotation_header_details_stats()
        if self.current_target:
            rows += self.current_target.stats.build_target_details_stats()

        for row in rows:
            if row.visible:
                details_table.add_row(row.label, row.value, end_section=row.end_section)

        return details_table

    def build_events_table(self) -> Table:
        events_log = Table(
            box=box.SIMPLE,
            min_width=MIN_SCREEN_WIDTH,
            width=MIN_SCREEN_WIDTH,
            caption=CONTROL_CAPTION,
            caption_style='bold')

        events_log.add_column(f'[blue]Events Log', style='dim')

        for event in events_journal.get_log():
            events_log.add_row(event)

        return events_log

    def build_stats(self):
        """Create statistics from aggregated RAW Statistics data."""
        details_table = self.build_details_stats_table()
        events_table = self.build_events_table() if events_journal.get_max_event_level() else None
        group = Group(details_table) if events_table is None else Group(details_table, events_table)
        return group
