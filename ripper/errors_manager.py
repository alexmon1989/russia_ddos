from ripper.errors import Error
from collections import defaultdict


def merge_error_dicts(d1: dict[str, Error], d2: dict[str, Error]):
    """Creates copy of the first dict and extends."""
    merged_errors = {}
    for (uuid, error) in d1.items():
        merged_errors[uuid] = error.clone()
    for (uuid, error) in d2.items():
        if uuid in merged_errors:
            merged_errors[uuid].count += error.count
            merged_errors[uuid].time = max(merged_errors[uuid].time, error.time)
        else:
            merged_errors[uuid] = error.clone()
    return merged_errors


class ErrorsManager:
    _errors: dict[str, Error] = None
    """All errors collected in runtime."""

    _submanagers: list['ErrorsManager'] = None
    """
    Error Managers could have lower-level sub-managers.
    It looks like a tree.
        EM   - Context error manager (aggregates submanagers)
     /  |   \
    EM  ...  EM   - Target error managers
    It allows targets to be isolated for context.
    """

    def __init__(self) -> None:
        self._errors = defaultdict(dict[str, Error])
        self._submanagers = []

    def add_submanager(self, submanager: 'ErrorsManager') -> bool:
        """Adds submanager."""
        if self.has_submanager(submanager):
            return False
        self._submanagers.append(submanager)
        return True
    
    def add_submanagers(self, submanagers: list['ErrorsManager']) -> int:
        """Adds submanagers."""
        added_cnt = 0
        for sub in submanagers:
            if self.add_submanager(sub):
                added_cnt += 1
        return added_cnt

    def has_submanager(self, submanager: 'ErrorsManager') -> bool:
        if submanager in self._submanagers:
            return True
        for submanager in self._submanagers:
            if submanager.has_submanager(submanager):
                return True
        return False

    @property
    def errors(self) -> dict[str, Error]:
        """All properties including submanager nodes."""
        # TODO add caching
        united_errors = merge_error_dicts({}, self._errors)
        for submanager in self._submanagers:
            if submanager.has_errors():
                united_errors = merge_error_dicts(united_errors, submanager.errors)
        return united_errors

    def clear_errors(self):
        """Removes all errors, including submanagers."""
        self._errors.clear()
        for submanager in self._submanagers:
            submanager.clear_errors()

    def add_error(self, error: Error):
        """
        Add Error to Error collection without duplication to the current error level.
        If Error exists in collection - it updates the error counter.
        """
        if self._errors.__contains__(error.uuid):
            self._errors[error.uuid].count += 1
            self._errors[error.uuid].time = error.time
        else:
            self._errors[error.uuid] = error
    
    def find_error(self, error_uuid: str):
        """Recursive lookup for error with specified error_uuid."""
        if self.errors.__contains__(error_uuid):
            return self.errors[error_uuid]
        return None

    def remove_error(self, error_uuid: str):
        """Remove Error from collection by Error Code."""
        if self._errors.__contains__(error_uuid):
            self._errors.__delitem__(error_uuid)
        for submanager in self._submanagers:
            submanager.remove_error(error_uuid)

    def has_errors(self) -> bool:
        """Check if Errors are exists."""
        cnt = len(self._errors) > 0
        if cnt > 0:
            return True
        for submanager in self._submanagers:
            if submanager.has_errors():
                return True
        return False
