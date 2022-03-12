import sys
import pytest as pytest
from ripper.urllib_x import http_request
from ripper.context import Context


def test_http_request():
  _ctx = Context()
  response = http_request(
    url='http://google.com/',
    user_agents=_ctx.user_agents,
    headers=_ctx.base_headers,
  )
  assert response.status == 301

def test_https_request():
  _ctx = Context()
  response = http_request(
    url='https://www.google.com/',
    user_agents=_ctx.user_agents,
    headers=_ctx.base_headers,
  )
  assert response.status == 200
