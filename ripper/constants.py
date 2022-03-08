###############################################
# Constants
###############################################

VERSION = 'v1.3.9'
USAGE = 'Usage: python %prog [options] arg'
EPILOG = 'Example: python DRipper.py -s 192.168.0.1 -p 80 -t 100'
GETTING_SERVER_IP_ERROR_MSG = 'Can\'t get server IP. Packet sending failed. Check your VPN.'
SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC = 120
NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG = 'There are no successful connections more than 2 min. ' \
                                      'Check your VPN or change host/port.'
DEFAULT_CURRENT_IP_VALUE = '...detecting'
