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
    def __init__(self, message=YOUR_IP_WAS_CHANGED_ERR_MSG, count: int = 1):
        """
        :param message: Error message.
        :param count: Error counter.
        """
        super().__init__(code='IP was changed', message=message, count=count)


class HostDoesNotRespondError(Error):
    def __init__(self, message: str, count: int = 1):
        """
        :param message: Error message.
        :param count: Error counter.
        """
        super().__init__(code='Host does not respond', message=message, count=count)


class HttpSendError(Error):
    def __init__(self, message: str, count: int = 1):
        """
        :param message: Error message.
        :param count: Error counter.
        """
        super().__init__(code='HTTP send Err', message=message, count=count)


class TcpSendError(Error):
    def __init__(self, message: str, count: int = 1):
        """
        :param message: Error message.
        :param count: Error counter.
        """
        super().__init__(code='TCP send Err', message=message, count=count)


class CheckTcpAttackError(Error):
    def __init__(self, message: str, count: int = 1):
        """
        :param message: Error message.
        :param count: Error counter.
        """
        super().__init__(code='Check TCP attack', message=message, count=count)


class UdpSendError(Error):
    def __init__(self, message: str, count: int = 1):
        """
        :param message: Error message.
        :param count: Error counter.
        """
        super().__init__(code='UDP send Err', message=message, count=count)


class ProxyListReadOperationFailedError(Error):
    def __init__(self, message: str, count: int = 1):
        """
        :param message: Error message.
        :param count: Error counter.
        """
        super().__init__(code='Proxy list read operation failed', message=message, count=count)