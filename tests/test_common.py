import pytest as pytest

from ripper.common import convert_size, is_my_ip_changed


class TestCommon:
    @pytest.mark.parametrize('actual, expected', [
        (0, '0.00 B'),
        (100, '100.00 B'),
        (1024, '1.00 kB'),
        (16384096, '15.63 MB'),
        (32256798429, '30.04 GB'),
        (620832256798429, '564.64 TB'),
    ])
    def test_convert_size(self, actual, expected):
        assert convert_size(actual) == expected

    def test_is_my_ip_changed(self):
        my_start_ip = '192.168.0.1'
        my_current_ip = '10.20.0.1'

        assert is_my_ip_changed(my_start_ip, my_current_ip) is True
        assert is_my_ip_changed(my_start_ip, my_start_ip) is False
