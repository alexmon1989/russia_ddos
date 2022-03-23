import pytest

from ripper.actions.tcp_flood import TcpFlood
from ripper.context.context import Context

test_target = ('localhost', 80)


class DescribeTcpFloodAttackMethod:
    def it_has_correct_name(self):
        ctx = Context(args=None)
        tcp_flood_am = TcpFlood(test_target, ctx)
        assert tcp_flood_am.name == 'TCP Flood'
        assert tcp_flood_am.label == 'tcp-flood'

# TODO Add more tests
