import os
import json
import urllib.request
import threading

from ripper.constants import *


class Version:
    @staticmethod
    def validate(version: str):
        parts = version.split('.')
        if len(parts) != 3:
            return False
        for ps in parts:
            if not ps.isdigit():
                return False
        return True

    _parts: list[int] = None

    def __init__(self, version: str):
        if not Version.validate(version):
            raise ValueError()
        self._parts = [int(ps) for ps in version.split('.')]

    @property
    def version(self):
        return '.'.join([str(ps) for ps in self._parts])

    def calc_positional_value(self):
        if not self._parts:
            return 0
        return self._parts[2] + self._parts[1] * 1000 + self._parts[0] * 1000_000

    def __ge__(self, other):
        return self.calc_positional_value() >= other.calc_positional_value()

    def __lt__(self, other):
        return self.calc_positional_value() < other.calc_positional_value()

    def __eq__(self, other):
        return self.calc_positional_value() == other.calc_positional_value()


class GithubUpdatesChecker:
    _owner: str = ''
    _repo: str = ''
    latest_version: Version = None

    def __init__(self, owner: str = GITHUB_OWNER, repo: str = GITHUB_REPO):
        self._owner = owner
        self._repo = repo

    def get_request_url(self):
        return f'https://api.github.com/repos/{self._owner}/{self._repo}/git/refs/tags'

    def fetch_tags_data(self):
        url = self.get_request_url()
        try:
            request = urllib.request.Request(url=url, headers=self._get_headers())
            raw = urllib.request.urlopen(request).read().decode('utf8')
            data = json.loads(raw)
        except:
            data = []
        return data

    def _get_headers(self):
        return {
            'Authorization': f'Bearer {os.getenv("GITHUB_TOKEN", "dummy-token")}'
        }

    def _ref_to_tag_name(self, ref: str):
        return ''.join(ref.split('/')[2:])

    def fetch_tag_names(self) -> list[str]:
        tags_data = self.fetch_tags_data()
        return [self._ref_to_tag_name(data['ref']) for data in tags_data]

    def fetch_versions(self) -> list[Version]:
        tag_names = self.fetch_tag_names()
        return [Version(vs) for vs in filter(lambda tag_name: Version.validate(tag_name), tag_names)]

    def fetch_lastest_version(self) -> Version:
        versions = self.fetch_versions()
        if not versions or len(versions) < 1:
            return None
        self.latest_version = versions[-1]
        return self.latest_version

    def demon_update_latest_version(self):
        threading.Thread(target=self.fetch_lastest_version).start()
