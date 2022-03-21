import pytest

from ripper.actions.tcp_flood import TcpFlood
from ripper.context import Context

test_target = ('localhost', 80)


def test_name():
    ctx = Context(args=None)
    tcp_flood_am = TcpFlood(test_target, ctx)
    assert tcp_flood_am.name == 'TCP Flood'

# TODO Add more tests