import threading
from threading import Thread, Event

from ripper.actions.attack_method import AttackMethod
from ripper.actions.http_bypass import HttpBypass
from ripper.actions.http_flood import HttpFlood
from ripper.actions.tcp_flood import TcpFlood
from ripper.actions.udp_flood import UdpFlood
from ripper.context.events_journal import EventsJournal

# Forward Reference
Context = 'Context'
Target = 'Target'

events_journal = EventsJournal()


# noinspection PyTypeChecker
attack_methods: list[AttackMethod] = [
    UdpFlood,
    TcpFlood,
    HttpFlood,
    HttpBypass,
]

attack_method_labels: list[str] = list(map(lambda am: am.label, attack_methods))


def attack_method_factory(_ctx: Context, target: Target):
    attack_method_name = target.attack_method
    # events_journal.info(f'Set attack method to {target.attack_method}', target=target)
    if attack_method_name == 'udp-flood':
        return UdpFlood(target=target, context=_ctx)
    elif attack_method_name == 'http-flood':
        return HttpFlood(target=target, context=_ctx)
    elif attack_method_name == 'tcp-flood':
        return TcpFlood(target=target, context=_ctx)
    elif attack_method_name == 'http-bypass':
        return HttpBypass(target=target, context=_ctx)
    # Dangerous, may lead to exception
    return None


class Attack(Thread):
    """This class creates threads with specified attack method."""
    _ctx: Context
    target: Target
    stop_event: Event = None

    def __init__(self, _ctx: Context, target: Target):
        """
        :param target: Target IPv4 address and destination port.
        :param method: Attack method.
        """
        Thread.__init__(self, daemon=True)
        self._ctx = _ctx
        self.target = target
        self.target.add_attack_thread(self)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        self.target.init()
        runner = attack_method_factory(_ctx=self._ctx, target=self.target)

        if self._ctx.dry_run:
            runner()
            exit(0)

        while not self.stop_event.is_set():
            runner()
