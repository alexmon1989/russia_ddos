from threading import Lock

from ripper.context.target import Target
from ripper.actions.attack import Attack

Context = 'Context'


class TargetsManager:
    _targets: list[Target] = None
    _ctx: Context = None
    _lock: Lock = None

    def __init__(self, _ctx: Context):
        self._targets = []
        self._ctx = _ctx
        self._lock = Lock()

    @property
    def free_threads_count(self):
        total = self._ctx.threads_count
        self._lock.acquire()
        for target in self._targets:
          total -= len(target.attack_threads)
        self._lock.release()
        return total
    
    @property
    def targets(self):
        return self._targets[:]

    def add_target(self, target):
        self._targets.append(target)

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
