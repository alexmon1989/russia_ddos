import sys
import pytest as pytest
from ripper.urllib_x import http_request, build_headers_string_from_dict
from ripper.context import Context

@pytest.mark.parametrize('url, status', [
    ('http://google.com/', 301),
    ('https://www.google.com/', 200),
])
def test_http_request(url, status):
  _ctx = Context()
  response = http_request(
    url=url,
    user_agents=_ctx.user_agents,
    headers=_ctx.headers,
  )
  assert response.status == status


@pytest.mark.parametrize('headers_dict, headers_txt', [
    ({
      'User-Agent': 'Mozilla/5.0 (Mobile; rv:32.0) Gecko/32.0 Firefox/32.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'X-ray': '7584398yfugahews8',
      }, 'User-Agent: Mozilla/5.0 (Mobile; rv:32.0) Gecko/32.0 Firefox/32.0\n' \
         'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\n' \
         'X-ray: 7584398yfugahews8'),
    ({}, ''),
])
def test_build_headers_string_from_dict(headers_dict, headers_txt):
  actual = build_headers_string_from_dict(headers_dict)
  assert actual == headers_txt