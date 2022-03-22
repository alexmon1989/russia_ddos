import os
from ripper.common import Singleton, strip_lines, read_file_lines_fs


def get_headers_dict(base_headers: list[str]):
    """Set headers for the request"""
    headers_dict = {}
    for line in base_headers:
        parts = line.split(':')
        headers_dict[parts[0]] = parts[1].strip()

    return headers_dict


class HeadersProvider(metaclass=Singleton):
    def __init__(self):
        self.user_agents = strip_lines(read_file_lines_fs(os.path.dirname(__file__) + '/useragents.txt'))
        self.base_headers = strip_lines(read_file_lines_fs(os.path.dirname(__file__) + '/headers.txt'))
        self.headers = get_headers_dict(self.base_headers)
