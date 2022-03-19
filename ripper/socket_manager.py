import socks
import socket

from ripper.proxy import Proxy


class SocketManager:
    """Manager for creating and closing sockets."""

    udp_socket: socket.socket = None
    """Shared socket.socket"""
    socket_timeout: int = None
    """Timeout for socket connection is seconds."""

    def __init__(self, socket_timeout: int = None):
        self.socket_timeout = socket_timeout

    def create_udp_socket(self) -> socket:
        """Creates udp socket."""
        # There is issues with UDP protocol vie PySock library
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return udp_socket

    def create_tcp_socket(self, proxy: Proxy = None) -> socket:
        """Returns tcp socket."""
        tcp_socket = socks.socksocket(
            socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
        proxy.decorate_socket(tcp_socket) if proxy is not None else 0
        tcp_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        tcp_socket.settimeout(self.socket_timeout) if self.socket_timeout is not None else 0
        return tcp_socket

    def get_udp_socket(self) -> socket:
        """Returns udp socket."""
        if self.udp_socket is None:
            self.udp_socket = self.create_udp_socket()
        return self.udp_socket

    def close_udp_socket(self) -> bool:
        """Closes udp socket if it exists."""
        if self.udp_socket is not None:
            self.udp_socket.close()
            self.udp_socket = None
            return True
        return False
