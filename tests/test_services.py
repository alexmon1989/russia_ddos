import pytest as pytest
import time
from collections import namedtuple

from ripper.context.context import Context
from ripper.context.errors import Error
from ripper.constants import *
from ripper.services import check_successful_tcp_attack, check_successful_connections, \
    no_successful_connections_error_msg

Args = namedtuple('Args', 'target')


class DescribeServices:
    args: Args = Args(
        target='http://localhost'
    )

    def it_checks_successful_tcp_attack(self):
        context = Context(self.args)
        init_check_time = time.time_ns() - (200 * 1000000 * 1000)
        context.target.statistic.packets.connections_check_time = init_check_time
        context.target.statistic.start_time = None
        uuid = Error('Check TCP attack', NO_SUCCESSFUL_CONNECTIONS_VPN_ERR_MSG).uuid

        # Case when no attack
        assert check_successful_tcp_attack(context) is False
        assert context.target.statistic.packets.connections_check_time == init_check_time
        assert context.target.statistic.packets.total_sent == 0
        assert context.target.statistic.packets.total_sent_prev == 0
        assert len(context.errors) == 1
        assert context.errors[uuid].code == 'Check TCP attack'
        assert context.errors[uuid].count == 1
        assert context.errors[uuid].message == NO_SUCCESSFUL_CONNECTIONS_VPN_ERR_MSG

        # Case when we have successful attack after some failed attacks
        context.target.statistic.packets.total_sent = 100
        context.target.statistic.packets.total_sent_prev = 1

        assert check_successful_tcp_attack(context) is True
        assert context.target.statistic.packets.connections_check_time > init_check_time
        assert context.target.statistic.packets.total_sent == context.target.statistic.packets.total_sent_prev
        assert context.target.statistic.packets.total_sent == 100
        assert len(context.errors) == 0

    def it_checks_successful_connections(self):
        context = Context(self.args)
        init_check_time = time.time_ns() - (200 * 1000000 * 1000)
        context.target.statistic.connect.last_check_time = init_check_time
        context.target.statistic.start_time = None
        uuid = Error('Check connection', no_successful_connections_error_msg(context)).uuid

        # Checks if there are no successful connections more than SUCCESSFUL_CONNECTIONS_CHECK_PERIOD sec
        assert check_successful_connections(context) is False
        assert context.target.statistic.connect.last_check_time == init_check_time
        assert context.target.statistic.connect.success == 0
        assert context.target.statistic.connect.success_prev == 0
        assert len(context.errors) == 1
        assert context.errors[uuid].code == 'Check connection'
        assert context.errors[uuid].count == 1
        assert context.errors[uuid].message == NO_SUCCESSFUL_CONNECTIONS_VPN_ERR_MSG

        # Checks if we have successful connections after connections fail
        context.target.statistic.connect.success = 1

        assert check_successful_connections(context) is True
        assert context.target.statistic.connect.last_check_time > init_check_time
        assert context.target.statistic.connect.success == 1
        assert context.target.statistic.connect.success_prev == 1
        assert len(context.errors) == 0
