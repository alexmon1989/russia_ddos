from datetime import datetime, timedelta
import time
from threading import Thread

Context = 'Context'


class DurationManager:
    _start_time: datetime = None
    """Script start time."""
    _duration: timedelta = None
    """Attack duration. After this duration script will stop it\'s execution."""
    _ctx: Context = None

    def __init__(self, _ctx: Context, duration_seconds: int = None):
      if duration_seconds is not None:
        self._duration = timedelta(0, duration_seconds)
        self._ctx = _ctx
    
    def delayed_exit(self):
        time.sleep(self._duration.total_seconds())
        self._ctx.targets_manager.delete_all_targets()

    def start_countdown(self):
        if self._duration is not None:
            self._start_time = datetime.now()
            Thread(target=self.delayed_exit).start()
    
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
        remaining_delta = self.finish_time - datetime.now()
        # To prevent situation with negative remaining duration
        if remaining_delta.total_seconds() < 0:
            return timedelta(seconds=0)
        return remaining_delta
