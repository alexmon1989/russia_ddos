import pytest
from collections import namedtuple

from ripper.actions.udp_flood import UdpFlood
from ripper.context.context import Context

Args = namedtuple('Args', 'targets threads_count')


class DescribeTcpFloodAttackMethod:
    def it_has_correct_name(self):
        args = Args(
            targets=['udp://localhost'],
            threads_count=100,
        )
        ctx = Context(args)
        ctx.__init__(args)
        tcp_flood_am = UdpFlood(ctx.targets_manager.targets[0], ctx)
        assert tcp_flood_am.name == 'UDP Flood'
        assert tcp_flood_am.label == 'udp-flood'

# TODO Add more tests
