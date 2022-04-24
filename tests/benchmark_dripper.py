import pytest
import time
import json
import docker
import urllib.request

from docker import DockerClient

from ripper.services import start_dripper
from ripper.constants import *
from ripper.arg_parser import Args

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
        time.sleep(2)
        yield
        self.container.stop()

    def it_http_flood_benchmark(self):
        urllib.request.urlopen('http://localhost:8000/start?type=http&port=8080').read()
        start_dripper(Args(
            targets=['http://localhost:8080'],
            threads_count=1,
            duration=10,
        ))
        stats = json.loads(urllib.request.urlopen('http://localhost:8000/stop').read())
        assert stats['code'] == 200
        assert stats['data']['type'] == 'http'
        assert stats['data']['duration']['seconds'] >= 10
        # On 2.3 GHz Quad-Core Intel Core i7 2022-04-24 >= 45066
        # I expect any CPU to perfrom at least 10 times slower
        assert stats['data']['requests']['total']['count'] > 45066 / 10
        assert stats['data']['requests']['total']['bytes'] > 227360183818 / 10
        assert stats['data']['requests']['average']['perSecond']['count'] > 4091 / 10
        assert stats['data']['requests']['average']['perSecond']['bytes'] > 20642834920 / 10
