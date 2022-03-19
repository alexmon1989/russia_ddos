import pytest

from ripper.actions.HttpFlood import HttpFlood
from ripper.context import Context

test_target = ('localhost', 80)


class TestHttpFlood:
    def test_headers(self):
        ctx = Context(args=None)
        http = HttpFlood(test_target, ctx)

        actual = http.headers()
        assert actual.get('Content-Length') == '0'
        with_content = http.headers('{"test": 1}')
        assert with_content.get('Content-Length') == '11'

    def test_payload(self):
        args = lambda: None
        args.host = 'localhost'
        args.http_method = 'POST'

        ctx = Context(args)
        ctx.user_agents = ['Mozilla/5.0 (Windows NT 6.3; WOW64; rv:39.0) Gecko/20100101 Firefox/39.0']
        http = HttpFlood(test_target, ctx)

        body = '{"test":1}'
        headers = '\n'.join([f'{key}: {value}' for (key, value) in http.headers().items()])
        expected = 'POST / HTTP/1.1\nHost: localhost\n' + headers + '\n'

        payload = http.payload()
        assert payload.split('\n') == expected.split('\n')

        payload_with_body = http.payload(body)
        headers_with_body = '\n'.join([f'{key}: {value}' for (key, value) in http.headers(body).items()])
        expected_with_body = 'POST / HTTP/1.1\nHost: localhost\n' + headers_with_body + '\n' + f'{body}\n'
        assert payload_with_body.split('\n') == expected_with_body.split('\n')
