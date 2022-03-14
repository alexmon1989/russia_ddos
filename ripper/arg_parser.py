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
                      dest='max_random_packet_len', type='int', default=48,
                      help='Max random packets length (default: 48)')
    parser.add_option('-m', '--method',
                      dest='attack_method', type='str', default='udp',
                      help='Attack method: udp (default), tcp, http')
    parser.add_option('-s', '--server',
                      dest='host',
                      help='Attack to server IP')


def print_usage():
    """Wrapper for Logo with help."""
    print(LOGO_NOCOLOR)
    create_parser().print_help()

    sys.exit()

