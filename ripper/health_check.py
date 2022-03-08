import random
import re
import json
import urllib
import gzip
import time
from collections import defaultdict
from ripper.context import Context
from ripper.constants import HOST_IN_PROGRESS_STATUS, HOST_FAILED_STATUS, HOST_SUCCESS_STATUS


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


def count_host_statuses(distribution):
    """Counter of in progress / failed / successful statuses based on nodes from check-host.net"""
    host_statuses = defaultdict(int)
    for val in distribution.values():
        status = classify_host_status(val)
        host_statuses[status] += 1
    return host_statuses


def fetch_zipped_body(_ctx: Context, url: str):
    """Fetches response body in text of the resource with gzip"""
    http_headers = _ctx.headers
    http_headers['User-Agent'] = random.choice(_ctx.user_agents).strip()
    compressed_resp = urllib.request.urlopen(
        urllib.request.Request(url, headers=http_headers)).read()
    return gzip.decompress(compressed_resp).decode('utf8')


def get_health_check_path(attack_method: str):
    if attack_method == 'http':
        return '/check-http'
    elif attack_method == 'tcp':
        return '/check-tcp'
    elif attack_method == 'udp':
        return '/check-udp'
    return '/check-ping'


def fetch_host_statuses(_ctx: Context):
    """Fetches regional availability statuses"""
    statuses = {}
    try:
        request_url = f'https://check-host.net{get_health_check_path(_ctx.attack_method)}?host={_ctx.host_ip}:{_ctx.port}'
        # request_code is some sort of trace_id which is provided on every request to master node
        request_code = re.search(r"get_check_results\(\n* *'([^']+)", fetch_zipped_body(_ctx, request_url))[1]
        # it takes time to poll all information from slave nodes
        time.sleep(5)
        # to prevent loop, do not wait for more than 30 seconds
        for i in range(0, 5):
            time.sleep(5)
            resp_data = json.loads(fetch_zipped_body(_ctx, f'https://check-host.net/check_result/{request_code}'))
            statuses = count_host_statuses(resp_data)
            if HOST_IN_PROGRESS_STATUS not in statuses:
                print(resp_data)
                return statuses
    except:
        pass
    return statuses