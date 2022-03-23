import os
from ripper.common import Singleton, strip_lines, read_file_lines_fs


def get_headers_dict(raw_headers: list[str]):
    """Set headers for the request"""
    headers_dict = {}
    for line in raw_headers:
        parts = line.split(':')
        headers_dict[parts[0]] = parts[1].strip()

    return headers_dict


class HeadersProvider(metaclass=Singleton):
    def __init__(self):
        self.refresh()

    def refresh(self):
        self.user_agents = strip_lines(read_file_lines_fs(os.path.dirname(__file__) + '/assets/user_agents.txt'))
        self.raw_headers = strip_lines(read_file_lines_fs(os.path.dirname(__file__) + '/assets/headers.txt'))
        self.headers = get_headers_dict(self.raw_headers)
