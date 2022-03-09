import os
from datetime import datetime
from collections import defaultdict
from typing import List
from ripper.sockets import SocketManager
from ripper.common import readfile


def get_headers_dict(base_headers: List[str]):
    """Set headers for the request"""
    headers_dict = {}
    for line in base_headers:
        parts = line.split(':')
        headers_dict[parts[0]] = parts[1].strip()
    
    return headers_dict


class Context:
    """Class (Singleton) for passing a context to a parallel processes."""
    version: str = ''

    # Input params
    host: str = ''
    host_ip: str = ''
    port: int = 80
    threads: int = 100
    max_random_packet_len: int = 0
    random_packet_len: bool = False
    attack_method: str = None

    protocol: str = 'http://'
    original_host: str = ''
    url: str = None

    # Internal vars
    # user_agents: list = None
    # base_headers: list = None
    # headers = None
    user_agents = readfile(os.path.dirname(__file__) + '/useragents.txt')
    base_headers = readfile(os.path.dirname(__file__) + '/headers.txt')
    headers = get_headers_dict(base_headers)

    # Statistic
    my_country: str = None
    target_country: str = None
    start_time = datetime.now()
    start_ip: str = ''
    packets_sent: int = 0
    connections_success: int = 0
    connections_success_prev: int = 0
    packets_sent_prev: int = 0
    connections_failed: int = 0
    connections_check_time: int = 0
    errors: List[str] = []

    # cpu_count: int = 1
    cpu_count = max(os.cpu_count(), 1)  # to avoid situation when vCPU might be 0
    show_statistics: bool = False
    current_ip = None
    getting_ip_in_progress: bool = False

    # Method-related stats
    http_codes_counter = defaultdict(int)

    # External API and services info
    isCloudflareProtected: bool = False
    sock_manager: SocketManager = SocketManager()

    connecting_host: bool = False

    # Health-check
    fetching_host_statuses_in_progress: bool = False
    last_host_statuses_update: datetime = None
    health_check_method: str = ''
    host_statuses = {}

    def __new__(cls):
        """Singleton realization."""
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance
