import pytest as pytest

from ripper.context.target import Target


class DescribeTarget:
    def it_can_validate_connection_status(self):
        stat = Target(target_uri='http://google.com')

        assert stat.validate_connection(120) is True
        assert stat.validate_connection(-3600) is False
