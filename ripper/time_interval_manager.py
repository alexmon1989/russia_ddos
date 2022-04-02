from datetime import datetime
from collections import defaultdict

from ripper.common import Singleton, s2ns


class TimeIntervalManager(metaclass=Singleton):
    timer_bucket: dict[str, datetime] = None
    """Internal stopwatch."""
    start_time: datetime = None
    """Script start time."""

    def __init__(self):
      self.start_time = datetime.now()
      self.timer_bucket = defaultdict(dict[str, datetime])

    def check_timer(self, sec: int, bucket: str = None) -> bool:
        """
        Check if time in seconds elapsed from last check.
        :param sec: Amount of seconds which needs to check.
        :param bucket: Bucket name to track specific timer.
        :return: True if specified seconds elapsed, False - if not elapsed.
        """
        stopwatch = '__stopwatch__' if bucket is None else bucket

        if not self.timer_bucket[stopwatch]:
            self.timer_bucket[stopwatch] = self.start_time
        delta = (datetime.now() - self.timer_bucket[stopwatch]).total_seconds()
        if int(delta) < sec:
            return False
        else:
            self.timer_bucket[stopwatch] = datetime.now()
            return True

    def get_timer_seconds(self, bucket: str = None) -> int:
         stopwatch = '__stopwatch__' if bucket is None else bucket

         if self.timer_bucket[stopwatch]:
             return int((datetime.now() - self.timer_bucket[bucket]).total_seconds())

         return 0

    def get_start_time_ns(self) -> int:
        """Get start time in nanoseconds."""
        if not self.start_time:
            return 0
        return s2ns(self.start_time.timestamp())
