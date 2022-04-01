import pytest as pytest

from ripper.context.stats import PacketsStats


class DescribeStats:
    def it_can_validate_connection_status(self):
        stat = PacketsStats()

        assert stat.validate_connection(120) is True
        assert stat.validate_connection(-3600) is False
