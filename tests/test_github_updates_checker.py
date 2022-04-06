import pytest

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
        assert Version('2.4.0') <= versions[-1]
