from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, SOL_TCP, IPPROTO_TCP, TCP_NODELAY
from typing import Optional


class SocketManager:
    """Manager for creating and closing sockets."""

    udp_socket: Optional[socket] = None

    def get_udp_socket(self) -> socket:
        """Returns udp socket."""
        if not self.udp_socket:
            self.udp_socket = self.create_udp_socket()
        return self.udp_socket

    @staticmethod
    def create_udp_socket() -> socket:
        """Creates udp socket."""
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        return udp_socket

    def close_udp_socket(self) -> bool:
        """Closes udp socket if it exists."""
        if self.udp_socket:
            self.udp_socket.close()
            self.udp_socket = None
            return True
        return False

    @staticmethod
    def create_tcp_socket() -> socket:
        """Returns tcp socket."""
        tcp_sock = socket(AF_INET, SOCK_STREAM, SOL_TCP)
        tcp_sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
        tcp_sock.settimeout(5)
        return tcp_sock
