import pytest
import time
import json
import docker
import urllib.request
from typing import Any
from optparse import Values

from docker import DockerClient

from ripper.services import dripper
from ripper.constants import *
from ripper.arg_parser import Args

DockerContainer = 'DockerContainer'


class DescribeBenchmark:
    image: str = 'oknyga/ddos-attack-benchmarker:latest'
    http_control_api_port: int = 8000
    tcp_benchmark_port: int = 8080
    udp_benchmark_port: int = 8053
    client: DockerClient = None
    container: DockerContainer = None

    @property
    def http_control_api_url(self):
        return f'http://localhost:{self.http_control_api_port}'

    @pytest.fixture(scope='class', autouse=True)
    def run_benchmarking_container(self):
        # Warning Make sure you run Docker Daemon!
        self.client = docker.from_env()
        [container.stop() for container in self.client.containers.list(filters={'ancestor': self.image})]
        # docker run -it -p 8000:8000/tcp -p 8080:8080/tcp -p 8053:8053/udp --rm oknyga/ddos-attack-benchmarker:latest -p 8000
        self.container = self.client.containers.run(
            image=self.image,
            command='-p 8000',
            detach=True,
            ports={
                '8000/tcp': self.http_control_api_port,
                '8053/udp': self.udp_benchmark_port,
                '8080/tcp': self.tcp_benchmark_port,
            },
        )
        # We might need some time to boot
        time.sleep(2)
        yield
        self.container.stop()
    
    def format_args(self, args: Values):
        return (
                f'Attack Method: {args.attack_method}\n'
                f'Threads Count: {args.threads_count}\n'
                #f'Min Random Packet Length (bytes): {args.min_random_packet_len}\n'
                #f'Max Random Packet Length (bytes): {args.max_random_packet_len}\n'
                f'Duration (seconds): {args.duration}'
               )
    
    def print_results(self, args: Values):
        print('\n---------INFO---------')
        print(self.format_args(args))
        print('---------DATA---------')
        print(str(urllib.request.urlopen(f'{self.http_control_api_url}/stats?view=text').read().decode()).replace('\\n', '\n'))
    
    def stop_and_validate(self, args: Values, expected_data: dict[str, Any], down_scale_factor: int = 10):
        actual = json.loads(urllib.request.urlopen(f'{self.http_control_api_url}/stop').read())
        assert actual['code'] == 200
        actual_data = actual['data']
        assert actual_data['type'] == expected_data['type']
        assert actual_data['duration']['seconds'] >= args.duration
        assert actual_data['requests']['total']['count'] > expected_data['requests']['total']['count'] / down_scale_factor
        assert actual_data['requests']['total']['bytes'] > expected_data['requests']['total']['bytes'] / down_scale_factor
        assert actual_data['requests']['average']['perSecond']['count'] > expected_data['requests']['average']['perSecond']['count'] / down_scale_factor
        assert actual_data['requests']['average']['perSecond']['bytes'] > expected_data['requests']['average']['perSecond']['bytes'] / down_scale_factor
        self.print_results(args)

    # Testset was prepared at 2022-04-24 on 2.3 GHz Quad-Core Intel Core i7
    # It is hard to imagine any CPU to perfrom more than 10 times slower
    @pytest.mark.parametrize('args, expected_data', [
        # Dripper takes ~7s to validate connection and boot
        (Args(threads_count=1, verbose=False, attack_method='http-flood', duration=5, health_check=0), {'type': 'http', 'duration': {'seconds': 12.15}, 'requests': {'average': {'perSecond': {'count': 5182.484155074492, 'bytes': 39362223335.33624}}, 'total': {'count': 62962, 'bytes': 478211651301}}}),
    ])
    def it_http_flood_benchmark(self, args, expected_data):
        urllib.request.urlopen(f'{self.http_control_api_url}/start?type=http&port={self.tcp_benchmark_port}').read()
        args_targeted = args._replace(targets=[f'http://localhost:{self.tcp_benchmark_port}'])
        dripper(args_targeted)
        self.stop_and_validate(
            args=args_targeted,
            expected_data=expected_data,
        )

    @pytest.mark.parametrize('args, expected_data', [
        (Args(threads_count=1, verbose=False, attack_method='tcp-flood', duration=5, health_check=0), {'type': 'tcp', 'duration': {'seconds': 9.45}, 'requests': {'average': {'perSecond': {'count': 82.84837583324516, 'bytes': 128909.3217648926}}, 'total': {'count': 783, 'bytes': 1218322}}}),
    ])
    def it_tcp_flood_benchmark(self, args, expected_data):
        urllib.request.urlopen(f'{self.http_control_api_url}/start?type=tcp&port={self.tcp_benchmark_port}').read()
        args_targeted = args._replace(targets=[f'tcp://localhost:{self.tcp_benchmark_port}'])
        dripper(args_targeted)
        self.stop_and_validate(
            args=args_targeted,
            expected_data=expected_data,
        )

    @pytest.mark.parametrize('args, expected_data', [
        (Args(threads_count=1, verbose=False, attack_method='udp-flood', duration=5, health_check=0), {'type': 'udp', 'duration': {'seconds': 5.55}, 'requests': {'average': {'perSecond': {'count': 465.4303204897371, 'bytes': 238128.37594526465}}, 'total': {'count': 2585, 'bytes': 1322565}}}),
    ])
    def it_udp_flood_benchmark(self, args, expected_data):
        urllib.request.urlopen(f'{self.http_control_api_url}/start?type=udp&port={self.udp_benchmark_port}').read()
        args_targeted = args._replace(targets=[f'udp://localhost:{self.udp_benchmark_port}'])
        dripper(args_targeted)
        self.stop_and_validate(
            args=args_targeted,
            expected_data=expected_data,
        )
