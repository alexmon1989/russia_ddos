import socks
import socket

from ripper.proxy import Sock5Proxy


class SocketManager:
    """Manager for creating and closing sockets."""

    udp_sockets: dict[str, socks.socksocket] = {}

    @staticmethod
    def create_udp_socket(proxy: Sock5Proxy = None) -> socket:
        """Creates udp socket."""
        udp_socket = socks.socksocket(socket.AF_INET, socket.SOCK_DGRAM)
        proxy.decorate_socket(udp_socket) if proxy else 0
        return udp_socket

    @staticmethod
    def create_tcp_socket(proxy: Sock5Proxy = None) -> socket:
        """Returns tcp socket."""
        tcp_socket = socks.socksocket(
            socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
        proxy.decorate_socket(tcp_socket) if proxy else 0
        tcp_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        tcp_socket.settimeout(5)
        return tcp_socket

    @staticmethod
    def create_http_socket(proxy: Sock5Proxy = None) -> socket:
        """Returns http socket."""
        http_socket = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
        proxy.decorate_socket(http_socket) if proxy else 0
        http_socket.settimeout(5)
        return http_socket

    def get_udp_socket(self, proxy: Sock5Proxy = None) -> socket:
        """Returns udp socket."""
        id = proxy.id() if proxy is not None else ''
        if id not in self.udp_sockets:
            self.udp_sockets[id] = self.create_udp_socket(proxy)
        return self.udp_sockets[id]

    def close_udp_socket(self, proxy) -> bool:
        """Closes udp socket if it exists."""
        id = proxy.id() if proxy is not None else ''
        if id not in self.udp_sockets:
            self.udp_sockets[id].close()
            del self.udp_sockets[id]
            return True
        return False
