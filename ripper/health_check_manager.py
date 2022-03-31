import random
import re
import json
import threading
import urllib
import gzip
import time
import datetime
from collections import defaultdict
from urllib import request

from ripper.constants import HOST_IN_PROGRESS_STATUS, HOST_FAILED_STATUS, HOST_SUCCESS_STATUS
from ripper.headers_provider import HeadersProvider

# Prepare static patterns once at start.
STATUS_PATTERN = re.compile(r"get_check_results\(\n* *'([^']+)")
# Forward ref
Target = 'Target'


def classify_host_status(node_response):
    """Classifies the status of the host based on the regional node information from check-host.net."""
    if node_response is None:
        return HOST_IN_PROGRESS_STATUS
    try:
        if not isinstance(node_response, list) or len(node_response) != 1:
            return HOST_FAILED_STATUS
        value = node_response[0]
        # tcp, udp
        if isinstance(value, dict):
            if 'error' in value:
                return HOST_FAILED_STATUS
            else:
                return HOST_SUCCESS_STATUS
        # http
        if isinstance(value, list) and len(value) == 5:
            return HOST_SUCCESS_STATUS if value[0] == 1 else HOST_FAILED_STATUS
        # ping
        if isinstance(value, list) and len(value) == 4:
            success_cnt = sum([1 if ping[0] == 'OK' else 0 for ping in value])
            return HOST_SUCCESS_STATUS if success_cnt > 1 else HOST_FAILED_STATUS
    except:
        pass
    return None


# TODO Autodetect gzip and move to utils
def fetch_zipped_body(url: str) -> str:
    """Fetches response body in text of the resource with gzip."""
    headers_provider = HeadersProvider()
    http_headers = dict(headers_provider.headers)
    http_headers['User-Agent'] = random.choice(headers_provider.user_agents)
    compressed_resp = urllib.request.urlopen(
        urllib.request.Request(url, headers=http_headers)).read()
    return gzip.decompress(compressed_resp).decode('utf8')


def classify_host_status_http(val):
    """Classifies the status of the host based on the regional node information from check-host.net"""
    if val is None:
        return HOST_IN_PROGRESS_STATUS
    try:
        if isinstance(val, list) and len(val) > 0:
            if 'error' in val[0]:
                return HOST_FAILED_STATUS
            else:
                return HOST_SUCCESS_STATUS
    except:
        pass
    return None


def count_host_statuses(distribution) -> dict[int]:
    """Counter of in progress / failed / successful statuses based on nodes from check-host.net."""
    host_statuses = defaultdict(int)
    for val in distribution.values():
        status = classify_host_status(val)
        host_statuses[status] += 1
    return host_statuses


class HealthCheckManager:
    """Tracks hosts availability state using check-host.net."""
    headers_provider: HeadersProvider = None
    connections_check_time: int
    fetching_host_statuses_in_progress: bool = False
    last_host_statuses_update: datetime = None
    host_statuses = {}

    target: Target = None
    _lock: threading.Lock

    def __init__(self, target: Target) -> None:
        self._lock = threading.Lock()
        self.headers_provider = HeadersProvider()
        self.target = target

    @property
    def health_check_method(self) -> str:
        if self.target.attack_method == 'http-flood':
            return 'http'
        elif self.target.attack_method == 'tcp-flood':
            return 'tcp'
        # udp check had false positives, further research is required
        # elif self.target.attack_method == 'udp-flood':
        #     return 'udp'
        return 'ping'

    @property
    def request_url(self) -> str:
        host = f'{self.target.host_ip}:{self.target.port}'
        if self.health_check_method == 'http':
            # https connection will not be established
            # the plain http request will be sent to https port
            # in some cases it will lead to false negative
            if self.target.port == 443:
                host = f'{self.target.host}'
            else:
                host = f'{self.target.host}:{self.target.port}'
        elif self.health_check_method == 'ping':
            host = self.target.host_ip

        path = f'/check-{self.health_check_method}'
        return f'https://check-host.net{path}?host={host}'

    def get_health_status(self):
        if self.last_host_statuses_update is None or len(self.host_statuses.values()) == 0:
            return f'...detecting\n({self.health_check_method.upper()} health check method from check-host.net)'

        failed_cnt = 0
        succeeded_cnt = 0
        if HOST_FAILED_STATUS in self.host_statuses:
            failed_cnt = self.host_statuses[HOST_FAILED_STATUS]
        if HOST_SUCCESS_STATUS in self.host_statuses:
            succeeded_cnt = self.host_statuses[HOST_SUCCESS_STATUS]

        total_cnt = failed_cnt + succeeded_cnt
        if total_cnt < 1:
            return

        availability_percentage = round(100 * succeeded_cnt / total_cnt)
        accessible_message = f'Accessible in {succeeded_cnt} of {total_cnt} zones ({availability_percentage}%)'
        if availability_percentage < 50:
            accessible_message += f'\n[orange1]It should be dead. Consider another target!'

        return accessible_message

    def fetch_host_statuses(self) -> dict:
        """Fetches regional availability statuses."""
        statuses = {}
        with self._lock:
            try:
                body = fetch_zipped_body(self.request_url)
                # request_code is some sort of trace_id which is provided on every request to master node
                request_code = re.search(STATUS_PATTERN, body)[1]
                # it takes time to poll all information from slave nodes
                time.sleep(5)
                # to prevent loop, do not wait for more than 30 seconds
                for i in range(0, 5):
                    time.sleep(5)
                    resp_data = json.loads(fetch_zipped_body(f'https://check-host.net/check_result/{request_code}'))
                    statuses = count_host_statuses(resp_data)
                    if HOST_IN_PROGRESS_STATUS not in statuses:
                        return statuses
            except:
                pass
        return statuses
