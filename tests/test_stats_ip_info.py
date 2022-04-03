import pytest as pytest

from ripper.stats.ip_info import IpInfo


class DescribeIpInfo:
    def it_has_my_ip_changed(self):
        my_start_ip = '192.168.0.1'
        ii = IpInfo(my_start_ip)

        assert not ii.is_ip_changed()
        ii.current_ip = '10.20.0.1'
        assert ii.is_ip_changed()
