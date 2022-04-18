import re
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
        return f'https://raw.githubusercontent.com/{self._owner}/{self._repo}/main/_version.py'

    def fetch_latest_version(self) -> Version:
        try:
            request = urllib.request.Request(url=self.get_request_url())
            raw: str = urllib.request.urlopen(request).read().decode('utf8')
            ver = re.search(r"(\d+\.\d+\.\d+)", raw).group(0)
            self.latest_version = Version(ver)
        except:
            return None

        return self.latest_version

    def demon_update_latest_version(self):
        threading.Thread(target=self.fetch_latest_version).start()
