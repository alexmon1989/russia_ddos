import re
import ssl

from urllib.parse import urlparse

from ripper.proxy import Sock5Proxy
from ripper.sockets import SocketManager
from ripper.common import get_random_user_agent
from ripper.constants import DEFAULT_HTTP_METHOD


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
        headers = {},
        extra_data: str = None,
        http_method: str = DEFAULT_HTTP_METHOD,
        is_random_user_agent: bool = True,
        is_content_length_header: bool = True) -> str:
    if not http_method:
        http_method = DEFAULT_HTTP_METHOD

    packet_txt = f'{http_method.upper()} {path} HTTP/1.1' \
                 f'\nHost: {host}'

    if is_random_user_agent and not check_headers_for_user_agent(headers):
        headers['User-Agent'] = get_random_user_agent()

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


def http_request(url: str, headers={}, extra_data=None, read_resp_size=32, http_method: str = None, proxy: Sock5Proxy = None):
    url_data = urlparse(url)
    hostname = url_data.hostname
    port = url_data.port if url_data.port is not None else default_scheme_port(
        url_data.scheme)
    path = url_data.path if url_data.path else '/'
    query = url_data.query if url_data.query else ''
    with SocketManager.create_http_socket(proxy) as client:
        if url_data.scheme == 'https':
            context = ssl.create_default_context()
            client = context.wrap_socket(client, server_hostname=hostname)

        client.connect((hostname, port))
        request_packet = build_request_http_package(
            host=f'{hostname}',
            headers=headers,
            extra_data=extra_data,
            http_method=http_method,
            path=(path if not query else f'{path}?{query}')
        )
        client.send(request_packet)
        # 32 chars is enough to get status code
        http_response = repr(client.recv(read_resp_size))
        status = int(re.search(r" (\d+) ", http_response)[1])
        return Response(
            status=status,
            full_response=http_response,
        )
