import threading
import random
import threading

from ripper.proxy import Sock5Proxy
from ripper.constants import PROXY_MAX_FAILURE_RATIO, PROXY_MIN_VALIDATION_REQUESTS

lock = threading.Lock()

class ProxyManager:
    """Manager for proxy collection."""

    proxy_list: list[Sock5Proxy] = []
    """Active proxies."""
    proxy_list_initial_len: int = 0
    """Count of proxies during the last application."""
    __proxy_extract_counter: int = 0
    """Vacuum operation is called automatically on every PROXY_MIN_VALIDATION_REQUESTS proxy extractions"""

    def set_proxy_list(self, proxy_list: list[Sock5Proxy]):
        self.proxy_list = proxy_list
        self.proxy_list_initial_len = len(proxy_list)

    # TODO prioritize faster proxies
    def get_random_proxy(self) -> Sock5Proxy:
        self.__proxy_extract_counter += 1
        if self.__proxy_extract_counter % PROXY_MIN_VALIDATION_REQUESTS == 0:
            self.vacuum()
        if not self.proxy_list or not len(self.proxy_list):
            return None
        return random.choice(self.proxy_list)

    def find_proxy_index(self, proxy: Sock5Proxy) -> int:
        """returns -1 if not found"""
        try:
            return self.proxy_list.index(proxy)
        # except ValueError:
        except:
            return -1

    def __delete_proxy(self, proxy: Sock5Proxy) -> bool:
        index = self.find_proxy_index(proxy)
        if index >= 0:
            self.proxy_list.pop(index)
        return index >= 0

    def delete_proxy_sync(self, proxy: Sock5Proxy) -> bool:
        lock.acquire()
        is_deleted = self.__delete_proxy(proxy)
        lock.release()
        return is_deleted
    
    def __validate_proxy(self, proxy: Sock5Proxy) -> bool:
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
