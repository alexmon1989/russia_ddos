import random
import threading
from typing import List

from ripper.common import read_file_lines
from ripper.proxy import Proxy, ProxyType
from ripper.constants import PROXY_MAX_FAILURE_RATIO, PROXY_MIN_VALIDATION_REQUESTS

lock = threading.Lock()


class ProxyManager:
    """Manager for proxy collection."""

    proxy_list: list[Proxy] = []
    """Active proxies."""
    proxy_list_initial_len: int = 0
    """Count of proxies during the last application."""
    __proxy_extract_counter: int = 0
    """Vacuum operation is called automatically on every PROXY_MIN_VALIDATION_REQUESTS proxy extractions"""
    proxy_type: ProxyType = ProxyType.SOCKS5
    """Type of proxy (SOCKS5, SOCKS4, HTTP)"""

    def set_proxy_type(self, proxy_type: str):
        proxy_type_lc = proxy_type.lower()
        if proxy_type_lc == 'socks5':
            self.proxy_type = ProxyType.SOCKS5
        elif proxy_type_lc == 'socks4':
            self.proxy_type = ProxyType.SOCKS4
        elif proxy_type_lc == 'http':
            self.proxy_type = ProxyType.HTTP
        else:
            self.proxy_type = None

    def set_proxy_list(self, proxy_list: list[Proxy]):
        self.proxy_list = proxy_list
        self.proxy_list_initial_len = len(proxy_list)

    # TODO prioritize faster proxies
    def get_random_proxy(self) -> Proxy:
        self.__proxy_extract_counter += 1
        if self.__proxy_extract_counter % PROXY_MIN_VALIDATION_REQUESTS == 0:
            self.vacuum()
        if not self.proxy_list or not len(self.proxy_list):
            return None
        return random.choice(self.proxy_list)

    def find_proxy_index(self, proxy: Proxy) -> int:
        """returns -1 if not found"""
        try:
            return self.proxy_list.index(proxy)
        # except ValueError:
        except:
            return -1

    def __delete_proxy(self, proxy: Proxy) -> bool:
        index = self.find_proxy_index(proxy)
        if index >= 0:
            self.proxy_list.pop(index)
        return index >= 0

    def delete_proxy_sync(self, proxy: Proxy) -> bool:
        lock.acquire()
        is_deleted = self.__delete_proxy(proxy)
        lock.release()
        return is_deleted

    def __validate_proxy(self, proxy: Proxy) -> bool:
        total_cnt = proxy.success_cnt + proxy.failure_cnt
        if total_cnt < PROXY_MIN_VALIDATION_REQUESTS:
            return True
        failure_ratio = proxy.failure_cnt / proxy.success_cnt
        return failure_ratio < PROXY_MAX_FAILURE_RATIO

    def vacuum(self) -> int:
        """Removes proxies which are not valid"""
        new_proxy_list = list(filter(lambda proxy: self.__validate_proxy(proxy), self.proxy_list))
        cnt = len(self.proxy_list) - len(new_proxy_list)
        if cnt > 0:
            self.proxy_list = new_proxy_list
        return cnt

    def __parse_proxy_line(self, line: str) -> Proxy:
        # ip:port:username:password or ip:port
        args = line.strip().split(':')
        if len(args) not in [2, 4]:
            raise ValueError(args)
        return Proxy(*args, proxy_type=self.proxy_type)

    def __parse_proxy_lines(self, lines: list[str]) -> Proxy:
        proxy_list = []
        for line in lines:
            proxy_list.append(self.__parse_proxy_line(line))
        return proxy_list

    def update_proxy_list_from_file(self, filename: str) -> List[Proxy]:
        lines = read_file_lines(filename)
        proxy_list = self.__parse_proxy_lines(lines)
        self.set_proxy_list(proxy_list)
        return proxy_list
