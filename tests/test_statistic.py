import pytest as pytest

from ripper import statistic


class DescribeStatistic:
    @pytest.mark.parametrize('actual, expected', [
        (0,  '[red]0[default]'),
        (15, '[red]15[default]'),
        (35, '[dark_orange]35[default]'),
        (55, '[orange1]55[default]'),
        (65, '[orange1]65[default]'),
        (75, '[yellow4]75[default]'),
        (85, '[yellow4]85[default]'),
        (95, '[green1]95[default]'),
    ])
    def it_applies_different_colors_depending_on_rate(self, actual, expected):
        assert statistic.rate_color(actual) == expected

    def it_builds_http_codes_distribution(self):
        http_status_codes = {
            200: 1,
            300: 2,
            400: 10,
            500: 2,
            429: 3,
        }
        actual = statistic.build_http_codes_distribution(http_status_codes)
        assert actual == '200: 6%, 300: 11%, 400: 56%, 429: 17%, 500: 11%'
