import sys
from optparse import OptionParser

from ripper.constants import *
from ripper.actions.attack import attack_method_labels


def create_parser() -> OptionParser:
    """Initialize parser with options."""
    parser = OptionParser(usage=USAGE, epilog=EPILOG, version=f'%prog {VERSION}')
    parser_add_options(parser)

    return parser


def parser_add_options(parser: OptionParser) -> None:
    """Add options to a parser."""
    parser.add_option('-s', '--target',
                      dest='target',
                      help='Attack target in {scheme}://{hostname}[:{port}][{path}] format')
    parser.add_option('-m', '--method',
                      dest='attack_method', type='str',
                      help=f'Attack method: {", ".join(attack_method_labels)}')
    parser.add_option('-e', '--http_method',
                      dest='http_method', type='str', default=ARGS_DEFAULT_HTTP_ATTACK_METHOD,
                      help=f'HTTP method. Default: {ARGS_DEFAULT_HTTP_ATTACK_METHOD}')
    parser.add_option('-t', '--threads',
                      dest='threads', type='int', default=ARGS_DEFAULT_THREADS,
                      help=f'threads. Default: {ARGS_DEFAULT_THREADS}')
    parser.add_option('-r', '--random_len',
                      dest='random_packet_len', type='int', default=ARGS_DEFAULT_RND_PACKET_LEN,
                      help=f'Send random packets with random length. Default: {ARGS_DEFAULT_RND_PACKET_LEN}')
    parser.add_option('-l', '--max_random_packet_len',
                      dest='max_random_packet_len', type='int', default=ARGS_DEFAULT_MAX_RND_PACKET_LEN,
                      help=f'Max random packets length. Default: {ARGS_DEFAULT_MAX_RND_PACKET_LEN} for udp/tcp')
    parser.add_option('-y', '--proxy_list',
                      dest='proxy_list',
                      help='File (fs or http/https) with proxies in ip:port:username:password line format. Proxies will be ignored in udp attack!')
    parser.add_option('-k', '--proxy_type',
                      dest='proxy_type', type='str', default=ARGS_DEFAULT_PROXY_TYPE,
                      help=f'Type of proxy to work with. Supported types: socks5, socks4, http. Default: {ARGS_DEFAULT_PROXY_TYPE}')
    parser.add_option('-c', '--health_check',
                      dest='health_check', type='int', default=ARGS_DEFAULT_HEALTH_CHECK,
                      help=f'Controls health check availability. Turn on: 1, turn off: 0. Default: {ARGS_DEFAULT_HEALTH_CHECK}')
    parser.add_option('-o', '--socket_timeout',
                      # default value is not set here to keep dynamic logic during initialization
                      dest='socket_timeout', type='int', default=ARGS_DEFAULT_SOCK_TIMEOUT,
                      help=f'Timeout for socket connection is seconds. Default (seconds): {ARGS_DEFAULT_SOCK_TIMEOUT} without proxy, {2*ARGS_DEFAULT_SOCK_TIMEOUT} with proxy')
    parser.add_option('-d', '--dry-run',
                      dest='dry_run', action="store_true",
                      help='Print formatted output without full script running.')
    parser.add_option('--log-size',
                      dest='log_size', type='int', default=5,
                      help='Set the Events Log history frame length.')


def print_usage():
    """Wrapper for Logo with help."""
    print(LOGO_NOCOLOR)
    create_parser().print_help()

    sys.exit()
