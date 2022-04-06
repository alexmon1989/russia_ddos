import pytest

from _version import __version__
from ripper.github_updates_checker import GithubUpdatesChecker, Version


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
        assert Version(__version__) <= versions[-1]
    
    def it_can_read_last_version(self):
        guc = GithubUpdatesChecker()
        last_version = guc.fetch_lastest_version()
        assert Version(__version__) <= last_version

    def it_can_get_str_version(self):
        assert Version('2.3.1').version == '2.3.1'