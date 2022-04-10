from datetime import datetime, timedelta
import os
import time
from threading import Thread


def delayed_os_exit(delay: int):
    time.sleep(delay)
    os._exit(0)


class DurationManager:
    _start_time: datetime = None
    """Script start time."""
    _duration: timedelta = None
    """Attack duration. After this duration script will stop it\'s execution."""

    def __init__(self, duration_seconds: int = None):
      if duration_seconds is not None:
        self._duration = timedelta(0, duration_seconds)
    
    def start_countdown(self):
        if self._duration is not None:
            self._start_time = datetime.now()
            Thread(target=delayed_os_exit, args=[self._duration.total_seconds()]).start()
    
    @property
    def finish_time(self) -> datetime:
        if self._duration is None:
            return None
        return self._start_time + self._duration

    @property
    def duration(self) -> timedelta:
        return self._duration

    @property
    def remaining_duration(self) -> timedelta:
        if self._duration is None:
            return None
        return self.finish_time - datetime.now()
