import curses
import threading
import sys
import time
from datetime import datetime

from ripper.context import Context
from ripper.common import convert_size
from ripper.constants import DEFAULT_CURRENT_IP_VALUE, VERSION
import ripper.services

lock = threading.Lock()


def show_info(_ctx: Context):
    """Prints attack info to console."""
    print("\033c")

    my_ip_masked = _ctx.IpInfo.my_ip_masked() if _ctx.current_ip != DEFAULT_CURRENT_IP_VALUE \
        else DEFAULT_CURRENT_IP_VALUE
    is_random_packet_len = _ctx.attack_method in ('tcp', 'udp') and _ctx.random_packet_len

    if _ctx.IpInfo.my_current_ip:
        if _ctx.IpInfo.my_current_ip == _ctx.IpInfo.my_start_ip:
            your_ip = my_ip_masked
        else:
            your_ip = f'IP was changed, check VPN (current IP: {my_ip_masked})'
    else:
        your_ip = f'Can\'t get your IP. Check internet connection.'

    target_host = f'{_ctx.host}:{_ctx.port}'
    load_method = f'{str(_ctx.attack_method).upper()}'
    thread_pool = f'{_ctx.threads}'
    available_cpu = f'{_ctx.cpu_count}'
    rnd_packet_len = 'YES' if is_random_packet_len else 'NO'
    max_rnd_packet_len = f'{_ctx.max_random_packet_len}' if is_random_packet_len else 'NOT REQUIRED'

    print('------------------------------------------------------')
    print(f'Start time:                 {_ctx.Statistic.start_time.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'Your public IP / Country:   {your_ip} / {_ctx.IpInfo.my_country}')
    print(f'Host IP / Country:          {target_host} / {_ctx.IpInfo.target_country}')
    print(f'CloudFlare Protection:      {_ctx.IpInfo.cloudflare_status()}')
    print(f'Load Method:                {load_method}')
    print(f'Threads:                    {thread_pool}')
    print(f'vCPU count:                 {available_cpu}')
    print(f'Random Packet Length:       {rnd_packet_len}')
    print(f'Max Random Packet Length:   {max_rnd_packet_len}')
    print('------------------------------------------------------')

    sys.stdout.flush()


def show_statistics(_ctx: Context):
    """Prints statistics to console."""

    lock.acquire()
    if not _ctx.Statistic.connect.in_progress:
        t = threading.Thread(target=ripper.services.update_current_ip, args=[_ctx])
        t.start()
    lock.release()

    if _ctx.attack_method == 'tcp':
        ripper.services.check_successful_tcp_attack(_ctx)
    else:
        ripper.services.check_successful_connections(_ctx)
    # cpu_load = get_cpu_load()

    show_info(_ctx)

    connections_success = f'{_ctx.Statistic.connect.success}'
    connections_failed = f'{_ctx.Statistic.connect.failed}'

    curr_time = datetime.now() - _ctx.Statistic.start_time

    print(f'Duration:                   {str(curr_time).split(".", 2)[0]}')
    # print(f'CPU Load Average:           {cpu_load}')
    if _ctx.attack_method == 'http':
        print(f'Requests sent:              {_ctx.Statistic.http.packets_sent}')
        if len(_ctx.http_codes_counter.keys()):
            print(f'HTTP codes distribution:    {build_http_codes_distribution(_ctx.http_codes_counter)}')
    elif _ctx.attack_method == 'tcp':
        size_sent = convert_size(_ctx.Statistic.tcp.packets_sent)
        if _ctx.Statistic.tcp.packets_sent == 0:
            size_sent = f'{size_sent}'
        else:
            size_sent = f'{size_sent}'

        print(f'Total Packets Sent Size:    {size_sent}')
    else:  # udp
        print(f'Packets Sent:               {_ctx.Statistic.udp.packets_sent}')
    print(f'Connection Success:         {connections_success}')
    print(f'Connection Failed:          {connections_failed}')
    print('------------------------------------------------------')
    print(f'Press CTRL+C to interrupt process.')

    if _ctx.errors:
        print('\n\n')
    for error in _ctx.errors:
        print(f'{error}')
        print('\007')

    sys.stdout.flush()
    time.sleep(3)


def build_http_codes_distribution(http_codes_counter):
    codes_distribution = []
    total = sum(http_codes_counter.values())
    for code in http_codes_counter.keys():
        count = http_codes_counter[code]
        percent = round(count * 100 / total)
        codes_distribution.append(f'{code}: {count} ({percent}%)')
    return ', '.join(codes_distribution)


def logo_top() -> str:
    return f'''
██████╗ ██████╗ ██╗██████╗ ██████╗ ███████╗██████╗
██╔══██╗██╔══██╗██║██╔══██╗██╔══██╗██╔════╝██╔══██╗
██║  ██║██████╔╝██║██████╔╝██████╔╝█████╗  ██████╔╝'''


def logo_bottom() -> str:
    return f'''
██║  ██║██╔══██╗██║██╔═══╝ ██╔═══╝ ██╔══╝  ██╔══██╗
██████╔╝██║  ██║██║██║     ██║     ███████╗██║  ██║
╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝'''.strip()


def logo_desc() -> str:
    return'''
It is the end user's responsibility to obey all applicable laws.
It is just like a server testing script and Your IP is visible.

Please, make sure you are ANONYMOUS!'''


def create_dashboard(stdscr, _ctx: Context):
    k = 0
    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_WHITE)

    _CYAN = curses.color_pair(1)
    _YELLOW = curses.color_pair(4)
    _GREEN = curses.color_pair(3)
    _RED = curses.color_pair(2)
    _WHITE = curses.color_pair(5)
    _GRAY = curses.color_pair(6)

    # ==== Ascii art ===
    bold_hr = '═' * 64
    thin_hr = '─' * 64

    # Loop where k is the last character pressed
    # while (k != ord('q')):
    while True:
        # Initialization
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        start_x = 0
        start_y = 0

        # Logo with description
        stdscr.addstr(start_y, start_x, logo_top(), _CYAN)
        start_y += len(logo_top().splitlines())
        stdscr.addstr(start_y, start_x, logo_bottom(), _YELLOW)
        start_y += len(logo_bottom().splitlines())
        stdscr.addstr(start_y, int(len(logo_bottom())/3 - len(VERSION)), VERSION, _GREEN)
        start_y += 1
        stdscr.addstr(start_y, start_x, logo_desc(), _WHITE)
        start_y += len(logo_desc().splitlines()) + 2

        # General info
        info = [
            (bold_hr, '', _WHITE),
            ('Start time', _ctx.Statistic.start_time.strftime("%Y-%m-%d %H:%M:%S"), _WHITE),
            ('Your public IP / Country', f'{_ctx.IpInfo.my_ip_masked()} / {_ctx.IpInfo.my_country}', _CYAN),
            ('Host IP / Country', f'{_ctx.host}:{_ctx.port} / {_ctx.IpInfo.target_country}', _CYAN),
            ('CloudFlare Protection', _ctx.IpInfo.cloudflare_status(), _RED if _ctx.IpInfo.isCloudflareProtected else _GREEN),
            (thin_hr, '', _WHITE),
            ('Load Method', str(_ctx.attack_method).upper(), _WHITE),
            ('Threads', _ctx.threads, _WHITE),
            ('vCPU count', _ctx.cpu_count, _WHITE),
            ('Random Packet Length', _ctx.random_packet_len, _WHITE),
            ('Max Random Packet Length', _ctx.max_random_packet_len, _WHITE),
            (bold_hr, '', _WHITE),
            (f'{_ctx.attack_method.upper()} Statistic', '', _WHITE),
            (bold_hr, '', _WHITE),
            ('Duration', str(datetime.now() - _ctx.Statistic.start_time).split(".", 2)[0], _WHITE),
        ]

        conn_success_rate = _ctx.Statistic.connect.get_success_rate()
        conn_success_rate_color = _RED
        if 70 > conn_success_rate > 50:
            conn_success_rate_color = _YELLOW
        if conn_success_rate >= 70:
            conn_success_rate_color = _GREEN

        if _ctx.attack_method == 'udp':
            info += [
                ('Sent packets', f'{_ctx.Statistic.udp.packets_sent:,}', _WHITE),
                ('Sent bytes', convert_size(_ctx.Statistic.udp.packets_sent_bytes), _WHITE),
                ('Sock connection Success', _ctx.Statistic.connect.success, _GREEN),
                ('Sock connection Failed', _ctx.Statistic.connect.failed, _RED),
                ('Connection Success Rate', f'{conn_success_rate}%', conn_success_rate_color),
            ]

        if _ctx.attack_method == 'tcp':
            info += [
                ('Sent packets', f'{_ctx.Statistic.tcp.packets_sent:,}', _WHITE),
                ('Sent bytes', convert_size(_ctx.Statistic.tcp.packets_sent_bytes), _WHITE),
                ('Sock connection Success', _ctx.Statistic.connect.success, _GREEN),
                ('Sock connection Failed', _ctx.Statistic.connect.failed, _RED),
                ('Connection Success Rate', f'{conn_success_rate}%', conn_success_rate_color),
            ]

        if _ctx.attack_method == 'http':
            info += [
                ('Sent requests', f'{_ctx.Statistic.http.packets_sent:,}', _WHITE),
                ('Connection Success', _ctx.Statistic.connect.success, _GREEN),
                ('Connection Failed', _ctx.Statistic.connect.failed, _RED),
                ('Connection Success Rate', f'{conn_success_rate}%', conn_success_rate_color),
                (thin_hr, '', _WHITE),
                ('Status code distribution', build_http_codes_distribution(_ctx.Statistic.http_stats), _WHITE)
            ]

        for pair in info:
            stdscr.addstr(start_y, start_x, str(pair[0]), _WHITE)
            stdscr.addstr(start_y, start_x + 28, str(pair[1]), pair[2])
            start_y += max(len(pair[0].splitlines()), 1)

        if _ctx.errors:
            for err in _ctx.errors:
                stdscr.addstr(start_y, start_x, err, _RED)
                start_y += max(len(err.splitlines()), 1)

        # Render status bar
        statusbarstr = 'Press CTRL+C to interrupt process.'
        stdscr.attron(_GREEN)
        stdscr.addstr(height - 1, 0, statusbarstr)
        stdscr.addstr(height - 1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        stdscr.attroff(_GREEN)

        # Refresh the screen
        stdscr.refresh()
        time.sleep(1)

        # Wait for next input
        # k = stdscr.getch()
