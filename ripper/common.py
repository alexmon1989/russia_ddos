import datetime
import gzip
import http.client
import re
import socket
import string
import random
import os
import subprocess
import json
import urllib.request

from rich import box
from rich.console import Console
from rich.panel import Panel

from ripper.constants import *

Target = 'Target'


# Prepare static patterns once at start.
IPv4_PATTERN = re.compile(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$")

console = Console()


def read_file_lines(filename: str) -> list[str]:
    """Read string from fs or http"""
    if filename.startswith('http'):
        return read_file_lines_http(filename)
    return read_file_lines_fs(filename)


def read_file_lines_fs(filename: str) -> list[str]:
    """Read string from file"""
    with open(filename, 'r') as file:
        return file.readlines()


def read_file_lines_http(url: str) -> list[str]:
    """Read string from http"""
    data = data = requests.get(url, timeout=30).text
    return data.splitlines()


def strip_lines(lines: list[str]) -> list[str]:
    return list(map(lambda line: line.strip(), lines))


def generate_random_bytes(min_len: int, max_len: int) -> bytes:
    """Generate random packet bytes."""
    # No need to generate random int if we max_len = min_len
    if min_len == max_len:
        return generate_fixed_size_random_bytes(max_len)
    return generate_fixed_size_random_bytes(random.randint(min_len, max_len))


def generate_fixed_size_random_bytes(len: int) -> bytes:
    """Generate random packet bytes."""
    return random.randbytes(len)


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


def ns2s(time_nano: int):
    return time_nano / 1000000 / 1000


def s2ns(time_seconds: int):
    return int(time_seconds * 1000000 * 1000)


def format_dt(dt: datetime, fmt=DATE_TIME_FULL) -> str:
    """Convert datetime to string using specified format pattern."""
    if dt is None:
        return ''
    return dt.strftime(fmt)


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
    """Gets country of the target's IPv4."""
    if host_ip is None or not is_ipv4(host_ip):
        return GEOIP_NOT_DEFINED

    country = GEOIP_NOT_DEFINED
    try:
        # Sometimes ends up in HTTP Error 429: Too Many Requests
        # TODO support multiple services
        response_body = urllib.request.urlopen(f'https://ipinfo.io/{host_ip}', timeout=3).read().decode('utf8')
        response_data = json.loads(response_body)
        country = response_data['country']
    except:
        pass

    return country


def detect_cloudflare(uri: str):
    """Check response and detect if the host protected by CloudFlare."""
    parsed_uri = urllib.request.urlparse(uri)
    domain = '{uri.netloc}'.format(uri=parsed_uri)
    scheme = '{uri.scheme}'.format(uri=parsed_uri)

    check = http.client.HTTPSConnection(domain, timeout=3) if scheme == 'https' \
        else http.client.HTTPConnection(domain, timeout=3)

    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_4 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Mobile/12H143',
        'Origin': 'https://google.com',
        'Referer': f'https://www.google.com/search?q={domain}&sourceid=chrome&ie=UTF-8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Accept-Encoding': 'gzip,deflate',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
        'Connection': 'keep-alive',
        'Content-Type': 'text/html'
    }
    try:
        check.request(method='GET', url='/', headers=headers)
        gzipped = check.getresponse().read()
        response = gzip.decompress(gzipped).decode('utf-8')
        for tag in CLOUDFLARE_TAGS:
            if response.__contains__(tag):
                return True
    except:
        return False

    return False


def convert_size(size_bytes: int, units: str = 'B') -> str:
    """Converts size in bytes to human-readable format."""
    for x in ['', 'k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']:
        if size_bytes < 1024.: return '{0:3.2f} {1}{2}'.format(size_bytes, x, units)
        size_bytes /= 1024.
    return '{0:3.2f} P{1}'.format(size_bytes, units)


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


def print_panel(message: str, style: str = 'bold white on red') -> None:
    """Output message in the colorful box."""
    console.print(
        Panel(message, box=box.ROUNDED),
        width=MIN_SCREEN_WIDTH,
        style=style)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
