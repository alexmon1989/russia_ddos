import pytest as pytest
from datetime import datetime

from ripper.context.context import Context
from ripper.health_check_manager import classify_host_status, count_host_statuses
from ripper.constants import HOST_IN_PROGRESS_STATUS, HOST_FAILED_STATUS, HOST_SUCCESS_STATUS
from ripper.headers_provider import HeadersProvider
from ripper.arg_parser import Args


class DescribeHealthCheck:
    @pytest.mark.parametrize('value, status', [
        (None, HOST_IN_PROGRESS_STATUS),
        ([{'error': 'Connection timed out'}], HOST_FAILED_STATUS),
        ([{'address': '4.2.2.2', 'time': 0.040173}], HOST_SUCCESS_STATUS),
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
    def it_classifies_host_status(self, value, status):
        assert classify_host_status(value) == status

    @pytest.mark.parametrize('distribution, statuses_counter', [
        ({"at1.node.check-host.net": [{"address": "95.173.136.72","time": 0.067267}], "ch1.node.check-host.net": [{"address": "95.173.136.72","time": 0.080538}], "de4.node.check-host.net": [{"address": "95.173.136.72","time": 1.078855}], "ir1.node.check-host.net": [{'error': 'Connection timed out'}], "it2.node.check-host.net": [{"address": "95.173.136.71","time": 0.063825}], "md1.node.check-host.net": [{"address": "95.173.136.70","time": 0.159452}], "nl1.node.check-host.net": [{'error': 'Connection timed out'}], "us1.node.check-host.net": None, "us2.node.check-host.net": [{"address": "95.173.136.70","time": 0.13008}]},
        {'HOST_IN_PROGRESS': 1, 'HOST_FAILED': 2, 'HOST_SUCCESS': 6}),
        ({}, {}),
    ])
    def it_counts_host_statuses(self, distribution, statuses_counter):
        actual = count_host_statuses(distribution)
        assert len(actual) == len(statuses_counter)
        for (key, value) in statuses_counter.items():
            assert actual[key] == value

    # slow
    @pytest.mark.skip(reason="Use this test only for dev, it can fail because depends from external service.")
    def it_can_fetch_host_statuses(self):
        args = Args(
            # TODO expect target_uri in args as well
            targets=['https://httpbin.org'],
            threads_count=100,
        )
        context = Context(args)
        context.__init__(args)
        assert len(context.targets_manager.targets[0].host_ip) > 0

        health_check_manager = context.targets_manager.targets[0].health_check_manager

        before_execution = datetime.now()
        distribution = health_check_manager.update_host_statuses()
        after_execution = datetime.now()

        # some nodes have issues with file descriptor or connection
        assert distribution[HOST_SUCCESS_STATUS] > 17
        # state should be updated
        assert distribution == health_check_manager.host_statuses
        assert not health_check_manager.is_in_progress
        assert health_check_manager.last_host_statuses_update >= before_execution
        assert health_check_manager.last_host_statuses_update <= after_execution

    @pytest.mark.parametrize('args_data, url', [
        ({'target_uri': 'https://google.com', 'health_check_method': 'http'}, 'https://check-host.net/check-http?host=google.com'),
        ({'target_uri': 'https://google.com', 'health_check_method': 'http'}, 'https://check-host.net/check-http?host=google.com'),
        ({'target_uri': 'http://google.com:92', 'health_check_method': 'http'}, 'https://check-host.net/check-http?host=google.com:92'),
        ({'target_uri': 'tcp://google.com:443', 'host_ip': '172.217.20.206', 'health_check_method': 'tcp'}, 'https://check-host.net/check-tcp?host=172.217.20.206:443'),
        ({'target_uri': 'udp://google.com:443', 'host_ip': '172.217.20.206', 'health_check_method': 'ping'}, 'https://check-host.net/check-ping?host=172.217.20.206'),
    ])
    def it_constructs_request_url(self, args_data, url):
        args = Args(
            # TODO expect target_uri in args as well
            targets=[args_data['target_uri']],
            threads_count=100,
        )
        context = Context(args)
        context.__init__(args)
        assert context.targets_manager.targets[0].health_check_manager.health_check_method == args_data['health_check_method']
        if 'host_ip' in args_data:
            context.targets_manager.targets[0].host_ip = args_data['host_ip']
        assert context.targets_manager.targets[0].health_check_manager.request_url == url

    @pytest.fixture(scope='session', autouse=True)
    def refresh_headers_provider(self):
        HeadersProvider().refresh()
