class PacketsStats:
    """Class for TCP/UDP statistic collection."""
    total_sent: int = 0
    """Total packets sent by TCP/UDP."""
    total_sent_prev: int = 0
    """Total packets sent by TCP/UDP (previous state)."""
    total_sent_bytes: int = 0
    """Total sent bytes by TCP/UDP connect."""
    connections_check_time: int = 0
    """Connection last check time."""

    def sync_packets_sent(self):
        """Sync previous packets sent stats with current packets sent stats."""
        self.total_sent_prev = self.total_sent

    def status_sent(self, sent_bytes: int = 0):
        """
        Collect sent packets statistic.
        :param sent_bytes sent packet size in bytes.
        """
        self.total_sent += 1
        self.total_sent_bytes += sent_bytes
