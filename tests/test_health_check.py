import sys
import pytest as pytest
from ripper.health_check import classify_host_status, count_host_statuses, fetch_host_statuses, construct_request_url
from ripper.constants import HOST_IN_PROGRESS_STATUS, HOST_FAILED_STATUS, HOST_SUCCESS_STATUS
from ripper.context import Context
from ripper.services import update_host_ip


@pytest.mark.parametrize('value, status', [
    (None, HOST_IN_PROGRESS_STATUS),
    ([{'error': 'Connection timed out'}], HOST_FAILED_STATUS),
    ([{'address': '4.2.2.2', 'time': 0.040173 }], HOST_SUCCESS_STATUS),
    ([{'address': '172.217.20.206', 'timeout': 1}], HOST_SUCCESS_STATUS),
    ([{'address': '172.217.20.206', 'error': 'Exiting subroutine via redo at /usr/local/share/perl/5.24.1/AnyEvent/Handle/UDP.pm line 246.\n', 'time': 0.000176}], HOST_FAILED_STATUS),
    ([[1, 0.103471040725708, 'Moved Permanently', '301', '172.217.20.206']], HOST_SUCCESS_STATUS),
    ([[0, 0.000416994094848633, 'Bad file descriptor', None, None]], HOST_FAILED_STATUS),
    ([[['OK', 0.0316579341888428, '172.217.20.206'], ['OK', 0.0315918922424316], ['OK', 0.0318388938903809], ['OK', 0.0318410396575928]]], HOST_SUCCESS_STATUS),
    ([[['TIMEOUT', 3.00089383125305, '121.11.11.11'], ['TIMEOUT', 3.0002110004425], ['TIMEOUT', 3.00109696388245], ['TIMEOUT', 3.00079393386841]]], HOST_FAILED_STATUS),
    ([[['OK', 0.0316579341888428, '172.217.20.206'], ['OK', 0.0315918922424316], ['OK', 0.0318388938903809], ['TIMEOUT', 3.0318410396575928]]], HOST_SUCCESS_STATUS),
    ([[['OK', 0.0316579341888428, '172.217.20.206'], ['OK', 0.0315918922424316], ['TIMEOUT', 3.0318388938903809], ['TIMEOUT', 3.0318410396575928]]], HOST_SUCCESS_STATUS),
    ([[['OK', 0.0316579341888428, '172.217.20.206'], ['TIMEOUT', 3.0315918922424316], ['TIMEOUT', 3.0318388938903809], ['TIMEOUT', 3.0318410396575928]]], HOST_FAILED_STATUS),
])
def test_classify_host_status(value, status):
    assert classify_host_status(value) == status


@pytest.mark.parametrize('distribution, statuses_counter', [
    ({"at1.node.check-host.net": [{"address": "95.173.136.72","time": 0.067267}], "ch1.node.check-host.net": [{"address": "95.173.136.72","time": 0.080538}], "de4.node.check-host.net": [{"address": "95.173.136.72","time": 1.078855}], "ir1.node.check-host.net": [{'error': 'Connection timed out'}], "it2.node.check-host.net": [{"address": "95.173.136.71","time": 0.063825}], "md1.node.check-host.net": [{"address": "95.173.136.70","time": 0.159452}], "nl1.node.check-host.net": [{'error': 'Connection timed out'}], "us1.node.check-host.net": None, "us2.node.check-host.net": [{"address": "95.173.136.70","time": 0.13008}]},
     {'HOST_IN_PROGRESS': 1, 'HOST_FAILED': 2, 'HOST_SUCCESS': 6}),
    ({}, {}),
])
def test_count_host_statuses(distribution, statuses_counter):
    actual = count_host_statuses(distribution)
    assert len(actual) == len(statuses_counter)
    for (key, value) in statuses_counter.items():
        assert actual[key] == value


# slow
def test_fetch_host_statuses():
    _ctx = Context()
    _ctx.host = 'google.com'
    _ctx.health_check_method = 'tcp'
    update_host_ip(_ctx)
    assert len(_ctx.host_ip) > 0
    distribution = fetch_host_statuses(_ctx)
    # some nodes have issues with file descriptor or connection
    assert distribution[HOST_SUCCESS_STATUS] > 17


@pytest.mark.parametrize('context_data, url', [
    ({'host': 'google.com', 'port': 443, 'health_check_method': 'http'}, 'https://check-host.net/check-http?host=google.com'),
    ({'host': 'google.com', 'port': 92, 'health_check_method': 'http'}, 'https://check-host.net/check-http?host=google.com:92'),
    ({'host': 'google.com', 'host_ip': '172.217.20.206', 'port': 443, 'health_check_method': 'tcp'}, 'https://check-host.net/check-tcp?host=172.217.20.206:443'),
    ({'host': 'google.com', 'host_ip': '172.217.20.206', 'port': 443, 'health_check_method': 'ping'}, 'https://check-host.net/check-ping?host=172.217.20.206'),
])
def test_construct_request_url(context_data, url):
    _ctx = Context()
    for (key, value) in context_data.items():
        if key == 'host':
            _ctx.host = value
        elif key == 'host_ip':
            _ctx.host_ip = value
        elif key == 'port':
            _ctx.port = value
        elif key == 'health_check_method':
            _ctx.health_check_method = value
    assert construct_request_url(_ctx) == url
