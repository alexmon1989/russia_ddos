import socks
import sockshandler
import socket
from typing import Optional
import urllib.request


class Sock5Proxy:
    def __init__(self, host: str, port: int, user: str = None, password: str = None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password


class SocketManager:
    """Manager for creating and closing sockets."""

    udp_socket: Optional[socket.socket] = None

    @staticmethod
    def open_socket(args, proxy: Sock5Proxy = None):
        s = socks.socksocket(*args)
        if proxy:
            s.set_proxy(socks.PROXY_TYPE_SOCKS5, proxy.host, proxy.port, True, proxy.user, proxy.password)
        return s

    @staticmethod
    def create_udp_socket(proxy: Sock5Proxy = None) -> socket:
        """Creates udp socket."""
        udp_socket = SocketManager.open_socket([socket.AF_INET, socket.SOCK_DGRAM], proxy)
        return udp_socket

    @staticmethod
    def create_tcp_socket(proxy: Sock5Proxy = None) -> socket:
        """Returns tcp socket."""
        tcp_sock = SocketManager.open_socket([socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP], proxy)
        tcp_sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        tcp_sock.settimeout(5)
        return tcp_sock

    @staticmethod
    def create_http_socket(proxy: Sock5Proxy = None) -> socket:
        """Returns http socket."""
        http_sock = SocketManager.open_socket([socket.AF_INET, socket.SOCK_STREAM], proxy)
        http_sock.settimeout(5)
        return http_sock

    def get_udp_socket(self) -> socket:
        """Returns udp socket."""
        if not self.udp_socket:
            self.udp_socket = self.create_udp_socket()
        return self.udp_socket

    def close_udp_socket(self) -> bool:
        """Closes udp socket if it exists."""
        if self.udp_socket:
            self.udp_socket.close()
            self.udp_socket = None
            return True
        return False
