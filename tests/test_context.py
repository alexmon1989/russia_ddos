from datetime import datetime, timedelta
from collections import namedtuple
import time
import pytest as pytest

from ripper.context.context import Context

Args = namedtuple('Args', 'targets threads_count')


class DescribeContext:
    args: Args = Args(
        targets=['https://httpbin.org'],
        threads_count=100,
    )

    @pytest.mark.parametrize('actual_ip, expected_result', [
        ('127.0.0.1', '127.***.***.***'),
        ('42.199.100.200', '42.***.***.***'),
        ('42', '42'),
        # ('...detecting', '...detecting')
    ])
    def it_can_get_ip_masked(self, actual_ip, expected_result):
        context = Context(self.args)
        context.__init__(self.args)
        context.my_ip_info.start_ip = actual_ip
        assert context.my_ip_info.ip_masked == expected_result

    def it_checks_time_interval(self):
        context = Context(self.args)
        context.__init__(self.args)
        last_2mins = datetime.now() - timedelta(minutes=2)
        context.time_interval_manager._start_time = last_2mins

        assert datetime.now() > context.time_interval_manager.start_time
        assert context.time_interval_manager.check_timer_elapsed(5) is True
        assert context.time_interval_manager.check_timer_elapsed(5) is False
        time.sleep(2)
        assert context.time_interval_manager.check_timer_elapsed(5) is False
        assert context.time_interval_manager.check_timer_elapsed(1) is True

    @pytest.mark.parametrize('target_uri, attack_method', [
        ('http://google.com', 'http-flood'),
        ('tcp://google.com', 'tcp-flood'),
        ('udp://google.com', 'udp-flood'),
    ])
    def it_detects_attack_by_target_in_context(self, target_uri, attack_method):
        args = Args(
            targets=[target_uri],
            threads_count=100,
        )
        context = Context(args)
        # context is singleton now, so it should be reinitialized manually
        context.__init__(args)
        assert context.targets_manager.targets[0].attack_method == attack_method
