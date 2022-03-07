import pytest as pytest
from ripper.health_check import classify_host_status, count_host_statuses
from ripper.constants import HOST_IN_PROGRESS_STATUS, HOST_FAILED_STATUS, HOST_SUCCESS_STATUS


@pytest.mark.parametrize('value, status', [
    (None, HOST_IN_PROGRESS_STATUS),
    ([{'error': 'Connection timed out'}], HOST_FAILED_STATUS),
    ([{'address': '4.2.2.2', 'time': 0.040173 }], HOST_SUCCESS_STATUS),
])
def test_classify_host_status(value, status):
    assert classify_host_status(value) == status


@pytest.mark.parametrize('distribution, statuses_count', [
    ({"at1.node.check-host.net": [{"address": "95.173.136.72","time": 0.067267}],
      "ch1.node.check-host.net": [{"address": "95.173.136.72","time": 0.080538}],
      "de4.node.check-host.net": [{"address": "95.173.136.72","time": 1.078855}],
      "ir1.node.check-host.net": [{'error': 'Connection timed out'}],
      "it2.node.check-host.net": [{"address": "95.173.136.71","time": 0.063825}],
      "md1.node.check-host.net": [{"address": "95.173.136.70","time": 0.159452}],
      "nl1.node.check-host.net": [{'error': 'Connection timed out'}],
      "us1.node.check-host.net": None,
      "us2.node.check-host.net": [{"address": "95.173.136.70","time": 0.13008}]},
      {
          'HOST_IN_PROGRESS': 1,
          'HOST_FAILED': 2,
          'HOST_SUCCESS': 6
      }),
    ({}, {}),
])
def test_count_host_statuses(distribution, statuses_count):
    actual = count_host_statuses(distribution)
    assert len(actual) == len(statuses_count)
    for (key, value) in statuses_count.items():
        assert actual[key] == value