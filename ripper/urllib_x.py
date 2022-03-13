import sys
import re
import random
import ssl
from urllib.parse import urlparse
from operator import itemgetter
from ripper.proxy import Sock5Proxy
from ripper.sockets import SocketManager


###############################################
# Common methods for network methods
###############################################
def build_headers_string_from_dict(headers_dict) -> str:
  return '\n'.join([f'{key}: {value}' for (key, value) in headers_dict.items()])


def build_request_http_package(host, headers = None, extra_data = None) -> str:
  packet_txt = f'GET / HTTP/1.1' \
               f'\nHost: {host}'
  if headers and len(headers.items()):
    packet_txt += f'\n\n{build_headers_string_from_dict(headers)}'
  if extra_data:
      packet_txt += f'\n\n{extra_data}'
  return packet_txt.encode('utf-8')


###############################################
# Network methods
###############################################
class Response:
  def __init__(self, status: int, full_response: str):
    self.status = status
    self.full_response = full_response


def default_scheme_port(scheme: str):
  if scheme == 'http':
    return 80
  if scheme == 'https':
    return 443
  return None


def http_request(url: str, user_agents = None, headers = {}, extra_data = None, read_resp_size = 32, http_method: str = 'GET', proxy: Sock5Proxy = None):
  url_data = urlparse(url)
  hostname = url_data.hostname
  port = url_data.port if url_data.port is not None else default_scheme_port(url_data.scheme)
  client = SocketManager.create_http_socket(proxy)

  if url_data.scheme == 'https':
    context = ssl.create_default_context()
    client = context.wrap_socket(client, server_hostname=hostname)

  if user_agents:
    headers['User-Agent'] = random.choice(user_agents)

  client.connect((hostname, port))
  request_packet = build_request_http_package(
    host=f'{hostname}',
    headers=headers,
    extra_data=extra_data,
  )
  client.send(request_packet)
  # 32 chars is enough to get status code
  http_response = repr(client.recv(read_resp_size))
  status = int(re.search(r" (\d+) ", http_response)[1])
  return Response(
    status=status,
    full_response=http_response,
  )
