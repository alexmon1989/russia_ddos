import datetime
import threading
from queue import Queue

from ripper.constants import *
from ripper.common import Singleton

# ==== Events template ====

INFO_TEMPLATE  = '[dim][bold][cyan][{0}][/] [blue reverse]{1:^7}[/] {2}'
WARN_TEMPLATE  = '[dim][bold][cyan][{0}][/] [orange1 reverse]{1:^7}[/] {2}'
ERROR_TEMPLATE = '[dim][bold][cyan][{0}][/] [red1 reverse]{1:^7}[/] {2}'


class LogLevel:
    none: int = 0
    error: int = 1
    warn: int = 2
    info: int = 3

    @staticmethod
    def get_by_name(name: str) -> int:
        if name == 'none':
            return LogLevel.none
        if name == 'error':
            return LogLevel.error
        if name == 'warn':
            return LogLevel.warn
        if name == 'info':
            return LogLevel.info


def build_event(log_level: )


class EventsJournal(metaclass=Singleton):
    """Collect and represent various logs and events."""
    _lock = None
    _queue: Queue
    _buffer: list[str]
    _log_level: LogLevel = None

    def __init__(self, size: int = DEFAULT_LOG_SIZE, log_level: str = DEFAULT_LOG_LEVEL):
        self._lock = threading.Lock()
        self._queue = Queue()
        self._buffer = [''] * size
        self._log_level = LogLevel.get_by_name(log_level)

    def get_log(self) -> list[str]:
        with self._lock:
            if not self._queue.empty():
                self._buffer.pop(0)
                self._buffer.append(self._queue.get())

        return self._buffer

    def info(self, message: str):
        if self._log_level >= LogLevel.info:
            self._push_event(INFO_TEMPLATE, 'info', message)

    def warn(self, message: str):
        if self._log_level >= LogLevel.warn:
            self._push_event(WARN_TEMPLATE, 'warn', message)

    def error(self, message: str):
        if self._log_level >= LogLevel.error:
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
