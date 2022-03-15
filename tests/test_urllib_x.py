import re
import pytest as pytest
from ripper.urllib_x import http_request, build_headers_string_from_dict, build_request_http_package
from ripper.context import Context


@pytest.mark.parametrize('url, status', [
    ('http://google.com/', 301),
    ('https://www.google.com/', 200),
])
def test_http_request(url, status):
    _ctx = Context()
    response = http_request(
        url=url,
        headers=_ctx.headers,
    )
    assert response.status == status


@pytest.mark.parametrize('headers_dict, headers_txt', [
    ({
        'User-Agent': 'Mozilla/5.0 (Mobile; rv:32.0) Gecko/32.0 Firefox/32.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'X-ray': '7584398yfugahews8',
    }, 'User-Agent: Mozilla/5.0 (Mobile; rv:32.0) Gecko/32.0 Firefox/32.0\n'
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\n'
        'X-ray: 7584398yfugahews8'),
    ({}, ''),
])
def test_build_headers_string_from_dict(headers_dict, headers_txt):
    actual = build_headers_string_from_dict(headers_dict)
    assert actual == headers_txt


@pytest.mark.parametrize('args, http_package', [
    ({
        'host': 'google.com',
        'http_method': 'POST',
        'headers': {'row1': 'xyz', 'row2': 'ijk'},
        'extra_data': 'Hello',
    }, 'POST / HTTP/1.1'
       '\nHost: google.com'
       '\n\nrow1: xyz'
       '\nrow2: ijk'
       '\nContent-Length: 5'
       '\n\nHello'
    ),
    ({
        'host': 'google.com',
        'http_method': 'POST',
        'headers': {'row1': 'xyz', 'row2': 'ijk'},
        'extra_data': 'Hello',
        'is_content_length_header': False,
    }, 'POST / HTTP/1.1'
       '\nHost: google.com'
       '\n\nrow1: xyz'
       '\nrow2: ijk'
       '\n\nHello'
    ),
    ({
        'host': 'google.com',
        'headers': {'row1': 'xyz', 'row2': 'ijk'},
        'extra_data': 'Hello',
    }, 'GET / HTTP/1.1'
       '\nHost: google.com'
       '\n\nrow1: xyz'
       '\nrow2: ijk'
       '\nContent-Length: 5'
       '\n\nHello'
    ),
    ({
        'host': 'google.com',
        'headers': {'row1': 'xyz', 'row2': 'ijk'},
    }, 'GET / HTTP/1.1'
       '\nHost: google.com'
       '\n\nrow1: xyz'
       '\nrow2: ijk'
    ),
    ({
        'host': 'google.com',
    }, 'GET / HTTP/1.1'
       '\nHost: google.com'
    ),
    ({
        'host': 'google.com',
        'path': '/hello',
    }, 'GET /hello HTTP/1.1'
       '\nHost: google.com'
    ),
])
def test_build_request_http_package(args, http_package):
    actual = build_request_http_package(**args)
    assert actual == http_package.encode('utf-8')
