from ripper.constants import BADGE_WARN, BADGE_INFO, BADGE_ERROR


def badge(message: str, badge_template: str) -> str:
    """Create color badge with message using template."""
    return badge_template.format(message=message)


def badge_info(message: str) -> str:
    return badge(message, BADGE_INFO)


def badge_warn(message: str) -> str:
    return badge(message, BADGE_WARN)


def badge_error(message: str) -> str:
    return badge(message, BADGE_ERROR)


def rate_color(rate: int, units: str = '') -> str:
    """
    Get color schema for percentage value.
    Color schema looks like red-yellow-green scale for values 0-50-100.
    """
    color = '[red]'
    if 30 > rate > 20:
        color = '[orange_red1]'
    if 50 > rate > 30:
        color = '[dark_orange]'
    if 70 > rate > 50:
        color = '[orange1]'
    if 90 > rate > 70:
        color = '[yellow4]'
    if rate >= 90:
        color = '[green1]'

    return f'{color}{rate}{units}[/]'


def build_http_codes_distribution(http_codes_counter) -> str:
    codes_distribution = []
    total = sum(http_codes_counter.values())
    if not total:
        return '...detecting'
    for code in http_codes_counter.keys():
        count = http_codes_counter[code]
        percent = round(count * 100 / total)
        codes_distribution.append(f'{code}: {percent}%')
    return ', '.join(codes_distribution)


class Row:
    def __init__(self, label: str, value: str = '', visible: bool = True, end_section: bool = False):
        self.label = str(label)
        self.value = str(value)
        self.visible = visible
        self.end_section = end_section
