import pytest as pytest

from ripper.stats.utils import build_http_codes_distribution, rate_color


class DescribeStatistic:
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
    def it_applies_different_colors_depending_on_rate(self, actual, expected):
        assert rate_color(actual) == expected

    def it_builds_http_codes_distribution(self):
        http_status_codes = {
            200: 1,
            300: 2,
            400: 10,
            500: 2
        }
        actual = build_http_codes_distribution(http_status_codes)
        assert actual == '200: 7%, 300: 13%, 400: 67%, 500: 13%'
