import re
import threading


class AttackMethod:
    """Abstract attack method."""

    @property
    def name(self):
      raise NotImplemented

    @property
    def label(self):
      raise NotImplemented

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    def validate(self):
      return True

    @property
    def thread_name(self):
        return threading.current_thread().name
