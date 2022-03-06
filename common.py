import string
import random
import math
import os
import subprocess
import json
import sys
import urllib.request
from functools import lru_cache
from constants import (GETTING_SERVER_IP_ERROR_MSG, NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG, DEFAULT_CURRENT_IP_VALUE,
                       VERSION)


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


@lru_cache(maxsize=None)
def get_server_ip_error_msg() -> str:
    return red_txt(GETTING_SERVER_IP_ERROR_MSG)


@lru_cache(maxsize=None)
def get_no_successfull_connection_error_msg() -> str:
    return red_txt(NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG)


def readfile(filename: str):
    """Read file into list."""
    file = open(filename, 'r')
    content = file.readlines()
    file.close()

    return content


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
