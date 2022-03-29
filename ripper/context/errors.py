import hashlib
from datetime import datetime

from ripper.constants import *


class Error:
    """Class with Error details."""
    uuid: str = None
    """UUID for Error, based on error details."""
    time: datetime = None
    """Error time."""
    code: str = None
    """Error type or process/operation short name"""
    count: int = 0
    """Error count."""
    message: str = ''
    """Error message"""

    def __init__(self, code: str, message: str, count: int = 1):
        """
        :param code: Error type.
        :param message: Error message.
        :param count: Error counter.
        """
        self.uuid = hashlib.sha1(f'{code}{message}'.encode()).hexdigest()
        self.time = datetime.now()
        self.code = code
        self.count = count
        self.message = message

class IPWasChangedError(Error):
    def __init__(self, count: int = 1):
        """
        :param count: Error counter.
        """
        super().__init__(code='IP was changed', message=YOUR_IP_WAS_CHANGED_ERR_MSG, count=count)
