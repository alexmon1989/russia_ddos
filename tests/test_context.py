from datetime import datetime, timedelta
from collections import namedtuple
import time
import pytest as pytest

from ripper.context.context import Context
from ripper.context.errors import Errors

Args = namedtuple('Args', 'target')


class DescribeContext:
    args: Args = Args(
        target='http://localhost'
    )

    def it_can_store_error_details(self):
        context = Context(self.args)
        context.errors.clear()

        actual = Errors(code='send UDP packet', message='Cannot get server ip')
        uuid = actual.uuid
        context.errors[uuid] = actual

        assert len(context.errors) == 1
        assert context.errors.get(uuid).code == 'send UDP packet'
        assert context.errors.get(uuid).count == 1
        assert context.errors.get(uuid).message == 'Cannot get server ip'

    def it_can_count_the_same_error(self):
        context = Context(self.args)
        context.errors.clear()

        assert len(context.errors) == 0

        actual = Errors(code='send UDP packet', message='Cannot get server ip')
        uuid = actual.uuid
        context.add_error(actual)

        assert len(context.errors) == 1
        assert context.errors.get(uuid) == actual
        assert context.errors.get(uuid).count == 1
        assert context.errors.get(uuid).code == 'send UDP packet'

        context.add_error(actual)
        assert len(context.errors) == 1
        assert context.errors.get(uuid).count == 2

    def it_can_delete_existing_error(self):
        context = Context(self.args)
        context.errors.clear()

        actual = Errors(code='send UDP packet', message='Cannot get server ip')
        uuid = actual.uuid
        context.add_error(actual)

        assert len(context.errors) == 1
        assert context.errors.get(uuid) == actual

        context.remove_error(uuid)
        assert len(context.errors) == 0

    @pytest.mark.parametrize('actual_ip, expected_result', [
        ('127.0.0.1', '127.*.*.*'),
        ('42.199.100.200', '42.*.*.*'),
        ('42', '42'),
        ('...detecting', '...detecting')
    ])
    def it_can_get_my_ip_masked(self, actual_ip, expected_result):
        context = Context(self.args)
        context.myIpInfo.my_start_ip = actual_ip
        assert context.myIpInfo.my_ip_masked() == expected_result

    def it_checks_time_interval(self):
        context = Context(self.args)
        last_2mins = datetime.now() - timedelta(minutes=2)
        context.target.statistic.start_time = last_2mins

        assert datetime.now() > context.target.statistic.start_time
        assert context.check_timer(5) is True
        assert context.check_timer(5) is False
        time.sleep(2)
        assert context.check_timer(5) is False
        assert context.check_timer(1) is True

    @pytest.mark.parametrize('target_str, attack_method', [
        ('http://google.com', 'http-flood'),
        ('tcp://google.com', 'tcp-flood'),
        ('udp://google.com', 'udp-flood'),
    ])
    def it_detects_attack_by_target_in_context(self, target_str, attack_method):
        assert Context(args=Args(
            target=target_str,
        )).target.attack_method == attack_method