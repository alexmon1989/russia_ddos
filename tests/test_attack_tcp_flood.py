import pytest
from collections import namedtuple

from ripper.actions.tcp_flood import TcpFlood
from ripper.context.context import Context

Args = namedtuple('Args', 'target')


class DescribeTcpFloodAttackMethod:
    def it_has_correct_name(self):
        ctx = Context(args=Args(
            target='tcp://localhost',
        ))
        tcp_flood_am = TcpFlood(ctx, ctx.target)
        assert tcp_flood_am.name == 'TCP Flood'
        assert tcp_flood_am.label == 'tcp-flood'

# TODO Add more tests
