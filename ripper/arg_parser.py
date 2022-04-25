from collections import namedtuple
import sys
from optparse import OptionParser, IndentedHelpFormatter

from ripper.constants import *
from ripper.actions.attack import attack_method_labels


def parser_add_options(parser: OptionParser) -> None:
    """Add options to a parser."""
    parser.add_option('-s', '--targets',
                      dest='targets', action='append',
                      help='Attack target in {scheme}://{hostname}[:{port}][{path}] format. Multiple targets allowed.')
    parser.add_option('--targets-list',
                      dest='targets_list', type='str',
                      help='File (fs or http/https) with targets in {scheme}://{hostname}[:{port}][{path}] line format.')
    parser.add_option('-m', '--method',
                      dest='attack_method', type='str',
                      help=f'Attack method: {", ".join(attack_method_labels)}')
    parser.add_option('-e', '--http-method',
                      dest='http_method', type='str', default=ARGS_DEFAULT_HTTP_ATTACK_METHOD,
                      help=f'HTTP method. Default: {ARGS_DEFAULT_HTTP_ATTACK_METHOD}')
    parser.add_option('-t', '--threads',
                      dest='threads_count', type='str', default=ARGS_DEFAULT_THREADS_COUNT,
                      help=f'Total fixed threads count (number) or "auto" (text) for automatic threads selection. Default: {ARGS_DEFAULT_THREADS_COUNT}')
    parser.add_option('--min-random-packet-len',
                      dest='min_random_packet_len', type='int',
                      help=f'Min random packets length. Default: {DEFAULT_MIN_RND_PACKET_LEN}')
    parser.add_option('-l', '--max-random-packet-len',
                      dest='max_random_packet_len', type='int',
                      help=f'Max random packets length. Default: {DEFAULT_MAX_RND_PACKET_LEN} for udp/tcp')
    parser.add_option('-y', '--proxy-list',
                      dest='proxy_list',
                      help='File (fs or http/https) with proxies in ip:port:username:password line format. Proxies will be ignored in udp attack!')
    parser.add_option('-k', '--proxy-type',
                      dest='proxy_type', type='str', default=ARGS_DEFAULT_PROXY_TYPE,
                      help=f'Type of proxy to work with. Supported types: socks5, socks4, http. Default: {ARGS_DEFAULT_PROXY_TYPE}')
    parser.add_option('-c', '--health-check',
                      dest='health_check', type='int', default=ARGS_DEFAULT_HEALTH_CHECK,
                      help=f'Controls health check availability. Turn on: 1, turn off: 0. Default: {ARGS_DEFAULT_HEALTH_CHECK}')
    parser.add_option('-o', '--socket-timeout',
                      # default value is not set here to keep dynamic logic during initialization
                      dest='socket_timeout', type='int', default=ARGS_DEFAULT_SOCK_TIMEOUT,
                      help=f'Timeout for socket connection is seconds. Default (seconds): {ARGS_DEFAULT_SOCK_TIMEOUT} without proxy, {2*ARGS_DEFAULT_SOCK_TIMEOUT} with proxy')
    parser.add_option('--dry-run',
                      dest='dry_run', action='store_true',
                      help='Print formatted output without full script running.')
    parser.add_option('--log-size',
                      dest='log_size', type='int', default=DEFAULT_LOG_SIZE,
                      help='Set the Events Log history frame length.')
    parser.add_option('--log-level',
                      dest='event_level', type='str', default=DEFAULT_LOG_LEVEL,
                      help='Log level for events board. Supported levels: info, warn, error, none.')
    parser.add_option('-d', '--duration',
                      dest='duration', type='int',
                      help='Attack duration in seconds. After this duration script will stop it\'s execution.')
    parser.add_option('-q', '--quiet',
                      dest='verbose', action='store_false',
                      help='Do not print messages to stdout')


def create_parser() -> OptionParser:
    """Initialize parser with options."""
    formatter = IndentedHelpFormatter(
        indent_increment=2,
        max_help_position=56,
        width=120,
        short_first=1
    )
    parser = OptionParser(usage=USAGE, epilog=EPILOG, version=f'%prog {VERSION}', formatter=formatter)
    parser_add_options(parser)

    return parser


def Args(**args):
    values = locals()['args']
    arguments = {}
    parser = create_parser()
    for option in parser.option_list:
        if option.dest:
            if (isinstance(option.default, tuple) and option.default[0] == 'NO'):
                arguments[option.dest] = None
            else:
                arguments[option.dest] = option.default
    ArgsClass = namedtuple('Args', ' '.join(arguments.keys()))
    for key, value in values.items():
        arguments[key] = value
    return ArgsClass(**arguments)


def print_usage():
    """Wrapper for Logo with help."""
    print(LOGO_NOCOLOR)
    create_parser().print_help()

    sys.exit()
