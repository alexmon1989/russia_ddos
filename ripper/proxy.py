from socks import PROXY_TYPE_SOCKS5
from ripper.common import readfile
from typing import List

class Sock5Proxy:
    def __init__(self, host: str, port: int, username: str = None, password: str = None, rdns: bool = True):
      self.host = host
      self.port = int(port)
      self.username = username
      self.password = password
      self.rdns = rdns

    # mutates socket
    # https://pypi.org/project/PySocks/
    def decorate_socket(self, s):
      if self.username and self.password:
        s.set_proxy(PROXY_TYPE_SOCKS5, self.host, self.port, self.rdns, self.username, self.password)
      else:
        s.set_proxy(PROXY_TYPE_SOCKS5, self.host, self.port, self.rdns)
      return s


def read_proxy_list(filename: str) -> List[Sock5Proxy]:
  proxy_list = []
  lines = readfile(filename)
  for line in lines:
    # ip:port:username:password or ip:port
    ip, port, username, password = line.strip().split(':')
    proxy = Sock5Proxy(host=ip, port=port, username=username, password=password)
    proxy_list.append(proxy)
  return proxy_list
