import pytest
from collections import namedtuple

from ripper.actions.udp_flood import UdpFlood
from ripper.context.context import Context

Args = namedtuple('Args', 'targets')


class DescribeTcpFloodAttackMethod:
    def it_has_correct_name(self):
        ctx = Context(args=Args(
            targets=['udp://localhost'],
        ))
        tcp_flood_am = UdpFlood(ctx, ctx.targets[0])
        assert tcp_flood_am.name == 'UDP Flood'
        assert tcp_flood_am.label == 'udp-flood'

# TODO Add more tests
