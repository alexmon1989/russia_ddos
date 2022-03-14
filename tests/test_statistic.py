import pytest as pytest

import ripper.statistic as statistic


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
