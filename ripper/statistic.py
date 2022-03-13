import threading
import time
from datetime import datetime

from rich import box
from rich.live import Live
from rich.table import Table

from ripper import common
from ripper.context import Context, ErrorCodes, Errors
from ripper.common import *
from ripper.constants import *
from ripper.health_check import get_health_status

import ripper.services


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


def collect_stats(_ctx: Context) -> list:
    """Prepare data for Statistic."""
    max_length = f' / Max length: {_ctx.max_random_packet_len}' if _ctx.max_random_packet_len else ''
    sent_units = 'Requests' if _ctx.attack_method.lower() == 'http' else 'Packets'
    conn_success_rate = _ctx.Statistic.connect.get_success_rate()
    has_errors = True if len(_ctx.errors) > 0 else False
    check_my_ip = is_my_ip_changed(_ctx.IpInfo.my_start_ip, _ctx.IpInfo.my_current_ip)
    your_ip_was_changed = f'\n[orange1]{YOUR_IP_WAS_CHANGED}' if check_my_ip else ''

    full_stats = [
        # Description                 Status
        ('Start Time',                format_dt(_ctx.Statistic.start_time)),
        ('Your Public IP / Country',  f'[cyan]{_ctx.IpInfo.my_ip_masked()} / [green]{_ctx.IpInfo.my_country}{your_ip_was_changed}'),
        ('Host IP / Country',         f'[cyan]{_ctx.host_ip}:{_ctx.port} / {_ctx.IpInfo.target_country}'),
        ('Load Method',               _ctx.attack_method.upper(), True),
        # ===================================
        ('Threads',                   f'{_ctx.threads}'),
        ('vCPU Count',                f'{_ctx.cpu_count}'),
        ('Random Packet Length',      f'{_ctx.random_packet_len}{max_length}', True),
        # ===================================
        ('CloudFlare DNS Protection', ('[red]' if _ctx.IpInfo.isCloudflareProtected else '[green]') + _ctx.IpInfo.cloudflare_status()),
        ('Last Availability Check',   f'[cyan]{format_dt(_ctx.last_host_statuses_update, DATE_TIME_SHORT)}'),
        ('Host Availability',         f'{get_health_status(_ctx)}', True),
        # ===================================
        (f'[cyan][bold]{_ctx.attack_method.upper()} Statistic', '', True),
        # ===================================
        ('Duration',                  f'{str(datetime.datetime.now() - _ctx.Statistic.start_time).split(".", 2)[0]}'),
        (f'Sent {sent_units}',        f'{_ctx.Statistic.packets.total_sent:,}'),
        # === Info UDP/TCP => insert Sent bytes statistic
        ('Connection Success',        f'[green]{_ctx.Statistic.connect.success}'),
        ('Connection Failed',         f'[red]{_ctx.Statistic.connect.failed}'),
        ('Connection Success Rate',   f'{rate_color(conn_success_rate)}{conn_success_rate}%', True),
    ]

    if _ctx.attack_method.lower() == 'http':
        full_stats.append(
            ('Status Code Distribution', build_http_codes_distribution(_ctx.Statistic.http_stats), has_errors))
    if not _ctx.attack_method.lower() == 'http':
        full_stats.insert(
            13,
            ('Sent Bytes',            f'{convert_size(_ctx.Statistic.packets.total_sent_bytes)}'))

    if has_errors:
        full_stats.append(('[bright_red][bold]Error Log', '', True))
        for key in _ctx.errors:
            err = _ctx.errors.get(key)
            full_stats.append((f'{key}', f'Total: {err.count}\n{err.message}'))

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

    table.add_column("Description")
    table.add_column("Status")

    for itm in collect_stats(_ctx):
        end_section = itm[2] if 3 == len(itm) else False
        table.add_row(itm[0], itm[1], end_section=end_section)

    return table


lock = threading.Lock()


def refresh(_ctx: Context):
    lock.acquire()
    if not _ctx.Statistic.connect.in_progress:
        threading.Thread(target=ripper.services.update_current_ip, args=[_ctx]).start()
        threading.Thread(target=ripper.services.update_host_statuses, args=[_ctx]).start()

    if _ctx.IpInfo.my_country == GEOIP_NOT_DEFINED:
        threading.Thread(target=common.get_country_by_ipv4, args=[_ctx.IpInfo.my_current_ip]).start()
    if _ctx.IpInfo.target_country == GEOIP_NOT_DEFINED:
        threading.Thread(target=common.get_country_by_ipv4, args=[_ctx.host_ip]).start()

    lock.release()

    # Check for my IPv4 wasn't changed
    if common.is_my_ip_changed(_ctx.IpInfo.my_start_ip, _ctx.IpInfo.my_current_ip):
        _ctx.add_error(Errors(ErrorCodes.YourIpWasChanged.value, YOUR_IP_WAS_CHANGED))

    if _ctx.attack_method == 'tcp':
        attack_successful = ripper.services.check_successful_tcp_attack(_ctx)
    else:
        attack_successful = ripper.services.check_successful_connections(_ctx)
    if not attack_successful:
        _ctx.add_error(Errors(ErrorCodes.HostDoesNotResponse.value, get_no_successful_connection_die_msg()))

        exit(get_no_successful_connection_die_msg())


def render(_ctx: Context):
    """Show DRipper runtime statistic."""
    with Live(generate_stats(_ctx), refresh_per_second=1) as live:
        # for _ in range(720):
        while True:
            time.sleep(0.5)
            live.update(generate_stats(_ctx))
            refresh(_ctx)
