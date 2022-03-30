import datetime
import threading
from queue import Queue

from ripper.common import format_dt
from ripper.constants import DATE_TIME_SHORT

# ==== Events template ====
INFO_TEMPLATE  = '[dim][{0}][/] [blue reverse]{1:^7}[/] {2}'
WARN_TEMPLATE  = '[dim][{0}][/] [orange1 reverse]{1:^7}[/] {2}'
ERROR_TEMPLATE = '[dim][{0}][/] [red1 reverse]{1:^7}[/] {2}'


class EventsJournal:
    """Collect and represent various logs and events."""

    _queue: Queue
    _buffer: list[str] = ['', '', '', '', '']

    def __init__(self, size: int = 0):
        self._queue = Queue(maxsize=size)

    def last(self, quantity: int):
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

    def _push_event(self, template: str, level: str, message: str):
        now = format_dt(datetime.datetime.now(), DATE_TIME_SHORT)
        event = template.format(
            now,
            level,
            f'{threading.current_thread().name.lower():11} {message}')
        self._queue.put(event)


