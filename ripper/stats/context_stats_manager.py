from datetime import datetime
from rich.table import Table
from rich import box

from ripper.context.target import Target
from ripper.errors_manager import ErrorsManager
from ripper.stats.utils import Row
from rich.console import Group
from ripper import common
from ripper.constants import *

Context = 'Context'


class ContextStatsManager:
    start_time: datetime = None
    """Script start time."""
    _ctx: Context = None
    """Context we are working with."""
    current_target_idx: int = 0
    """We show one target details at the same time."""

    def __init__(self, _ctx: Context):
        self.start_time = datetime.now()
        self._ctx = _ctx

    @property
    def current_target(self) -> Target:
        return self._ctx.targets[self.current_target_idx]
    
    @property
    def combined_error_manager(self) -> ErrorsManager:
        em = ErrorsManager()
        em.add_submanager(self._ctx.errors_manager)
        # Merges context-level errors with visible target-level errors
        if self.current_target:
            em.add_submanager(self.current_target.errors_manager)
        return em

    def build_global_details_stats(self) -> list[Row]:
        """Prepare data for global part of statistics."""
        max_length = f' | Max length: {self._ctx.max_random_packet_len}' if self._ctx.max_random_packet_len else ''
        check_my_ip = common.is_my_ip_changed(self._ctx.myIpInfo.my_start_ip, self._ctx.myIpInfo.my_current_ip)
        your_ip_was_changed = f'\n[orange1]{YOUR_IP_WAS_CHANGED_ERR_MSG}' if check_my_ip else ''
        is_proxy_list = bool(self._ctx.proxy_manager.proxy_list and len(self._ctx.proxy_manager.proxy_list))
        your_ip_disclaimer = f' (do not use VPN with proxy) ' if is_proxy_list else ''

        full_stats: list[Row] = [
            #   Description                  Status
            Row('Start Time',                common.format_dt(self._ctx.start_time)),
            Row('Your Public IP | Country',  f'[cyan]{self._ctx.myIpInfo.my_ip_masked()} | [green]{self._ctx.myIpInfo.my_country}[red]{your_ip_disclaimer}{your_ip_was_changed}'),
            Row('Total Threads',             f'{self._ctx.threads}'),
            Row('Proxies Count',             f'[cyan]{len(self._ctx.proxy_manager.proxy_list)} | {self._ctx.proxy_manager.proxy_list_initial_len}', visible=is_proxy_list),
            Row('Proxies Type',              f'[cyan]{self._ctx.proxy_manager.proxy_type.value}', visible=is_proxy_list),
            Row('vCPU Count',                f'{self._ctx.cpu_count}'),
            Row('Socket Timeout (seconds)',  f'{self._ctx.sock_manager.socket_timeout}'),
            Row('Random Packet Length',      f'{self._ctx.random_packet_len}{max_length}', end_section=True),
            # ===================================
        ]

        return full_stats

    def build_details_stats_table(self) -> Table:
        table_caption = CONTROL_CAPTION if not self.combined_error_manager.has_errors() else None

        details_table = Table(
            title=LOGO_COLOR,
            title_justify='center',
            style='bold',
            box=box.HORIZONTALS,
            min_width=MIN_SCREEN_WIDTH,
            width=MIN_SCREEN_WIDTH,
            caption=table_caption,
            caption_style='bold')

        details_table.add_column('Description')
        details_table.add_column('Status')

        rows = self.build_global_details_stats()
        if self.current_target:
            rows += self.current_target.stats.build_target_details_stats()

        for row in rows:
            if row.visible:
                details_table.add_row(row.label, row.value, end_section=row.end_section)
        
        return details_table

    def build_errors_table(self) -> Table:
      logs_caption = CONTROL_CAPTION if self.combined_error_manager.has_errors() else None
      logs_table = None
      if self.combined_error_manager.has_errors():
          logs_table = Table(
              box=box.SIMPLE,
              min_width=MIN_SCREEN_WIDTH,
              width=MIN_SCREEN_WIDTH,
              caption=logs_caption,
              caption_style='bold')

          logs_table.add_column('Time')
          logs_table.add_column('Action')
          logs_table.add_column('Q-ty')
          logs_table.add_column('Message')

          for key in self.combined_error_manager.errors:
              err = self.combined_error_manager.errors.get(key)
              logs_table.add_row(f'[cyan]{err.time.strftime(DATE_TIME_SHORT)}',
                           f'[orange1]{err.code}',
                           f'{err.count}',
                           f'{err.message}')
      return logs_table

    def build_stats(self):
        """Create statistics from aggregated RAW Statistics data."""
        details_table = self.build_details_stats_table()
        errors_table = self.build_errors_table()
        group = Group(details_table) if errors_table is None else Group(details_table, errors_table)
        return group
