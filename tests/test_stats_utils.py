import pytest as pytest

from ripper.stats.utils import build_http_codes_distribution, rate_color


class DescribeStatsUtils:
    @pytest.mark.parametrize('actual, expected', [
        (0,  '[red]0[/]'),
        (15, '[red]15[/]'),
        (35, '[dark_orange]35[/]'),
        (55, '[orange1]55[/]'),
        (65, '[orange1]65[/]'),
        (75, '[yellow4]75[/]'),
        (85, '[yellow4]85[/]'),
        (95, '[green1]95[/]'),
    ])
    def it_applies_different_colors_depending_on_rate(self, actual, expected):
        assert rate_color(actual) == expected

    def it_builds_http_codes_distribution(self):
        http_status_codes = {
            200: 1,
            300: 2,
            400: 10,
            429: 3,
            500: 2,
        }
        actual = build_http_codes_distribution(http_status_codes)
        assert actual == '200: 6%, 300: 11%, 400: 56%, 429: 17%, 500: 11%'
