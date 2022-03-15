import sys
from optparse import OptionParser

from ripper.constants import *


def create_parser() -> OptionParser:
    """Initialize parser with options."""
    parser = OptionParser(usage=USAGE, epilog=EPILOG)
    parser_add_options(parser)

    return parser


def parser_add_options(parser: OptionParser) -> None:
    """Add options to a parser."""
    parser.add_option('-p', '--port',
                      dest='port', type='int', default=80,
                      help='port (default: 80)')
    parser.add_option('-t', '--threads',
                      dest='threads', type='int', default=100,
                      help='threads (default: 100)')
    parser.add_option('-r', '--random_len',
                      dest='random_packet_len', type='int', default=1,
                      help='Send random packets with random length (default: 1')
    parser.add_option('-l', '--max_random_packet_len',
                      # default value is not set here to keep dynamic logic during initialization
                      dest='max_random_packet_len', type='int',
                      help='Max random packets length (Default: 48 for udp, 1000 for tcp)')
    parser.add_option('-m', '--method',
                      dest='attack_method', type='str', default='udp',
                      help='Attack method: udp (Default), tcp, http')
    parser.add_option('-s', '--server',
                      dest='host',
                      help='Attack to server IP')
    parser.add_option('-y', '--proxy_list',
                      dest='proxy_list',
                      help='File with sock5 proxies in ip:port:username:password line format')
    parser.add_option('-c', '--health_check',
                      dest='health_check', type='int', default=1,
                      help='Controls health check availability. Turn on: 1, turn off: 0. Default: 1')
    parser.add_option('-e', '--http_method',
                      dest='http_method', type='str', default='GET',
                      help='HTTP method. Default: GET')
    parser.add_option('-a', '--http_path',
                      dest='http_path', type='str', default='/',
                      help='HTTP path. Default: /')
    parser.add_option('-o', '--socket_timeout',
                      # default value is not set here to keep dynamic logic during initialization
                      dest='socket_timeout', type='int',
                      help='Timeout for socket connection is seconds. Default (seconds): 10 without proxy, 20 with proxy')


def print_usage():
    """Wrapper for Logo with help."""
    print(LOGO_NOCOLOR)
    create_parser().print_help()

    sys.exit()

