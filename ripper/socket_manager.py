import socks
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, SOL_TCP, IPPROTO_TCP, TCP_NODELAY

from ripper.proxy import Proxy


class SocketManager:
    """Manager for creating and closing sockets."""

    _socket: socket = None
    """Shared socket"""
    socket_timeout: int = None
    """Timeout for socket connection is seconds."""

    def __init__(self, socket_timeout: int = None):
        self.socket_timeout = socket_timeout

    def create_udp_socket(self) -> socket:
        """Creates udp socket."""
        # There is issues with UDP protocol via PySock library
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        udp_socket.settimeout(self.socket_timeout) if self.socket_timeout is not None else 0

        return udp_socket

    def create_tcp_socket(self, proxy: Proxy = None) -> socket:
        """Returns tcp socket."""
        tcp_socket = socks.socksocket(AF_INET, SOCK_STREAM, SOL_TCP)

        proxy.decorate_socket(tcp_socket) if proxy is not None else 0

        tcp_socket.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
        tcp_socket.settimeout(self.socket_timeout) if self.socket_timeout is not None else 0

        return tcp_socket

    def get_udp_socket(self) -> socket:
        """Returns shared UDP socket."""
        if self._socket is None:
            self._socket = self.create_udp_socket()

        return self._socket

    def get_tcp_socket(self, proxy: Proxy = None) -> socket:
        """Returns shared TCP socket."""
        if self._socket is None:
            self._socket = self.create_tcp_socket(proxy)

        return self._socket

    def close_socket(self) -> bool:
        """Closes udp socket if it exists."""
        if self._socket is not None:
            self._socket.close()
            self._socket = None
            return True
        return False
