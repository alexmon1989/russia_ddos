import threading
import time
from datetime import datetime

from rich import box
from rich.console import Group, Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

import ripper.common as common
import ripper.services as services
from ripper.context.context import Context
from ripper.context.events_journal import EventsJournal
from ripper.constants import *

Events = EventsJournal()


def build_http_codes_distribution(http_codes_counter) -> str:
    codes_distribution = []
    total = sum(http_codes_counter.values())
    for code in http_codes_counter.keys():
        count = http_codes_counter[code]
        percent = round(count * 100 / total)
        codes_distribution.append(f'{code}: {percent}%')
    codes_distribution.sort()
    return ', '.join(codes_distribution)


def rate_color(rate: int, units: str = '') -> str:
    """
    Get color schema for percentage value.
    Color schema looks like red-yellow-green scale for values 0-50-100.
    """
    color = '[red]'
    if 30 > rate > 20:
        color = '[orange_red1]'
    if 50 > rate > 30:
        color = '[dark_orange]'
    if 70 > rate > 50:
        color = '[orange1]'
    if 90 > rate > 70:
        color = '[yellow4]'
    if rate >= 90:
        color = '[green1]'

    return f'{color}{rate}{units}[default]'


class Row:
    def __init__(self, label: str, value: str, visible: bool = True, end_section: bool = False):
        self.label = label
        self.value = value
        self.visible = visible
        self.end_section = end_section


def collect_stats(_ctx: Context) -> list[Row]:
    """Prepare data for Statistic."""
    max_length = f' | Max length: {_ctx.max_random_packet_len}' if _ctx.max_random_packet_len else ''
    sent_units = 'Requests' if _ctx.target.attack_method.lower() == 'http' else 'Packets'
    conn_success_rate = _ctx.target.statistic.connect.get_success_rate()
    check_my_ip = common.is_my_ip_changed(_ctx.myIpInfo.my_start_ip, _ctx.myIpInfo.my_current_ip)
    your_ip_was_changed = f'\n[orange1]{YOUR_IP_WAS_CHANGED}' if check_my_ip else ''
    is_proxy_list = bool(_ctx.proxy_manager.proxy_list and len(_ctx.proxy_manager.proxy_list))
    your_ip_disclaimer = f' (do not use VPN with proxy) ' if is_proxy_list else ''

    duration = datetime.now() - _ctx.target.statistic.start_time
    packets_rps = int(_ctx.target.statistic.packets.total_sent / duration.total_seconds())
    data_rps = int(_ctx.target.statistic.packets.total_sent_bytes / duration.total_seconds())

    full_stats: list[Row] = [
        #   Description                  Status
        Row('Start Time, duration',      f'{common.format_dt(_ctx.target.statistic.start_time)} - {str(duration).split(".", 2)[0]}'),
        Row('Your Country, Public IP',   f'[green]{_ctx.myIpInfo.my_country:4}[/] [cyan]{_ctx.myIpInfo.my_ip_masked():20} [red]{your_ip_disclaimer}{your_ip_was_changed}'),
        Row('Host Country, IP',          f'[red]{_ctx.target.country:4}[/] [cyan]{_ctx.target.host_ip}:{_ctx.target.port}'),
        Row('HTTP Request',              f'[cyan]{_ctx.target.http_method}: {_ctx.target.url()}', visible=_ctx.target.attack_method.lower().startswith('http')),
        Row('Attack Method',             _ctx.target.attack_method.lower(), end_section=True),
        # ===================================
        Row('Threads',                   f'{_ctx.threads}'),
        Row('Proxies Count',             f'[cyan]{len(_ctx.proxy_manager.proxy_list)} | {_ctx.proxy_manager.proxy_list_initial_len}', visible=is_proxy_list),
        Row('Proxies Type',              f'[cyan]{_ctx.proxy_manager.proxy_type.value}', visible=is_proxy_list),
        Row('vCPU Count',                f'{_ctx.cpu_count}'),
        Row('Socket Timeout (seconds)',  f'{_ctx.sock_manager.socket_timeout}'),
        Row('Random Packet Length',      f'{_ctx.random_packet_len}{max_length}', end_section=True),
        # ===================================
        Row('CloudFlare DNS Protection', ('[red]' if _ctx.target.is_cloud_flare_protection else '[green]') + _ctx.target.cloudflare_status(), end_section=not _ctx.is_health_check),
        Row('Last Availability Check',   f'[cyan]{common.format_dt(_ctx.target.health_check_manager.last_host_statuses_update, DATE_TIME_SHORT)}'),
        Row('Host Availability',         f'{_ctx.target.health_check_manager.get_health_status()}', visible=_ctx.is_health_check, end_section=True),
        # ===================================
        Row(f'[cyan][bold]{_ctx.target.attack_method.upper()} Statistics', '', end_section=True),
        # ===================================
        Row('Sent Bytes @ AVG speed',    f'{common.convert_size(_ctx.target.statistic.packets.total_sent_bytes):>12} @ [green]{common.convert_size(data_rps)}/s'),
        Row(f'Sent {sent_units} @ AVG speed', f'{_ctx.target.statistic.packets.total_sent:>12,} @ [green]{packets_rps} {sent_units.lower()}/s'),
        # === Info UDP/TCP => insert Sent bytes statistic
        Row('Connections',               f'success: [green]{_ctx.target.statistic.connect.success}[/], failed: [red]{_ctx.target.statistic.connect.failed}[/], success rate: {rate_color(conn_success_rate, " %")}', end_section=True),
        # ===================================
        Row('Status Code Distribution',  build_http_codes_distribution(_ctx.target.statistic.http_stats), end_section=True, visible=_ctx.target.attack_method.lower() in ['http-flood', 'http-bypass']),
    ]

    return full_stats


def generate_stats(_ctx: Context):
    """Create statistic from aggregated RAW Statistic data."""

    caption = f'[grey53]Press [green]CTRL+C[grey53] to interrupt process.{BANNER}'

    table = Table(
        style='bold',
        box=box.HORIZONTALS,
        min_width=MIN_SCREEN_WIDTH,
        width=MIN_SCREEN_WIDTH,
        caption_style='bold')

    table.add_column('Description', width=27)
    table.add_column('Status')

    for row in collect_stats(_ctx):
        if row.visible:
            table.add_row(row.label, row.value, end_section=row.end_section)

    events_log = Table(
        box=box.SIMPLE,
        min_width=MIN_SCREEN_WIDTH,
        width=MIN_SCREEN_WIDTH,
        caption=caption,
        caption_style='bold')

    events_log.add_column('[blue]Events Log', style='dim')

    for event in Events.get_log():
        events_log.add_row(f'{event}')

    return Group(table, events_log)


lock = threading.Lock()


def refresh(_ctx: Context) -> None:
    """
    Check threads, IPs, VPN status, etc.
    """
    lock.acquire()

    threading.Thread(
        target=services.update_current_ip,
        args=[_ctx, UPDATE_CURRENT_IP_CHECK_PERIOD_SEC]).start()

    if _ctx.is_health_check:
        threading.Thread(target=services.update_host_statuses, args=[_ctx]).start()

    if _ctx.myIpInfo.my_country == GEOIP_NOT_DEFINED:
        threading.Thread(target=common.get_country_by_ipv4, args=[_ctx.myIpInfo.my_current_ip]).start()
    if _ctx.target.country == GEOIP_NOT_DEFINED:
        threading.Thread(target=common.get_country_by_ipv4, args=[_ctx.target.host_ip]).start()

    lock.release()

    # Check for my IPv4 wasn't changed (if no proxylist only)
    if _ctx.proxy_manager.proxy_list_initial_len == 0 and common.is_my_ip_changed(_ctx.myIpInfo.my_start_ip, _ctx.myIpInfo.my_current_ip):
        Events.error(YOUR_IP_WAS_CHANGED)

    if not _ctx.target.statistic.packets.validate_connection(SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC):
        msg = f'There were no successful connections for more ' \
              f'than {NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC // 60} minutes. ' \
              f'Your attack is ineffective.'
        Events.error(msg)
        exit(msg)

    if _ctx.proxy_manager.proxy_list_initial_len > 0 and len(_ctx.proxy_manager.proxy_list) == 0:
        Events.error(f'Host does not respond {NO_MORE_PROXIES_MSG}')
        exit(NO_MORE_PROXIES_MSG)


def render_statistic(_ctx: Context) -> None:
    """Show DRipper runtime statistic."""
    console = Console()
    logo = Panel(LOGO_COLOR, box=box.SIMPLE, width=MIN_SCREEN_WIDTH)
    console.print(logo, justify='center', width=MIN_SCREEN_WIDTH)

    with Live(generate_stats(_ctx), vertical_overflow='visible') as live_table:
        while True:
            time.sleep(0.4)
            refresh(_ctx)
            live_table.update(generate_stats(_ctx))
            if _ctx.dry_run:
                break
