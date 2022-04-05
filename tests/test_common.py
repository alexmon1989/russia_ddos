import pytest as pytest

from ripper.common import convert_size


class DescribeCommonMethods:
    @pytest.mark.parametrize('actual, expected', [
        (0, '0.00 B'),
        (100, '100.00 B'),
        (1024, '1.00 kB'),
        (16384096, '15.63 MB'),
        (32256798429, '30.04 GB'),
        (620832256798429, '564.64 TB'),
        (620832256798429256, '551.41 PB'),
    ])
    def it_has_convert_size(self, actual, expected):
        assert convert_size(actual) == expected

    @pytest.mark.parametrize('actual, units, expected', [
        (1024, 'B/s', '1.00 kB/s'),
        (1024, 'Bps', '1.00 kBps'),
        (16384096, 'B/s', '15.63 MB/s')
    ])
    def it_has_convert_size_with_units(self, actual, units, expected):
        assert convert_size(actual, units) == expected
