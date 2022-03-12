import socks
import socket

def create_connection(address, timeout=None, source_address=None):
    sock = socks.socksocket()
    sock.connect(address)
    return sock

socks.set_default_proxy(socks.SOCKS5, '45.136.228.80', 6135, True, 'fhghetlr', 'y28lfq0ek85w')
socket.socket = socks.socksocket
socket.create_connection = create_connection
import urllib3

try:
    s = socks.socksocket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("ifconfig.me", 443))

    message = b'GET / HTTP/1.0\r\n\r\n'
    s.sendall(message)

    reply = s.recv(4069)
    print(reply)
except Exception as e:
    print(e)