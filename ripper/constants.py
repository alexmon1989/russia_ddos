###############################################
# Constants
###############################################

VERSION = 'v2.0.0'
USAGE = 'Usage: python %prog [options] arg'
EPILOG = 'Example: python DRipper.py -s 192.168.0.1 -p 80 -t 100'
GETTING_SERVER_IP_ERROR_MSG = 'Can\'t get server IP. Packet sending failed. Check your VPN.'
SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC = 120
NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC = 180
NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG = 'There are no successful connections more than 2 min. ' \
                                      'Check your VPN or change host/port.'
DEFAULT_CURRENT_IP_VALUE = '...detecting'
HOST_IN_PROGRESS_STATUS = 'HOST_IN_PROGRESS'
HOST_FAILED_STATUS = 'HOST_FAILED'
HOST_SUCCESS_STATUS = 'HOST_SUCCESS'

DT_FORMAT = '%Y-%m-%d %H:%M:%S'

MIN_SCREEN_WIDTH = 80

MIN_UPDATE_HOST_STATUSES_TIMEOUT = 120

LOGO_COLOR = f'''[cyan]
██████╗ ██████╗ ██╗██████╗ ██████╗ ███████╗██████╗
██╔══██╗██╔══██╗██║██╔══██╗██╔══██╗██╔════╝██╔══██╗
██║  ██║██████╔╝██║██████╔╝██████╔╝█████╗  ██████╔╝[yellow]
██║  ██║██╔══██╗██║██╔═══╝ ██╔═══╝ ██╔══╝  ██╔══██╗
██████╔╝██║  ██║██║██║     ██║     ███████╗██║  ██║
╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝
                                           [green]{VERSION}
[default]
It is the end user's responsibility to obey all applicable laws.
It is just like a server testing script and Your IP is visible.

Please, make sure you are ANONYMOUS!
'''

LOGO_NOCOLOR = f'''
██████╗ ██████╗ ██╗██████╗ ██████╗ ███████╗██████╗
██╔══██╗██╔══██╗██║██╔══██╗██╔══██╗██╔════╝██╔══██╗
██║  ██║██████╔╝██║██████╔╝██████╔╝█████╗  ██████╔╝
██║  ██║██╔══██╗██║██╔═══╝ ██╔═══╝ ██╔══╝  ██╔══██╗
██████╔╝██║  ██║██║██║     ██║     ███████╗██║  ██║
╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝
                                           {VERSION}

It is the end user's responsibility to obey all applicable laws.
It is just like a server testing script and Your IP is visible.

Please, make sure you are ANONYMOUS!
'''
