import os

import pytest
import time

from ripper.github_updates_checker import GithubUpdatesChecker, Version


@pytest.mark.skipif(os.getenv('CI') == 'true', reason='May freeze CI test...')
class DescribeGithubUpdatesChecker:
    def it_can_read_tag_names(self):
        guc = GithubUpdatesChecker()
        tag_names = guc.fetch_tag_names()
        assert len(tag_names) > 0
        assert isinstance(tag_names[0], str)

    def it_can_read_versions(self):
        guc = GithubUpdatesChecker()
        versions = guc.fetch_versions()
        assert len(versions) > 0
        assert Version('1.0.0') <= versions[-1]

    def it_can_read_latest_version(self):
        guc = GithubUpdatesChecker()
        latest_version = guc.fetch_lastest_version()
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
