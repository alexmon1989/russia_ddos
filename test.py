import time
import datetime
import docker
import urllib.request

from docker import DockerClient

from ripper.services import dripper
from ripper.constants import *
from ripper.arg_parser import Args

DockerContainer = 'DockerContainer'

image: str = 'oknyga/ddos-attack-benchmarker:latest'
client: DockerClient = None
container: DockerContainer = None

client = docker.from_env()
[container.stop() for container in client.containers.list(
    filters={'ancestor': image})]
# docker run -it -p 8080:80/tcp -p 8053:53/udp --rm oknyga/ddos-attack-benchmarker:latest -p 80
container = client.containers.run(
    image=image,
    command='-p 80',
    detach=True,
    ports={'80/tcp': 8000, '8053/udp': 8053, '8080/tcp': 8080},
)
time.sleep(2)
urllib.request.urlopen(
    'http://localhost:8000/start?type=http&port=8080').read()

print(datetime.datetime.now())
dripper(Args(
    targets=['http://localhost:8080'],
    threads_count=1,
    duration=5,
))
print(datetime.datetime.now())
print(urllib.request.urlopen('http://localhost:8000/stop').read())
#####

urllib.request.urlopen(
    'http://localhost:8000/start?type=tcp&port=8080').read()

print(datetime.datetime.now())
dripper(Args(
    targets=['tcp://localhost:8080'],
    threads_count=1,
    duration=5,
))
print(datetime.datetime.now())
print(urllib.request.urlopen('http://localhost:8000/stop').read())

container.stop()