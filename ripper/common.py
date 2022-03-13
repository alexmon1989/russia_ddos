import datetime
import http.client
import ipaddress
import re
import socket
import string
import random
import os
import subprocess
import json
import sys
import urllib.request

from ripper.constants import *

# Prepare static patterns once at start.
IPv4_PATTERN = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$")


def get_no_successful_connection_die_msg() -> str:
    return f"There were no successful connections for more " \
           f"than {NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC // 60} minutes. " \
           f"Your attack is ineffective."


def readfile(filename: str) -> list[str]:
    """Read string from file"""
    with open(filename, 'r') as file:
        return file.readlines()


def get_random_string(len_from: int, len_to: int) -> str:
    """Random string with different length"""
    length = random.randint(len_from, len_to)
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str


def get_current_ip() -> str:
    """Gets user IP with external service."""
    current_ip = DEFAULT_CURRENT_IP_VALUE
    try:
        # Check if curl exists in Linux/macOS
        rc = subprocess.call(['which', 'curl'], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) if os.name == 'posix' else 1
        current_ip = os.popen('curl -s ifconfig.me').readline() \
            if rc == 0 else urllib.request.urlopen('https://ifconfig.me').read().decode('utf8')
    except:
        pass

    return current_ip if is_ipv4(current_ip) else DEFAULT_CURRENT_IP_VALUE


def format_dt(dt: datetime, fmt=DATE_TIME_FULL) -> str:
    """Convert datetime to string using specified format pattern."""
    if dt is None:
        return ''
    return dt.strftime(fmt)


def is_my_ip_changed(my_start_ip: str, my_current_ip: str) -> bool:
    """Check if my IPv4 starting address wasn't changed during script run."""
    return my_start_ip != my_current_ip


def is_ipv4(ip: str) -> bool:
    """Check if specified string - is IPv4 format."""
    match = re.match(IPv4_PATTERN, ip)

    return bool(match)


def get_ipv4(host: str) -> str:
    """Get target IPv4 address by domain name."""
    if is_ipv4(host):
        return host  # do not use socket if we already have a valid IPv4

    try:
        host_ip = socket.gethostbyname(host)
        if is_ipv4(host_ip):
            return host_ip
    except:
        pass
    else:
        return DEFAULT_CURRENT_IP_VALUE


def get_country_by_ipv4(host_ip: str) -> str:
    """Gets country of the target's IPv4"""
    if host_ip is None or not is_ipv4(host_ip):
        return GEOIP_NOT_DEFINED

    country = GEOIP_NOT_DEFINED
    try:
        response_body = urllib.request.urlopen(f'https://ipinfo.io/{host_ip}', timeout=1).read().decode('utf8')
        response_data = json.loads(response_body)
        country = response_data['country']
    except:
        pass

    return country


def isCloudFlareProtected(link: str, user_agents: list) -> bool:
    """Check if the site is under CloudFlare protection."""

    parsed_uri = urllib.request.urlparse(link)
    domain = "{uri.netloc}".format(uri=parsed_uri)
    try:
        origin = socket.gethostbyname(domain)
        conn = http.client.HTTPSConnection('www.cloudflare.com', timeout=1)
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
    """Converts size in bytes to human-readable format."""
    for x in ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']:
        if size_bytes < 1024.: return "%3.2f %sB" % (size_bytes, x)
        size_bytes /= 1024.
    return "%3.2f PB" % size_bytes


def get_cpu_load() -> str:
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
# Input parser, Logo, Help messages
###############################################


def print_usage(parser):
    """Wrapper for Logo with help."""
    print(LOGO_NOCOLOR)
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
                      help='Attack method: udp (default), tcp, http')
    parser.add_option('-s', '--server',
                      dest='host',
                      help='Attack to server IP')
