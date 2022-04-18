import time
from enum import Enum
from threading import Thread, Event, Lock
from psutil import cpu_percent

from ripper.context.target import Target
from ripper.actions.attack import Attack
from ripper.constants import *
from ripper.context.events_journal import EventsJournal

Context = 'Context'
events_journal = EventsJournal()


class ThreadsDistribution(Enum):
    Fixed = 'fixed',
    Auto = 'auto',


class TargetsManagerPacketsStats:
    total_sent: int = 0
    total_sent_bytes: int = 0
    avg_sent_per_second: int = 0
    avg_sent_bytes_per_second: int = 0

    def __init__(self, targets: list[Target]) -> None:
        duration_seconds = None
        for target in targets:
            self.total_sent += target.stats.packets.total_sent
            self.total_sent_bytes += target.stats.packets.total_sent_bytes
            if duration_seconds is None:
                duration_seconds = target.time_interval_manager.execution_duration.total_seconds()
        if duration_seconds:
            self.avg_sent_per_second = self.total_sent / duration_seconds
            self.avg_sent_bytes_per_second = self.total_sent / duration_seconds

    def __ge__(self, other: 'TargetsManagerPacketsStats'):
        return self.avg_sent_per_second > other.avg_sent_per_second \
            and self.avg_sent_bytes_per_second > other.avg_sent_bytes_per_second

    def __lt__(self, other: 'TargetsManagerPacketsStats'):
        return self.avg_sent_per_second < other.avg_sent_per_second \
            and self.avg_sent_bytes_per_second < other.avg_sent_bytes_per_second

    def __eq__(self, other: 'TargetsManagerPacketsStats'):
        return self.avg_sent_per_second == other.avg_sent_per_second \
            and self.avg_sent_bytes_per_second == other.avg_sent_bytes_per_second


class AutomaticThreadsDistribution:
    _packet_stats: TargetsManagerPacketsStats = None
    _targets_manager: 'TargetsManager' = None
    _interval_delay_seconds: int = None
    _stop_event: Event = None
    _failed_tests_cnt: int = 0
    """Count of failed performance improvements checks after scale up"""

    def __init__(self, targets_manager: 'TargetsManager', interval_delay_seconds: int = DEFAULT_AUTOSCALE_TEST_SECONDS) -> None:
        self._targets_manager = targets_manager
        self._interval_delay_seconds = interval_delay_seconds
        self._stop_event = Event()

    def scale_up(self):
        threads_count = self._targets_manager.threads_count
        new_threads_count = threads_count + self._targets_manager.targets_count()
        events_journal.info(f'Scale up from {threads_count} to {new_threads_count}')
        self._targets_manager.set_threads_count(new_threads_count)
        self._targets_manager.allocate_attacks()

    def __runner__(self):
        while not self._stop_event.is_set():
            time.sleep(self._interval_delay_seconds)
            current_packet_stats = TargetsManagerPacketsStats(targets=self._targets_manager.targets)
            if self._packet_stats:
                if self._packet_stats < current_packet_stats and cpu_percent(5) < MAX_AUTOSCALE_CPU_PERCENTAGE:
                    self._failed_tests_cnt = 0
                    self.scale_up()
                else:
                    self._failed_tests_cnt += 1
                    if self._failed_tests_cnt >= MAX_FAILED_FAILED_AUTOSCALE_TESTS:
                        self.stop()
            self._packet_stats = current_packet_stats

    def start(self):
        events_journal.info(f'Start automatic threads distribution')
        Thread(target=self.__runner__).start()

    def stop(self):
        events_journal.info(f'Stop automatic threads distribution')
        self._stop_event.set()


class TargetsManager:
    _targets: list[Target] = None
    _ctx: Context = None
    _lock: Lock = None
    _threads_count: int = None
    _threads_distribution: ThreadsDistribution = None

    def __init__(self, _ctx: Context, threads_count: int = 1, threads_distribution: ThreadsDistribution = ThreadsDistribution.Fixed):
        self._targets = []
        self._ctx = _ctx
        self._lock = Lock()
        self._threads_count = threads_count
        self._threads_distribution = threads_distribution

    @property
    def free_threads_count(self):
        total = self.threads_count
        self._lock.acquire()
        for target in self._targets:
            total -= len(target.attack_threads)
        self._lock.release()
        return total

    @property
    def targets(self):
        return self._targets[:]

    @property
    def threads_count(self):
        return self._threads_count

    @property
    def threads_distribution(self):
        return self._threads_distribution

    def set_threads_count(self, threads_count: int):
        # We can't have fewer threads than targets
        self._threads_count = max(threads_count, len(self._targets))

    def set_auto_threads_distribution(self):
        self._threads_distribution = ThreadsDistribution.Auto
        atd = AutomaticThreadsDistribution(targets_manager=self)
        atd.start()

    def add_target(self, target):
        self._targets.append(target)
        target_idx = self._targets.index(target)
        target.index = target_idx
        # We can't have fewer threads than targets
        self._threads_count = max(self._threads_count, len(self._targets))

    def delete_target(self, target: Target, is_stop_attack: bool = True, is_allocate_attacks: bool = True):
        if is_stop_attack:
            target.stop_attack_threads()
        self._lock.acquire()
        try:
            target_idx = self._targets.index(target)
            self._targets.pop(target_idx)
        except:
            pass
        self._lock.release()
        if is_allocate_attacks:
            self.allocate_attacks()

    def allocate_attacks(self):
        free_threads_count = self.free_threads_count
        if free_threads_count < 1:
            return
        self._lock.acquire()
        targets_cnt = len(self._targets)
        if targets_cnt < 1:
            return
        for idx in range(free_threads_count):
            target = self._targets[idx % targets_cnt]
            Attack(_ctx=self._ctx, target=target).start()
        self._lock.release()

    def targets_count(self):
        return len(self._targets)
