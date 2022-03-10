import socks
import sockshandler
from socket import socket, AF_INET, SOCK_DGRAM, SOCK_STREAM, SOL_TCP, IPPROTO_TCP, TCP_NODELAY
from typing import Optional
import urllib.request

def create_connection(address, timeout=None, source_address=None):
    sock = socks.socksocket()
    sock.connect(address)
    return sock

class SocketManager:
    """Manager for creating and closing sockets."""

    udp_socket: Optional[socket] = None

    def apply_proxy(self):
        # handlers = [gziphandler.GzipHandler]
        # handlers = []
        # handlers.append(sockshandler.SocksHandler(proxy_url=proxy_url))
        # if proxy_url is not None:
        #     scheme = (urllib.parse.urlparse(proxy_url).scheme or "").lower()
        #     if scheme in ("http", "https"):
        #         handlers.append(urllib.request.ProxyHandler({scheme: proxy_url}))
        #     elif scheme in ("socks4", "socks5"):
        #         handlers.append(sockshandler.SocksHandler(proxy_url=proxy_url))
        #     else:
        #         raise RuntimeError("Invalid proxy protocol: {}".format(scheme))

        # if cookie_jar is not None:
        #     handlers.append(urllib.request.HTTPCookieProcessor(cookie_jar))

        # return urllib.request.build_opener(*handlers)
        socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, '45.136.228.80', 6135, True, 'fhghetlr', 'y28lfq0ek85w')
        socket.socket = socks.socksocket
        socket.create_connection = create_connection

        proxy_support = urllib.request.ProxyHandler({'http': 'socks5://fhghetlr:y28lfq0ek85w@45.136.228.80:6135',
                                                     'https': 'socks5://fhghetlr:y28lfq0ek85w@45.136.228.80:6135'})
        opener = urllib.request.build_opener(proxy_support)
        urllib.request.install_opener(opener)

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
