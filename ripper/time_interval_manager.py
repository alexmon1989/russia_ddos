from datetime import datetime, timedelta
from collections import defaultdict

from ripper.common import Singleton, s2ns


class TimeIntervalManager(metaclass=Singleton):
    _timer_bucket: dict[str, datetime] = None
    """Internal stopwatch."""
    _start_time: datetime = None
    """Script start time."""

    def __init__(self):
      self._start_time = datetime.now()
      self._timer_bucket = defaultdict(dict[str, datetime])
    
    def reset_start_time(self):
        self._start_time = datetime.now()
    
    @property
    def start_time(self) -> datetime:
        return self._start_time

    @property
    def execution_duration(self) -> timedelta:
        return datetime.now() - self._start_time

    @property
    def start_time_ns(self) -> int:
        """Get start time in nanoseconds."""
        if not self._start_time:
            return 0
        return s2ns(self._start_time.timestamp())
    
    def _get_key_name(self, bucket: str = None) -> str:
        if bucket:
            return bucket
        return '__stopwatch__'

    def check_timer_elapsed(self, sec: int, bucket: str = None) -> bool:
        """
        Check if time in seconds elapsed from last check.
        :param sec: Amount of seconds which needs to check.
        :param bucket: Bucket name to track specific timer.
        :return: True if specified seconds elapsed, False - if not elapsed.
        """
        key = self._get_key_name(bucket)
        delta = self.get_timer_seconds(bucket=key)
        if int(delta) < sec:
            return False
        else:
            self._timer_bucket[key] = datetime.now()
            return True

    def get_timer_seconds(self, bucket: str = None) -> int:
        key = self._get_key_name(bucket)
        if key not in self._timer_bucket:
            return int(datetime.now().timestamp())

        return int((datetime.now() - self._timer_bucket[bucket]).total_seconds())
