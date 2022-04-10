import pytest
import time
from random import randint

from ripper.context.target import Target
from ripper.targets_manager import TargetsManagerPacketsStats


class DescribeTargetsManagerPacketsStats:
    def build_targets_list(self):
        return [
            Target(target_uri='http://google.com'),
            Target(target_uri='http://medium.com'),
            Target(target_uri='http://github.com'),
        ]
    
    def increase_target_packets(self, target: Target, total_sent: int, total_sent_bytes: int):
        target.stats.packets.total_sent += total_sent
        target.stats.packets.total_sent_bytes += total_sent_bytes
    
    def increase_target_packets_list(self, targets: list[Target]):
        tmps1 = TargetsManagerPacketsStats(targets)
        before_total_sent = tmps1.total_sent
        before_total_sent_bytes = tmps1.total_sent_bytes
        expected_total_sent = before_total_sent
        expected_total_sent_bytes = before_total_sent_bytes
        for target in targets:
            sent = randint(0, 10)
            sent_bytes = randint(0, 10000)
            expected_total_sent += sent
            expected_total_sent_bytes += sent_bytes
            self.increase_target_packets(target, sent, sent_bytes)
        tmps2 = TargetsManagerPacketsStats(targets=targets)
        assert tmps2.total_sent == expected_total_sent
        assert tmps2.total_sent_bytes == expected_total_sent_bytes
        assert tmps2 > tmps1
        assert tmps1 < tmps2

    def it_should_accumulate_data_from_targets(self):
        targets = self.build_targets_list()
        tmps = TargetsManagerPacketsStats(targets=targets)
        assert tmps.total_sent == 0
        assert tmps.total_sent_bytes == 0
        self.increase_target_packets_list(targets)
        self.increase_target_packets_list(targets)
        self.increase_target_packets_list(targets)
    
    def it_should_calculate_average_with_duration(self):
        targets = self.build_targets_list()
        self.increase_target_packets_list(targets)
        tmps = TargetsManagerPacketsStats(targets=targets)
        avg_sent_per_second = tmps.avg_sent_per_second
        avg_sent_bytes_per_second = tmps.avg_sent_bytes_per_second
        time.sleep(1)
        tmps = TargetsManagerPacketsStats(targets=targets)
        assert avg_sent_per_second > tmps.avg_sent_per_second
        assert avg_sent_bytes_per_second > tmps.avg_sent_bytes_per_second
