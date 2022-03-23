import pytest

from ripper.actions.udp_flood import UdpFlood
from ripper.context.context import Context

test_target = ('localhost', 80)


class DescribeUdpFloodAttackMethod:
    def it_has_correct_name(self):
        ctx = Context(args=None)
        udp_flood_am = UdpFlood(test_target, ctx)
        assert udp_flood_am.name == 'UDP Flood'
        assert udp_flood_am.label == 'udp-flood'

# TODO Add more tests