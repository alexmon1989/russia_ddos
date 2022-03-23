import pytest

from ripper.actions.http_flood import HttpFlood
from ripper.context.context import Context
from ripper.context.target import Target
from ripper.headers_provider import HeadersProvider

test_target = Target('http://localhost')


class DescribeHttpFloodAttackMethod:
    def it_has_some_headers(self):
        ctx = Context(args=None)
        http_flood_am = HttpFlood(test_target, ctx)

        actual = http_flood_am.headers()
        assert actual.get('Content-Length') == '0'
        with_content = http_flood_am.headers('{"test": 1}')
        assert with_content.get('Content-Length') == '11'

    def it_has_payload(self):
        args = lambda: None
        args.target = 'http://localhost'
        args.http_method = 'POST'

        ctx = Context(args)
        ctx.headers_provider.user_agents = ['Mozilla/5.0 (Windows NT 6.3; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0']
        http_flood_am = HttpFlood(test_target, ctx)

        body = '{"test":1}'
        headers = '\r\n'.join([f'{key}: {value}' for (key, value) in http_flood_am.headers().items()])
        expected = 'POST / HTTP/1.1\r\nHost: localhost\r\n' + headers + '\r\n\r\n'

        payload = http_flood_am.payload()
        assert payload.split('\r\n') == expected.split('\r\n')

        payload_with_body = http_flood_am.payload(body)
        headers_with_body = '\r\n'.join([f'{key}: {value}' for (key, value) in http_flood_am.headers(body).items()])
        expected_with_body = 'POST / HTTP/1.1\r\nHost: localhost\r\n' + headers_with_body + '\r\n' + f'{body}\r\n\r\n'
        assert payload_with_body.split('\r\n') == expected_with_body.split('\r\n')

    def it_has_correct_name(self):
        ctx = Context(args=None)
        http_flood_am = HttpFlood(test_target, ctx)
        assert http_flood_am.name == 'HTTP Flood'
        assert http_flood_am.label == 'http-flood'

    @pytest.fixture(scope='session', autouse=True)
    def refresh_headers_provider(self):
        HeadersProvider().refresh()
