import datetime
import textwrap
import threading
from queue import Queue

from ripper.constants import *
from ripper.common import Singleton

Target = 'Target'


class EventLevel:
    none: int = 0
    error: int = 1
    warn: int = 2
    info: int = 3

    @staticmethod
    def get_id_by_name(name: str) -> int:
        if name == 'none':
            return EventLevel.none
        if name == 'error':
            return EventLevel.error
        if name == 'warn':
            return EventLevel.warn
        if name == 'info':
            return EventLevel.info

    @staticmethod
    def get_name_by_id(id: int) -> str:
        if id == EventLevel.none:
            return 'none'
        if id == EventLevel.error:
            return 'error'
        if id == EventLevel.warn:
            return 'warn'
        if id == EventLevel.info:
            return 'info'


class Event:
    _level: int = EventLevel.none
    _target: Target = None
    _message: str = None

    def __init__(self, level: int, message: str, target: Target = None):
        self._level = level
        self._message = message
        self._target = target

    def get_level_color(self):
        if self._level == EventLevel.warn:
            return 'bold orange1 reverse'
        if self._level == EventLevel.error:
            return 'bold white on red3'
        return 'bold blue reverse'

    def format_message(self):
        now = datetime.datetime.now().strftime(DATE_TIME_SHORT)
        thread_name = threading.current_thread().name.lower()
        log_level_name = EventLevel.get_name_by_id(self._level)
        log_level_color = self.get_level_color()
        locator = f'target-{self._target.index}' if self._target is not None else 'global'
        msg_limited = textwrap.shorten(self._message, width=50, placeholder='...')
        return f'[dim][bold][cyan][{now}][/]  [{log_level_color}]{log_level_name:^7}[/] {locator:9} {thread_name:11} {msg_limited}'


class EventsJournal(metaclass=Singleton):
    """Collect and represent various logs and events_journal."""
    _lock = None
    _queue: Queue = None
    _buffer: list[str] = None
    _max_event_level: int = EventLevel.none

    def __init__(self):
        self._lock = threading.Lock()
        self._queue = Queue()
        self.set_log_size(DEFAULT_LOG_SIZE)
        self.set_max_event_level(DEFAULT_LOG_LEVEL)

    def set_log_size(self, size):
        self._buffer = [''] * size

    def set_max_event_level(self, max_event_level_name: str):
        self._max_event_level = EventLevel.get_id_by_name(max_event_level_name)

    def get_max_event_level(self):
        return self._max_event_level

    def get_log(self) -> list[str]:
        with self._lock:
            if not self._queue.empty():
                self._buffer.pop(0)
                self._buffer.append(self._queue.get())

        return self._buffer

    def info(self, message: str, target: Target = None):
        if self._max_event_level >= EventLevel.info:
            self._push_event(Event(
                level=EventLevel.info,
                message=message,
                target=target,
            ))

    def warn(self, message: str, target: Target = None):
        if self._max_event_level >= EventLevel.warn:
            self._push_event(Event(
                level=EventLevel.warn,
                message=message,
                target=target,
            ))

    def error(self, message: str, target: Target = None):
        if self._max_event_level >= EventLevel.error:
            self._push_event(Event(
                level=EventLevel.error,
                message=message,
                target=target,
            ))

    def exception(self, ex: Exception, target: Target = None):
        self._push_event(Event(
            level=EventLevel.error,
            message=f'{type(ex).__name__}: {ex.__str__()[:128]}',
            target=target,
        ))

    def _push_event(self, event: Event):
        with self._lock:
            self._queue.put(event.format_message())
