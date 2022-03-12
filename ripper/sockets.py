import socks
import sockshandler
import socket
from typing import Optional
import urllib.request
from ripper.proxy import Sock5Proxy


class SocketManager:
    """Manager for creating and closing sockets."""

    udp_socket: Optional[socket.socket] = None

    @staticmethod
    def create_udp_socket(proxy: Sock5Proxy = None) -> socket:
        """Creates udp socket."""
        udp_socket = socks.socksocket(socket.AF_INET, socket.SOCK_DGRAM)
        proxy.decorate_socket(udp_socket) if proxy else 0
        return udp_socket

    @staticmethod
    def create_tcp_socket(proxy: Sock5Proxy = None) -> socket:
        """Returns tcp socket."""
        tcp_sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
        proxy.decorate_socket(tcp_sock) if proxy else 0
        tcp_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        tcp_sock.settimeout(5)
        return tcp_sock

    @staticmethod
    def create_http_socket(proxy: Sock5Proxy = None) -> socket:
        """Returns http socket."""
        http_sock = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
        proxy.decorate_socket(http_sock) if proxy else 0
        http_sock.settimeout(5)
        return http_sock

    def get_udp_socket(self, proxy: Sock5Proxy = None) -> socket:
        """Returns udp socket."""
        if not self.udp_socket:
            self.udp_socket = self.create_udp_socket(proxy)
        return self.udp_socket

    def close_udp_socket(self) -> bool:
        """Closes udp socket if it exists."""
        if self.udp_socket:
            self.udp_socket.close()
            self.udp_socket = None
            return True
        return False
