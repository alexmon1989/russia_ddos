from threading import Lock
from enum import Enum

from ripper.context.target import Target
from ripper.actions.attack import Attack

Context = 'Context'


class ThreadsDistribution(Enum):
    Fixed = 'fixed',
    Auto = 'auto',

# Add support for ThreadsDistribution
# Add arg option (str) for threads count, "auto"
# If auto selected, start with minimal number of threads and grow till packets sent grows (total) and till CPU < 100%

class TargetsManager:
    _targets: list[Target] = None
    _ctx: Context = None
    _lock: Lock = None
    _threads_count: int = None

    def __init__(self, _ctx: Context, threads_count: int = 1):
        self._targets = []
        self._ctx = _ctx
        self._lock = Lock()
        self._threads_count = threads_count

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
    
    def set_threads_count(self, threads_count: int):
        self._threads_count = threads_count

    def add_target(self, target):
        self._targets.append(target)
        target_idx = self._targets.index(target)
        target.index = target_idx

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

    def len(self):
        return len(self._targets)
