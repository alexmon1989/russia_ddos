import pytest
from collections import namedtuple

from ripper.actions.http_flood import HttpFlood
from ripper.context.context import Context
from ripper.headers_provider import HeadersProvider

Args = namedtuple('Args', 'targets http_method')


class DescribeHttpFloodAttackMethod:
    target_uri: str = 'tcp://localhost'

    def it_has_some_headers(self):
        args = Args(
            targets=[self.target_uri],
            http_method='GET',
        )
        ctx = Context(args)
        ctx.__init__(args)
        http_flood_am = HttpFlood(_ctx=ctx, target=ctx.targets[0])

        actual = http_flood_am.headers()
        assert actual.get('Content-Length') == '0'
        with_content = http_flood_am.headers('{"test": 1}')
        assert with_content.get('Content-Length') == '11'

    def it_has_payload(self):
        args = Args(
            targets=[self.target_uri],
            http_method='POST',
        )
        ctx = Context(args)
        ctx.__init__(args)
        ctx.headers_provider.user_agents = ['Mozilla/5.0 (Windows NT 6.3; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0']
        http_flood_am = HttpFlood(_ctx=ctx, target=ctx.targets[0])

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
        args = Args(
            targets=[self.target_uri],
            http_method='GET',
        )
        ctx = Context(args)
        ctx.__init__(args)
        http_flood_am = HttpFlood(target=ctx.targets[0], _ctx=ctx)
        assert http_flood_am.name == 'HTTP Flood'
        assert http_flood_am.label == 'http-flood'

    @pytest.fixture(scope='session', autouse=True)
    def refresh_headers_provider(self):
        HeadersProvider().refresh()
