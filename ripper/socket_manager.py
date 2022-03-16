import socks
import socket

from ripper.proxy import Sock5Proxy


class SocketManager:
    """Manager for creating and closing sockets."""

    udp_sockets: dict[str, socks.socksocket] = {}
    """Maps proxy (id) to socket"""
    socket_timeout: int = None
    """Timeout for socket connection is seconds."""

    def __init__(self, socket_timeout: int = None):
        self.socket_timeout = socket_timeout

    def create_udp_socket(self, proxy: Sock5Proxy = None) -> socket:
        """Creates udp socket."""
        # There is issues with UDP protocol vie PySock library
        # udp_socket = socks.socksocket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        proxy.decorate_socket(udp_socket) if proxy is not None else 0
        return udp_socket

    def create_tcp_socket(self, proxy: Sock5Proxy = None) -> socket:
        """Returns tcp socket."""
        tcp_socket = socks.socksocket(
            socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
        proxy.decorate_socket(tcp_socket) if proxy is not None else 0
        tcp_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        tcp_socket.settimeout(self.socket_timeout) if self.socket_timeout is not None else 0
        return tcp_socket

    def get_udp_socket(self, proxy: Sock5Proxy = None) -> socket:
        """Returns udp socket."""
        id = proxy.id() if proxy is not None else ''
        if id not in self.udp_sockets:
            self.udp_sockets[id] = self.create_udp_socket(proxy)
        return self.udp_sockets[id]

    def close_udp_socket(self, proxy: Sock5Proxy = None) -> bool:
        """Closes udp socket if it exists."""
        id = proxy.id() if proxy is not None else ''
        if id not in self.udp_sockets:
            self.udp_sockets[id].close()
            del self.udp_sockets[id]
            return True
        return False
