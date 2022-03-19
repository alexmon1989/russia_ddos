import pytest as pytest

from ripper.context import *
from ripper.constants import *
from ripper.services import check_successful_tcp_attack, check_successful_connections, \
    no_successful_connections_error_msg


class TestServices:
    def test_check_successful_tcp_attack(self):
        context = Context(args=None)
        init_check_time = time.time_ns() - (200 * 1000000 * 1000)
        context.Statistic.packets.connections_check_time = init_check_time
        context.Statistic.start_time = None
        uuid = Errors('Check TCP attack', NO_SUCCESSFUL_CONNECTIONS_ERROR_VPN_MSG).uuid

        # Case when no attack
        assert check_successful_tcp_attack(context) is False
        assert context.Statistic.packets.connections_check_time == init_check_time
        assert context.Statistic.packets.total_sent == 0
        assert context.Statistic.packets.total_sent_prev == 0
        assert len(context.errors) == 1
        assert context.errors[uuid].code == 'Check TCP attack'
        assert context.errors[uuid].count == 1
        assert context.errors[uuid].message == NO_SUCCESSFUL_CONNECTIONS_ERROR_VPN_MSG

        # Case when we have successful attack after some failed attacks
        context.Statistic.packets.total_sent = 100
        context.Statistic.packets.total_sent_prev = 1

        assert check_successful_tcp_attack(context) is True
        assert context.Statistic.packets.connections_check_time > init_check_time
        assert context.Statistic.packets.total_sent == context.Statistic.packets.total_sent_prev
        assert context.Statistic.packets.total_sent == 100
        assert len(context.errors) == 0

    def test_check_successful_connections(self):
        context = Context(args=None)
        init_check_time = time.time_ns() - (200 * 1000000 * 1000)
        context.Statistic.connect.last_check_time = init_check_time
        context.Statistic.start_time = None
        uuid = Errors('Check connection', no_successful_connections_error_msg(context)).uuid

        # Checks if there are no successful connections more than SUCCESSFUL_CONNECTIONS_CHECK_PERIOD sec
        assert check_successful_connections(context) is False
        assert context.Statistic.connect.last_check_time == init_check_time
        assert context.Statistic.connect.success == 0
        assert context.Statistic.connect.success_prev == 0
        assert len(context.errors) == 1
        assert context.errors[uuid].code == 'Check connection'
        assert context.errors[uuid].count == 1
        assert context.errors[uuid].message == NO_SUCCESSFUL_CONNECTIONS_ERROR_VPN_MSG

        # Checks if we have successful connections after connections fail
        context.Statistic.connect.success = 1

        assert check_successful_connections(context) is True
        assert context.Statistic.connect.last_check_time > init_check_time
        assert context.Statistic.connect.success == 1
        assert context.Statistic.connect.success_prev == 1
        assert len(context.errors) == 0
