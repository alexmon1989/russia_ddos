import pytest
import time
import docker
import urllib.request
from collections import namedtuple
from docker import DockerClient

from ripper.services import start
from ripper.constants import *

Args = namedtuple(
    'Args', 'targets targets_list http_method attack_method threads_count dry_run min_random_packet_len max_random_packet_len proxy_list socket_timeout proxy_type health_check duration log_size event_level')
DockerContainer = 'DockerContainer'

class DescribeBenchmark:
    image: str = 'oknyga/ddos-attack-benchmarker:latest'
    client: DockerClient = None
    container: DockerContainer = None

    @pytest.fixture(scope='session', autouse=True)
    def refresh_headers_provider(self):
        self.client = docker.from_env()
        [container.stop() for container in self.client.containers.list(filters={'ancestor': self.image})]
        # docker run -it -p 8080:80/tcp -p 8053:53/udp --rm oknyga/ddos-attack-benchmarker:latest -p 80
        self.container = self.client.containers.run(
            image=self.image,
            command='-p 80',
            detach=True,
            ports={'80/tcp': 8000, '8053/udp': 8053, '8080/tcp': 8080},
        )
        time.sleep(5)
        urllib.request.urlopen('http://localhost:8000/start?type=http&port=8080').read()
        yield
        self.container.stop()

    def it_http_flood_benchmark(self):
        start(Args(
            targets=['http://localhost:8080'],
            targets_list=None,
            min_random_packet_len=None,
            max_random_packet_len=None,
            proxy_list=None,
            proxy_type=ARGS_DEFAULT_PROXY_TYPE,
            health_check=ARGS_DEFAULT_HEALTH_CHECK,
            socket_timeout=ARGS_DEFAULT_SOCK_TIMEOUT,
            dry_run=None,
            log_size=DEFAULT_LOG_SIZE,
            event_level=DEFAULT_LOG_LEVEL,
            attack_method='http-flood',
            http_method='GET',
            threads_count=1,
            duration=5,
        ))
        print(urllib.request.urlopen('http://localhost:8000/stop').read())
        print('123')
        assert False
