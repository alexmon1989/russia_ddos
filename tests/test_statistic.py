import datetime
import time

import pytest as pytest

from ripper import context, statistic


class TestStatistic:
    @pytest.mark.parametrize('actual, expected', [
        (0,  '[red]'),
        (15, '[red]'),
        (35, '[dark_orange]'),
        (55, '[orange1]'),
        (65, '[orange1]'),
        (75, '[yellow4]'),
        (85, '[yellow4]'),
        (95, '[green1]'),
    ])
    def test_rate_color(self, actual, expected):
        assert statistic.rate_color(actual) == expected

    def test_build_http_codes_distribution(self):
        http_status_codes = {
            200: 1,
            300: 2,
            400: 10,
            500: 2
        }
        actual = statistic.build_http_codes_distribution(http_status_codes)
        assert actual == '200: 1 (7%), 300: 2 (13%), 400: 10 (67%), 500: 2 (13%)'
