import pytest as pytest
import time

from ripper.errors import *
from ripper.constants import *
from ripper.context.target import Target

class DescribeServices:
    target_uri: str = 'http://localhost'

    def it_checks_successful_tcp_attack(self):
        target = Target(target_uri=self.target_uri)
        init_check_time = time.time_ns() - (200 * 1000000 * 1000)
        target.statistic.packets.connections_check_time = init_check_time
        target.statistic.start_time = None
        uuid = CheckTcpAttackError(message=NO_SUCCESSFUL_CONNECTIONS_ERR_MSG).uuid

        # Case when no attack
        assert target.check_successful_tcp_attack() is False
        assert target.statistic.packets.connections_check_time == init_check_time
        assert target.statistic.packets.total_sent == 0
        assert target.statistic.packets.total_sent_prev == 0
        assert len(target.errors_manager.errors) == 1
        assert target.errors_manager.errors[uuid].code == 'Check TCP attack'
        assert target.errors_manager.errors[uuid].count == 1
        assert target.errors_manager.errors[uuid].message == NO_SUCCESSFUL_CONNECTIONS_ERR_MSG

        # Case when we have successful attack after some failed attacks
        target.statistic.packets.total_sent = 100
        target.statistic.packets.total_sent_prev = 1

        assert target.check_successful_tcp_attack() is True
        assert target.statistic.packets.connections_check_time > init_check_time
        assert target.statistic.packets.total_sent == target.statistic.packets.total_sent_prev
        assert target.statistic.packets.total_sent == 100
        assert len(target.errors_manager.errors) == 0

    def it_checks_successful_connections(self):
        target = Target(target_uri=self.target_uri)
        init_check_time = time.time_ns() - (200 * 1000000 * 1000)
        target.statistic.connect.last_check_time = init_check_time
        target.statistic.start_time = None
        uuid = CheckConnectionError().uuid

        # Checks if there are no successful connections more than SUCCESSFUL_CONNECTIONS_CHECK_PERIOD sec
        assert target.check_successful_connections() is False
        assert target.statistic.connect.last_check_time == init_check_time
        assert target.statistic.connect.success == 0
        assert target.statistic.connect.success_prev == 0
        assert len(target.errors_manager.errors) == 1
        assert target.errors_manager.errors[uuid].code == 'Check connection'
        assert target.errors_manager.errors[uuid].count == 1
        assert target.errors_manager.errors[uuid].message == NO_SUCCESSFUL_CONNECTIONS_ERR_MSG

        # Checks if we have successful connections after connections fail
        target.statistic.connect.success = 1

        assert target.check_successful_connections() is True
        assert target.statistic.connect.last_check_time > init_check_time
        assert target.statistic.connect.success == 1
        assert target.statistic.connect.success_prev == 1
        assert len(target.errors_manager.errors) == 0
