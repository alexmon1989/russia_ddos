import time
import threading


class PacketsStats:
    """Class for TCP/UDP statistic collection."""
    total_sent: int = 0
    """Total packets sent by TCP/UDP."""
    
    total_sent_bytes: int = 0
    """Total sent bytes by TCP/UDP connect."""
    connections_check_time: int = 0
    """Connection last check time."""
    _lock: threading.Lock

    def __init__(self):
        self._lock = threading.Lock()
        self.connections_check_time = time.time_ns()

    def status_sent(self, sent_bytes: int = 0):
        """
        Collect sent packets statistic.
        :param sent_bytes sent packet size in bytes.
        """
        with self._lock:
            self.connections_check_time = time.time_ns()
            self.total_sent += 1
            self.total_sent_bytes += sent_bytes
