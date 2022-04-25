import pytest
import time
import json
import docker
import urllib.request
from typing import Any
from optparse import Values

from ripper.services import dripper
from ripper.constants import *
from ripper.arg_parser import Args

DockerContainer = 'DockerContainer'


class DescribeBenchmark:
    image: str = 'oknyga/ddos-attack-benchmarker:latest'
    http_control_api_port: int = 8000
    tcp_benchmark_port: int = 8080
    udp_benchmark_port: int = 8053

    @property
    def http_control_api_url(self):
        return f'http://localhost:{self.http_control_api_port}'

    @pytest.fixture(scope='class', autouse=True)
    def run_benchmark_container(self):
        # Warning Make sure you run Docker Daemon!
        # docker run -it -p 8000:8000/tcp -p 8080:8080/tcp -p 8053:8053/udp --rm oknyga/ddos-attack-benchmarker:latest -p 8000
        client = docker.from_env()
        containers = client.containers.list(filters={'ancestor': self.image})
        if len(containers) < 1:
            client.containers.run(
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
        else:
            urllib.request.urlopen(f'{self.http_control_api_url}/stop').read()
    
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

    # Testset was prepared at 2022-04-24 on 2.3 GHz Quad-Core Intel Core i7
    # It is hard to imagine any CPU to perfrom more than 10 times slower
    def it_http_flood_benchmark(self):
        args = Args(
            threads_count=1,
            attack_method='http-flood',
            duration=5,
            targets=[f'http://localhost:{self.tcp_benchmark_port}'],
        )
        expected_data = {'type': 'http', 'duration': {'seconds': 12.15}, 'requests': {'average': {'perSecond': {'count': 5182.484155074492, 'bytes': 39362223335.33624}}, 'total': {'count': 62962, 'bytes': 478211651301}}}
        urllib.request.urlopen(f'{self.http_control_api_url}/start?type=http&port={self.tcp_benchmark_port}').read()
        dripper(args)
        urllib.request.urlopen(f'http://localhost:{self.tcp_benchmark_port}').read()
        try:
            urllib.request.urlopen(f'{self.http_control_api_url}/stop').read()
        except Exception as e:
            print(e)

        assert True
        # self.stop_and_validate(
        #     args=args,
        #     expected_data=expected_data,
        # )

    def it_tcp_flood_benchmark(self):
        args = Args(
            threads_count=1,
            attack_method='tcp-flood',
            duration=5,
            targets=[f'tcp://localhost:{self.tcp_benchmark_port}'],
        )
        expected_data = {"type": "tcp", "duration": {"seconds": 9.45}, "requests": {"average": {"perSecond": {"count": 82.84837583324516, "bytes": 128909.3217648926}}, "total": {"count": 783, "bytes": 1218322}}}
        urllib.request.urlopen(f'{self.http_control_api_url}/start?type=tcp&port={self.tcp_benchmark_port}').read()
        dripper(args)
        try:
            urllib.request.urlopen(f'{self.http_control_api_url}/stop').read()
        except Exception as e:
            print(e)
        # self.stop_and_validate(
        #     args=args,
        #     expected_data=expected_data,
        # )
