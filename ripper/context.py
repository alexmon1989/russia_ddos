from datetime import datetime
from collections import defaultdict
from typing import List
from ripper.sockets import SocketManager


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
    user_agents: list = None
    base_headers: list = None
    headers = None

    # Statistic
    country: str = None
    start_time: datetime = None
    start_ip: str = ''
    packets_sent: int = 0
    connections_success: int = 0
    connections_success_prev: int = 0
    packets_sent_prev: int = 0
    connections_failed: int = 0
    connections_check_time: int = 0
    errors: List[str] = []

    cpu_count: int = 1
    show_statistics: bool = False
    current_ip = None
    getting_ip_in_progress: bool = False

    # Method-related stats
    http_codes_counter = defaultdict(int)

    # External API and services info
    isCloudflareProtected: bool = False
    sock_manager: SocketManager = SocketManager()

    def __new__(cls):
        """Singleton realization."""
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance
