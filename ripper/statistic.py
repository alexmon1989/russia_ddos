import threading
import time
from datetime import datetime
from rich import box
from rich.live import Live
from rich.table import Table

import ripper.common as common
import ripper.services as services
from ripper.context import Context, ErrorCodes, Errors
from ripper.constants import *
from ripper.health_check import get_health_status


def build_http_codes_distribution(http_codes_counter) -> str:
    codes_distribution = []
    total = sum(http_codes_counter.values())
    for code in http_codes_counter.keys():
        count = http_codes_counter[code]
        percent = round(count * 100 / total)
        codes_distribution.append(f'{code}: {count} ({percent}%)')
    return ', '.join(codes_distribution)


def rate_color(rate: int) -> str:
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

    return color


class Row:
    def __init__(self, label: str, value: str, visible: bool = True, end_section: bool = False):
        self.label = label
        self.value = value
        self.visible = visible
        self.end_section = end_section


def collect_stats(_ctx: Context) -> list[Row]:
    """Prepare data for Statistic."""
    max_length = f' / Max length: {_ctx.max_random_packet_len}' if _ctx.max_random_packet_len else ''
    sent_units = 'Requests' if _ctx.attack_method.lower() == 'http' else 'Packets'
    conn_success_rate = _ctx.Statistic.connect.get_success_rate()
    has_errors = True if len(_ctx.errors) > 0 else False
    check_my_ip = common.is_my_ip_changed(_ctx.IpInfo.my_start_ip, _ctx.IpInfo.my_current_ip)
    your_ip_was_changed = f'\n[orange1]{YOUR_IP_WAS_CHANGED}' if check_my_ip else ''
    is_proxy_list = _ctx.proxy_manager.proxy_list and len(_ctx.proxy_manager.proxy_list)
    your_ip_disclaimer = f' (do not use VPN with proxy) ' if is_proxy_list else ''

    full_stats: list[Row] = [
        #   Description                  Status
        Row('Start Time',                common.format_dt(_ctx.Statistic.start_time)),
        Row('Your Public IP / Country',  f'[cyan]{_ctx.IpInfo.my_ip_masked()} / [green]{_ctx.IpInfo.my_country}[red]{your_ip_disclaimer}{your_ip_was_changed}'),
        Row('Host IP / Country',         f'[cyan]{_ctx.host_ip}:{_ctx.port} / [red]{_ctx.IpInfo.target_country}'),
        Row('HTTP Request',              f'[cyan]{_ctx.http_method}: {_ctx.get_target_url()}', visible=_ctx.attack_method.lower() == 'http'),
        Row('Load Method',               _ctx.attack_method.upper(), end_section=True),
        # ===================================
        Row('Threads',                   f'{_ctx.threads}'),
        Row('Proxies count',             f'[cyan]{len(_ctx.proxy_manager.proxy_list)} / {_ctx.proxy_manager.proxy_list_initial_len}', visible=is_proxy_list),
        Row('vCPU Count',                f'{_ctx.cpu_count}'),
        Row('Socket Timeout (seconds)',  f'{_ctx.sock_manager.socket_timeout}'),
        Row('Random Packet Length',      f'{_ctx.random_packet_len}{max_length}', end_section=True),
        # ===================================
        Row('CloudFlare DNS Protection', ('[red]' if _ctx.IpInfo.isCloudflareProtected else '[green]') + _ctx.IpInfo.cloudflare_status(), end_section=not _ctx.is_health_check),
        Row('Last Availability Check',   f'[cyan]{common.format_dt(_ctx.last_host_statuses_update, DATE_TIME_SHORT)}', visible=(_ctx.is_health_check and len(_ctx.host_statuses.values()))),
        Row('Host Availability',         f'{get_health_status(_ctx)}', visible=_ctx.is_health_check, end_section=True),
        # ===================================
        Row(f'[cyan][bold]{_ctx.attack_method.upper()} Statistics', '', end_section=True),
        # ===================================
        Row('Duration',                  f'{str(datetime.now() - _ctx.Statistic.start_time).split(".", 2)[0]}'),
        Row('Sent Bytes',                f'{common.convert_size(_ctx.Statistic.packets.total_sent_bytes)}', visible=_ctx.attack_method.lower() != 'http'),
        Row(f'Sent {sent_units}',        f'{_ctx.Statistic.packets.total_sent:,}'),
        # === Info UDP/TCP => insert Sent bytes statistic
        Row('Connection Success',        f'[green]{_ctx.Statistic.connect.success}'),
        Row('Connection Failed',         f'[red]{_ctx.Statistic.connect.failed}'),
        Row('Connection Success Rate',   f'{rate_color(conn_success_rate)}{conn_success_rate}%', end_section=True),
        # ===================================
        Row('Status Code Distribution',  build_http_codes_distribution(_ctx.Statistic.http_stats), end_section=has_errors, visible=_ctx.attack_method.lower() == 'http'),
    ]

    if has_errors:
        full_stats.append(Row('[bright_red][bold]Error Log', '', end_section=True))
        for key in _ctx.errors:
            err = _ctx.errors.get(key)
            full_stats.append(Row(f'{key}', f'Total: {err.count}\n{err.message}'))

    return full_stats


def generate_stats(_ctx: Context) -> Table:
    """Create statistic from aggregated RAW Statistic data."""

    table = Table(
        title=LOGO_COLOR,
        title_justify='center',
        style='bold',
        box=box.HORIZONTALS,
        min_width=MIN_SCREEN_WIDTH,
        width=MIN_SCREEN_WIDTH,
        caption=f'[grey53]Press [green]CTRL+C[grey53] to interrupt process.{BANNER}',
        caption_style='bold')

    table.add_column('Description')
    table.add_column('Status')

    for row in collect_stats(_ctx):
        if row.visible:
            table.add_row(row.label, row.value, end_section=row.end_section)

    return table


lock = threading.Lock()


def refresh(_ctx: Context) -> None:
    """Check threads, IPs, VPN status, etc."""
    lock.acquire()
    if not _ctx.Statistic.connect.in_progress:
        threading.Thread(target=services.update_current_ip, args=[_ctx]).start()
        if _ctx.is_health_check:
            threading.Thread(target=services.update_host_statuses, args=[_ctx]).start()

    if _ctx.IpInfo.my_country == GEOIP_NOT_DEFINED:
        threading.Thread(target=common.get_country_by_ipv4, args=[_ctx.IpInfo.my_current_ip]).start()
    if _ctx.IpInfo.target_country == GEOIP_NOT_DEFINED:
        threading.Thread(target=common.get_country_by_ipv4, args=[_ctx.host_ip]).start()

    lock.release()

    # Check for my IPv4 wasn't changed (if no proxylist only)
    if _ctx.proxy_manager.proxy_list_initial_len == 0 and common.is_my_ip_changed(_ctx.IpInfo.my_start_ip, _ctx.IpInfo.my_current_ip):
        _ctx.add_error(Errors(ErrorCodes.YourIpWasChanged.value, YOUR_IP_WAS_CHANGED))

    if not services.validate_attack(_ctx):
        _ctx.add_error(Errors(ErrorCodes.HostDoesNotResponse.value,
                       common.get_no_successful_connection_die_msg()))
        exit(common.get_no_successful_connection_die_msg())

    if _ctx.proxy_manager.proxy_list_initial_len > 0 and len(_ctx.proxy_manager.proxy_list) == 0:
        _ctx.add_error(Errors(ErrorCodes.HostDoesNotResponse.value,
                       common.get_no_more_proxies_msg()))
        exit(common.get_no_more_proxies_msg())


def render_statistic(_ctx: Context) -> None:
    """Show DRipper runtime statistic."""
    with Live(generate_stats(_ctx), vertical_overflow='visible') as live:
        # for _ in range(720):
        while True:
            time.sleep(0.5)
            live.update(generate_stats(_ctx))
            refresh(_ctx)
