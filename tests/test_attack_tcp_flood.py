import pytest

from ripper.actions.tcp_flood import TcpFlood
from ripper.context.context import Context
from ripper.arg_parser import Args


class DescribeTcpFloodAttackMethod:
    def it_has_correct_name(self):
        args = Args(
            targets=['tcp://localhost'],
            threads_count=100,
        )
        ctx = Context(args)
        ctx.__init__(args)
        tcp_flood_am = TcpFlood(ctx.targets_manager.targets[0], ctx)
        assert tcp_flood_am.name == 'TCP Flood'
        assert tcp_flood_am.label == 'tcp-flood'

# TODO Add more tests
