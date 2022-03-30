import datetime
from queue import Queue

from ripper.common import format_dt
from ripper.constants import DATE_TIME_SHORT, INFO_TEMPLATE, WARN_TEMPLATE, ERROR_TEMPLATE


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
        self._push_event(INFO_TEMPLATE, message)

    def warn(self, message: str):
        self._push_event(WARN_TEMPLATE, message)

    def error(self, message: str):
        self._push_event(ERROR_TEMPLATE, message)

    def _push_event(self, template: str, message: str):
        now = format_dt(datetime.datetime.now(), DATE_TIME_SHORT)
        event = template.format(now, message)
        self._queue.put(event)


