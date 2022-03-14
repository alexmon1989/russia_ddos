import random
import re
import json
import urllib
import gzip
import time
from collections import defaultdict
from ripper.context import Context
from ripper.constants import HOST_IN_PROGRESS_STATUS, HOST_FAILED_STATUS, HOST_SUCCESS_STATUS


def get_health_status(_ctx: Context):
    if _ctx.last_host_statuses_update is None or len(_ctx.host_statuses.values()) == 0:
        return f'...detecting\n({_ctx.health_check_method.upper()} health check method from check-host.net)'

    failed_cnt = 0
    succeeded_cnt = 0
    if HOST_FAILED_STATUS in _ctx.host_statuses:
        failed_cnt = _ctx.host_statuses[HOST_FAILED_STATUS]
    if HOST_SUCCESS_STATUS in _ctx.host_statuses:
        succeeded_cnt = _ctx.host_statuses[HOST_SUCCESS_STATUS]

    total_cnt = failed_cnt + succeeded_cnt
    if total_cnt < 1:
        return

    availability_percentage = round(100 * succeeded_cnt / total_cnt)
    accessible_message = f'Accessible in {succeeded_cnt} of {total_cnt} zones ({availability_percentage}%)'
    if availability_percentage < 50:
        accessible_message += f'\n[orange1]It should be dead. Consider another target!'

    return accessible_message


def classify_host_status(node_response):
    """Classifies the status of the host based on the regional node information from check-host.net"""
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
    """Counter of in progress / failed / successful statuses based on nodes from check-host.net"""
    host_statuses = defaultdict(int)
    for val in distribution.values():
        status = classify_host_status(val)
        host_statuses[status] += 1
    return host_statuses


def fetch_zipped_body(_ctx: Context, url: str) -> str:
    """Fetches response body in text of the resource with gzip"""
    http_headers = _ctx.headers
    http_headers['User-Agent'] = random.choice(_ctx.user_agents).strip()
    compressed_resp = urllib.request.urlopen(
        urllib.request.Request(url, headers=http_headers)).read()
    return gzip.decompress(compressed_resp).decode('utf8')


def get_health_check_method(attack_method: str) -> str:
    if attack_method == 'http':
        return 'http'
    elif attack_method == 'tcp':
        return 'tcp'
    # udp check had false positives, further research is required
    # elif attack_method == 'udp':
    #     return 'udp'
    return 'ping'


def construct_request_url(_ctx: Context) -> str:
    host = f'{_ctx.host_ip}:{_ctx.port}'
    if _ctx.health_check_method == 'http':
        # https connection will not be established
        # the plain http request will be sent to https port
        # in some cases it will lead to false negative
        if _ctx.port == 443:
            host = f'{_ctx.host}'
        else:
            host = f'{_ctx.host}:{_ctx.port}'
    elif _ctx.health_check_method == 'ping':
        host = _ctx.host_ip

    path = f'/check-{_ctx.health_check_method}'
    return f'https://check-host.net{path}?host={host}'


def fetch_host_statuses(_ctx: Context) -> dict:
    """Fetches regional availability statuses"""
    statuses = {}
    try:
        request_url = construct_request_url(_ctx)
        body = fetch_zipped_body(_ctx, request_url)
        # request_code is some sort of trace_id which is provided on every request to master node
        request_code = re.search(r"get_check_results\(\n* *'([^']+)", body)[1]
        # it takes time to poll all information from slave nodes
        time.sleep(5)
        # to prevent loop, do not wait for more than 30 seconds
        for i in range(0, 5):
            time.sleep(5)
            resp_data = json.loads(fetch_zipped_body(_ctx, f'https://check-host.net/check_result/{request_code}'))
            statuses = count_host_statuses(resp_data)
            if HOST_IN_PROGRESS_STATUS not in statuses:
                return statuses
    except:
        pass
    return statuses
