import sys
import pytest as pytest
from ripper.health_check import classify_host_status, count_host_statuses, fetch_host_statuses
from ripper.constants import HOST_IN_PROGRESS_STATUS, HOST_FAILED_STATUS, HOST_SUCCESS_STATUS
from ripper.context import Context
from ripper.services import update_host_ip


def construct_context(host: str, attack_method: str, port: int = 80):
    _ctx = Context()
    _ctx.host = host
    _ctx.attack_method = attack_method
    _ctx.port = port
    update_host_ip(_ctx)
    return _ctx


# construct_context('google.com', 'udp', 53), {'HOST_SUCCESS': 17}
# construct_context('localhost', 'udp', 53), {'HOST_FAILED': 21}
# construct_context('google.com', 'http', 5000) {'HOST_FAILED': 21}
# construct_context('google.com', 'http', 80) {'HOST_SUCCESS': 17}
# construct_context('google.com', 'undefined', 80) {'HOST_SUCCESS': 21}
# construct_context('localhost', 'undefined', 80) {'HOST_SUCCESS': 21}
# construct_context('121.11.11.11', 'undefined', 80) {'HOST_FAILED': 21}

_ctx = construct_context('121.11.11.11', 'undefined', 80) #, {'HOST_SUCCESS': 17}
fetch_host_statuses(_ctx)