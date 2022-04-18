import pytest
import time

from ripper.github_updates_checker import GithubUpdatesChecker, Version


class DescribeGithubUpdatesChecker:
    def it_can_read_latest_version(self):
        guc = GithubUpdatesChecker()
        latest_version = guc.fetch_latest_version()
        assert Version('1.0.0') <= latest_version

    def it_can_get_str_version(self):
        assert Version('2.3.1').version == '2.3.1'

    def it_can_read_latest_version_on_background(self):
        guc = GithubUpdatesChecker()
        guc.demon_update_latest_version()

        for _ in range(5):
            if guc.latest_version is None:
                time.sleep(1)
            else:
                break
        if guc.latest_version is None:
            # rate limiter
            assert False
        assert Version('1.0.0') <= guc.latest_version
