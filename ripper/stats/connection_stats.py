from threading import Lock


class ConnectionStats:
    """Class for Connection statistic"""
    success_prev: int = 0
    """Total connections to HOST with Success status (previous state)"""
    success: int = 0
    """Total connections to HOST with Success status"""
    failed: int = 0
    """Total connections to HOST with Failed status."""
    last_check_time: int = 0
    """Last check connection time."""
    in_progress: bool = False
    """Connection state used for checking liveness of Socket."""
    _lock: Lock = None

    def __init__(self):
        self._lock = Lock()

    def get_success_rate(self) -> int:
        """Calculate Success Rate for connection."""
        if self.success == 0:
            return 0

        return int(self.success / (self.success + self.failed) * 100)

    def sync_success(self):
        """Sync previous success state with current success state."""
        self.success_prev = self.success

    def set_state_in_progress(self):
        """Set connection State - in progress."""
        self.in_progress = True

    def set_state_is_connected(self):
        """Set connection State - is connected."""
        self.in_progress = False

    def status_success(self):
        """Collect successful connections."""
        self.success += 1

    def status_failed(self):
        """Collect failed connections."""
        self.failed += 1
