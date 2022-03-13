###############################################
# Constants | Logo and help messages
###############################################

VERSION = 'v2.0.3'
USAGE = 'Usage: python %prog [options] arg'
EPILOG = 'Example: python DRipper.py -s 192.168.0.1 -p 80 -t 100'

LOGO_COLOR = f'''[deep_sky_blue1]
██████╗ ██████═╗██╗██████╗ ██████╗ ███████╗██████═╗
██╔══██╗██╔══██║██║██╔══██╗██╔══██╗██╔════╝██╔══██║
██║  ██║██████╔╝██║██████╔╝██████╔╝█████╗  ██████╔╝[bright_yellow]
██║  ██║██╔══██╗██║██╔═══╝ ██╔═══╝ ██╔══╝  ██╔══██╗
██████╔╝██║  ██║██║██║     ██║     ███████╗██║  ██║
╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝
                                           [green]{VERSION}
[grey53]
It is the end user's responsibility to obey all applicable laws.
It is just like a server testing script and Your IP is visible.

Please, make sure you are ANONYMOUS!
'''

LOGO_NOCOLOR = f'''
██████╗ ██████═╗██╗██████╗ ██████╗ ███████╗██████═╗
██╔══██╗██╔══██║██║██╔══██╗██╔══██╗██╔════╝██╔══██║
██║  ██║██████╔╝██║██████╔╝██████╔╝█████╗  ██████╔╝
██║  ██║██╔══██╗██║██╔═══╝ ██╔═══╝ ██╔══╝  ██╔══██╗
██████╔╝██║  ██║██║██║     ██║     ███████╗██║  ██║
╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝     ╚═╝     ╚══════╝╚═╝  ╚═╝
                                           {VERSION}

It is the end user's responsibility to obey all applicable laws.
It is just like a server testing script and Your IP is visible.

Please, make sure you are ANONYMOUS!
'''

BANNER = '\n\n[r][deep_sky_blue1]#StandWith[bright_yellow]Ukraine\n'


# ==== Error messages ====
GETTING_SERVER_IP_ERROR_MSG = 'Can\'t get server IP. Packet sending failed. Check your VPN.'
NO_SUCCESSFUL_CONNECTIONS_ERROR_MSG = 'There are no successful connections more than 2 min. ' \
                                      'Check your VPN or change host/port.'
YOUR_IP_WAS_CHANGED = 'Your IP was changed!!! Check VPN connection.'
CANNOT_SEND_REQUEST_ERR_MSG = 'Cannot send Request or Packet. Host does not response.'
DEFAULT_CURRENT_IP_VALUE = '...detecting'
HOST_IN_PROGRESS_STATUS = 'HOST_IN_PROGRESS'
HOST_FAILED_STATUS = 'HOST_FAILED'
HOST_SUCCESS_STATUS = 'HOST_SUCCESS'


# ==== Formats and Constants
DATE_TIME_FULL = '%Y-%m-%d %H:%M:%S'
DATE_TIME_SHORT = '%H:%M:%S'


# ==== Defaults ====
GEOIP_NOT_DEFINED = 'NOT DEFINED'
CONNECT_TO_HOST_MAX_RETRY = 5
MIN_SCREEN_WIDTH = 80
MIN_UPDATE_HOST_STATUSES_TIMEOUT = 120
SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC = 120
NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC = 180
