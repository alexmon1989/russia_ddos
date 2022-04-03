import datetime
import threading
from queue import Queue

from ripper.constants import DATE_TIME_SHORT
from ripper.common import Singleton

# ==== Events template ====
INFO_TEMPLATE  = '[dim][bold][cyan][{0}][/] [blue reverse]{1:^7}[/] {2}'
WARN_TEMPLATE  = '[dim][bold][cyan][{0}][/] [orange1 reverse]{1:^7}[/] {2}'
ERROR_TEMPLATE = '[dim][bold][cyan][{0}][/] [red1 reverse]{1:^7}[/] {2}'


class EventsJournal(metaclass=Singleton):
    """Collect and represent various logs and events."""

    _lock = None
    _queue: Queue
    _buffer: list[str]

    def __init__(self, size: int = 5):
        self._lock = threading.Lock()
        self._queue = Queue()
        self._buffer = [''] * size

    def get_log(self) -> list[str]:
        with self._lock:
            if not self._queue.empty():
                self._buffer.pop(0)
                self._buffer.append(self._queue.get())

        return self._buffer

    def info(self, message: str):
        self._push_event(INFO_TEMPLATE, 'info', message)

    def warn(self, message: str):
        self._push_event(WARN_TEMPLATE, 'warn', message)

    def error(self, message: str):
        self._push_event(ERROR_TEMPLATE, 'error', message)

    def exception(self, ex):
        self._push_event(ERROR_TEMPLATE, f'{type(ex).__name__}: {ex.__str__()[:128]}')

    def _push_event(self, template: str, level: str, message: str):
        with self._lock:
            now = datetime.datetime.now().strftime(DATE_TIME_SHORT)
            event = template.format(
                now,
                level,
                f'{threading.current_thread().name.lower():11} {message}')
            self._queue.put(event)
