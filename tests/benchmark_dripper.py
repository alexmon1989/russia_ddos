import pytest
import os
import time
import json
import urllib.request
from ripper.services import dripper
from ripper.constants import *
from ripper.arg_parser import Args


class DescribeBenchmark:
    http_control_api_port: int = 8000
    tcp_benchmark_port: int = 8080
    udp_benchmark_port: int = 8053

    @property
    def http_control_api_url(self):
        return f'http://localhost:{self.http_control_api_port}'

    @pytest.fixture(scope='class', autouse=True)
    def start_benchmarking_service(self):
        print('')
        os.system(f'ddbenchmarker -p {self.http_control_api_port} -d')
        time.sleep(2)
        urllib.request.urlopen(f'{self.http_control_api_url}/stop').read()
        time.sleep(2)

    # XXX Running benchmarking tool in the Docker has performance limitations
    # import docker
    # from docker import DockerClient
    # image: str = 'oknyga/ddos-attack-benchmarker:latest'
    # DockerContainer = 'DockerContainer'
    # client: DockerClient = None
    # container: DockerContainer = None
    # @pytest.fixture(scope='class', autouse=True)
    # def start_benchmarking_docker_container(self):
    #     # Warning Make sure you run Docker Daemon!
    #     self.client = docker.from_env()
    #     [container.stop() for container in self.client.containers.list(filters={'ancestor': self.image})]
    #     # docker run -it -p 8000:8000/tcp -p 8080:8080/tcp -p 8053:8053/udp --rm oknyga/ddos-attack-benchmarker:latest -p 8000
    #     self.container = self.client.containers.run(
    #         image=self.image,
    #         command='-p 8000',
    #         detach=True,
    #         ports={
    #             '8000/tcp': self.http_control_api_port,
    #             '8053/udp': self.udp_benchmark_port,
    #             '8080/tcp': self.tcp_benchmark_port,
    #         },
    #     )
    #     # We might need some time to boot
    #     time.sleep(2)
    #     yield
    #     self.container.stop()

    def run(self, type: str, threads_count: int, duration_seconds: int = 10):
        urllib.request.urlopen(f'{self.http_control_api_url}/start?type={type}&port={self.tcp_benchmark_port}').read()
        args = Args(
            threads_count=threads_count,
            targets=[f'{type}://localhost:{self.tcp_benchmark_port}'],
            verbose=False,
            attack_method=f'{type}-flood',
            duration=duration_seconds,
            health_check=0,
        )
        context = dripper(args)
        stats = json.loads(urllib.request.urlopen(f'{self.http_control_api_url}/stop').read())
        return context, stats
    
    def run_set(self, type: str, duration_seconds: int = 10):
        data = [
            # threads_count, requests_per_second, bytes_per_second
            [1, -1, -1],
            [5, -1, -1],
            [10, -1, -1],
            [50, -1, -1],
            [100, -1, -1],
        ]
        print(f'Type: {type}')
        print(f'Test Duration (seconds): {duration_seconds}')
        for i in range(len(data)):
            threads_count = data[i][0]
            context, stats = self.run(
                type=type, threads_count=threads_count, duration_seconds=duration_seconds)
            assert stats['code'] == 200
            assert stats['data']['type'] == type
            requests_per_second = stats['data']['requests']['average']['perSecond']['count']
            bytes_per_second = stats['data']['requests']['average']['perSecond']['bytes']
            data[i][1] = requests_per_second
            data[i][2] = bytes_per_second
            # More threads do not always lead to higher throughput
            # if i > 0:
            #     assert data[i][1] > data[i-1][1]
            #     assert data[i][2] > data[i-1][2]
            print(
                f'Threads Count: {threads_count} / '
                f'Throughput (r/s): {round(requests_per_second, 2)} / '
                f'Throughput (mb/s): {round(bytes_per_second / (10 ** 6), 2)} / '
                f'Average Package (bytes): {round(bytes_per_second / requests_per_second, 2)}'
            )

    def it_http_flood_benchmark(self):
        self.run_set(type='http', duration_seconds=10)

    def it_tcp_flood_benchmark(self):
        self.run_set(type='tcp', duration_seconds=10)

    def it_udp_flood_benchmark(self):
        self.run_set(type='udp', duration_seconds=10)
