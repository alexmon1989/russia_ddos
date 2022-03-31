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

#
#          EM   - Context error manager (aggregates children nodes)
#       /  |   \
#     EM  ...  EM   - Target error managers
#
class ErrorsManager:
    _errors: dict[str, Error] = None
    """All errors collected in runtime."""

    _children: list['ErrorsManager'] = None

    def __init__(self) -> None:
        # self._errors = {}
        self._errors = defaultdict(dict[str, Error])
        self._children = []

    def append_child(self, child: 'ErrorsManager'):
        """Adds child node."""
        if self.has_child(child):
            return False
        self._children.append(child)
        return True
    # TODO Append children
    
    def has_child(self, child: 'ErrorsManager') -> bool:
        if child in self._children:
            return True
        for child in self._children:
            if child.has_child(child):
                return True
        return False

    # TODO add caching
    @property
    def errors(self) -> dict[str, Error]:
        """All properties including child nodes."""
        united_errors = {} | self._errors
        for child in self._children:
            if child.has_errors():
                united_errors = united_errors | child.errors
        return united_errors

    def clear_errors(self):
        """Removes all errors, including children."""
        self._errors.clear()
        for child in self._children:
            child.clear_errors()
    
    # def get_errors(self, error_uuid: str) -> list[Error]:
    #     """Reads all errors with uuid provided from current manager and children"""
    #     errors = [self._errors.get(error_uuid)]
    #     for child in self._children:
    #         errors.append(*child.get_errors(error_uuid))
    #     return errors

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
    
    def find_error(self, error_uuid: Error):
        """Recursive lookup for error with specified error_uuid."""
        if self._errors.__contains__(error_uuid):
            return self._errors[error_uuid]
        for child in self._children:
            error = child.find_error(error_uuid)
            if error:
                return error
        return None

    def remove_error(self, error_code: str):
        """Remove Error from collection by Error Code."""
        if self._errors.__contains__(error_code):
            self._errors.__delitem__(error_code)
        for child in self._children:
            child.remove_error(error_code)

    def has_errors(self) -> bool:
        """Check if Errors are exists."""
        cnt = len(self._errors) > 0
        if cnt > 0:
            return True
        for child in self._children:
            if child.has_errors():
                return True
        return False
