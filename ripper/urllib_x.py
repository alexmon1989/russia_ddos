import re
import ssl
import socks
import socket
from urllib.parse import urlparse

from ripper.proxy import Sock5Proxy


###############################################
# Common methods for network methods
###############################################
def build_headers_string_from_dict(headers_dict) -> str:
    return '\n'.join([f'{key}: {value}' for (key, value) in headers_dict.items()])


def check_headers_for_user_agent(headers):
    if not isinstance(headers, dict):
        return False
    header_names = set(k.lower() for k in headers)
    return 'user-agent' in header_names


def build_request_http_package(
        host: str,
        path: str = '/',
        headers={},
        extra_data: str = None,
        http_method: str = None,
        is_content_length_header: bool = True) -> bytes:
    # redefinition is required to support bad argument propagation from http_request
    if not http_method:
        http_method = 'GET'

    packet_txt = f'{http_method.upper()} {path} HTTP/1.1' \
                 f'\nHost: {host}'

    if is_content_length_header and extra_data:
        headers['Content-Length'] = len(extra_data.encode('utf-8'))

    if headers and len(headers.items()):
        packet_txt += f'\n\n{build_headers_string_from_dict(headers)}'

    if extra_data:
        packet_txt += f'\n\n{extra_data}'

    return packet_txt.encode('utf-8')


def default_scheme_port(scheme: str):
    if scheme == 'http':
        return 80
    if scheme == 'https':
        return 443
    return None


###############################################
# Network methods
###############################################
class Response:
    def __init__(self, status: int, full_response: str):
        self.status = status
        self.full_response = full_response


def create_http_socket(proxy: Sock5Proxy = None, socket_timeout: int = None) -> socket:
    """Returns http socket."""
    http_socket = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
    proxy.decorate_socket(http_socket) if proxy is not None else 0
    http_socket.settimeout(socket_timeout) if socket_timeout is not None else 0

    return http_socket


def http_request(url: str, headers={}, extra_data=None, read_resp_size=32, http_method: str = None, proxy: Sock5Proxy = None, socket_timeout: int = None):
    url_data = urlparse(url)
    hostname = url_data.hostname
    scheme = url_data.scheme
    port = url_data.port if url_data.port is not None else default_scheme_port(scheme)
    path = url_data.path if url_data.path else '/'
    query = url_data.query if url_data.query else ''
    request_packet = build_request_http_package(
        host=hostname,
        headers=headers,
        extra_data=extra_data,
        http_method=http_method,
        path=(path if not query else f'{path}?{query}')
    )
    with create_http_socket(proxy=proxy, socket_timeout=socket_timeout) as http_socket:
        http_socket.connect((hostname, port))
        if scheme == 'https':
            context = ssl.create_default_context()
            # context.check_hostname = False
            # context.verify_mode = ssl.CERT_NONE
            http_socket = context.wrap_socket(
                http_socket,
                server_hostname=hostname,
            )
        http_socket.send(request_packet)
        # 32 chars is enough to get status code
        http_response = repr(http_socket.recv(read_resp_size))
        status = int(re.search(r" (\d+) ", http_response)[1])
        return Response(
            status=status,
            full_response=http_response,
        )
