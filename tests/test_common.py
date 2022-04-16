import pytest as pytest
import time
import random

from ripper.common import convert_size, detect_cloudflare, generate_fixed_size_random_bytes, generate_random_bytes


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

    def it_can_check_cloudflare_protection(self):
        assert detect_cloudflare('https://www.thesfmarathon.com') is True

    def it_can_generate_fixed_size_random_sequence(self):
        b1 = generate_fixed_size_random_bytes(10)
        assert len(b1) == 10
        b2 = generate_fixed_size_random_bytes(10)
        assert len(b2) == 10
        assert b1 == b1
        assert b1 != b2
        start = time.time()
        for _ in range(1000):
            generate_fixed_size_random_bytes(65536)
        duration = time.time() - start
        # 1K packets per second
        assert duration < 1

    def it_can_generate_random_bytes(self):
        for _ in range(10):
            min_len = random.randint(1, 1000)
            max_len = min_len + random.randint(1, 1000)
            bt = generate_random_bytes(min_len, max_len)
            assert max_len >= len(bt) >= min_len

    def it_can_generate_random_bytes_with_empty_length(self):
        bt = generate_random_bytes(0, 0)
        assert not bt

    def it_can_generate_long_fixed_random_bytes(self):
        bt = generate_random_bytes(10000, 10000)
        assert len(bt) == 10000
