import http.client
import ipaddress
import socket
import string
import random
import math
import os
import subprocess
import json
import sys
import urllib.request
from functools import lru_cache
from datetime import datetime
from colorama import Fore

from ripper.constants import (GETTING_SERVER_IP_ERROR_MSG, NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG,
                              DEFAULT_CURRENT_IP_VALUE, VERSION, NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC)


@lru_cache(maxsize=None)
def get_server_ip_error_msg() -> str:
    return Fore.RED + GETTING_SERVER_IP_ERROR_MSG + Fore.RESET


@lru_cache(maxsize=None)
def get_no_successful_connection_error_msg() -> str:
    return Fore.RED + NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG + Fore.RESET


def get_no_successful_connection_die_msg() -> str:
    return f"{Fore.LIGHTRED_EX}There were no successful connections for more " \
           f"than {NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC // 60} minutes. " \
           f"Your attack is ineffective.{Fore.RESET}"


def readfile(filename: str):
    """Read string from file"""
    with open(filename, 'r') as file:
        return file.readlines()


def get_random_string(len_from, len_to):
    """Random string with different length"""
    length = random.randint(len_from, len_to)
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str


def get_random_port():
    ports = [22, 53, 80, 443]
    return random.choice(ports)


def get_first_ip_part(ip: str) -> str:
    parts = ip.split('.')
    if len(parts) > 1:
        return f'{parts[0]}.*.*.*'
    else:
        return parts[0]


def get_current_ip():
    """Gets user IP."""
    current_ip = DEFAULT_CURRENT_IP_VALUE
    try:
        current_ip = os.popen('curl -s ifconfig.me').readline() \
            if os.name == 'posix' else urllib.request.urlopen('https://ifconfig.me').read().decode('utf8')
    except:
        pass

    return current_ip


def format_dt(dt: datetime):
    if dt is None:
        return ''
    return dt.strftime("%Y-%m-%d %H:%M:%S")


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
    except:
        return False

    return False


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


def print_logo():
    print(Fore.CYAN + f'''

██████╗ ██████╗ ██╗██████╗ ██████╗ ███████╗██████╗
██╔══██╗██╔══██╗██║██╔══██╗██╔══██╗██╔════╝██╔══██╗
██║  ██║██████╔╝██║██████╔╝██████╔╝█████╗  ██████╔╝ {Fore.YELLOW + ''}
██║  ██║██╔══██╗██║██╔═══╝ ██╔═══╝ ██╔══╝  ██╔══██╗
██████╔╝██║  ██║██║██║     ██║     ███████╗██║  ██║
╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝
                                            {Fore.GREEN + VERSION + Fore.RESET}

It is the end user's responsibility to obey all applicable laws.
It is just like a server testing script and Your IP is visible.

Please, make sure you are ANONYMOUS!
    ''')


###############################################
# Input parser, Logo, Help messages
###############################################


def print_usage(parser):
    """Wrapper for Logo with help."""
    print_logo()
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
