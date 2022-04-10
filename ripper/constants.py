from _version import __version__

###############################################
# Constants | Logo and help messages
###############################################
VERSION = f'v{__version__}'
USAGE = 'Usage: %prog [options] arg'
EPILOG = 'Example: dripper -t 100 -m tcp-flood -s tcp://192.168.0.1:80'
GITHUB_OWNER = 'alexmon1989'
GITHUB_REPO = 'russia_ddos'
GITHUB_ID = f'{GITHUB_OWNER}/{GITHUB_REPO}'
GITHUB_URL = f'https://github.com/{GITHUB_ID}'

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

[u blue link={GITHUB_URL}]{GITHUB_URL}[/]
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

{GITHUB_URL}
'''

BANNER = '\n\n[r][deep_sky_blue1]#StandWith[bright_yellow]Ukraine[/]'
CONTROL_CAPTION = f'[grey53]Press [green]CTRL+C[grey53] to interrupt process.{BANNER}\n'

DEFAULT_CURRENT_IP_VALUE = '...detecting'
HOST_IN_PROGRESS_STATUS = 'HOST_IN_PROGRESS'
HOST_FAILED_STATUS = 'HOST_FAILED'
HOST_SUCCESS_STATUS = 'HOST_SUCCESS'

# ==== Badge templates ====
BADGE_INFO = '[bold gray0 on cyan] {message} [/]'
BADGE_WARN = '[bold gray0 on orange1] {message} [/]'
BADGE_ERROR = '[bold white on red1] {message} [/]'


# ==== Formats and Constants
DATE_TIME_FULL = '%Y-%m-%d %H:%M:%S'
DATE_TIME_SHORT = '%H:%M:%S'


# ==== Defaults for Input ARGS ===
ARGS_DEFAULT_PORT = 80
ARGS_DEFAULT_THREADS_COUNT = 'auth'
ARGS_DEFAULT_RND_PACKET_LEN = 1
ARGS_DEFAULT_MAX_RND_PACKET_LEN = 1024
ARGS_DEFAULT_HEALTH_CHECK = 1
ARGS_DEFAULT_HTTP_ATTACK_METHOD = 'GET'
ARGS_DEFAULT_HTTP_REQUEST_PATH = '/'
ARGS_DEFAULT_SOCK_TIMEOUT = 1
ARGS_DEFAULT_PROXY_TYPE = 'socks5'


# ==== Defaults ====
GEOIP_NOT_DEFINED = '--'
CONNECT_TO_HOST_MAX_RETRY = 5
MIN_SCREEN_WIDTH = 100
MIN_UPDATE_HOST_STATUSES_TIMEOUT = 120
SUCCESSFUL_CONNECTIONS_CHECK_PERIOD_SEC = 120
NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC = 180
HTTP_STATUS_CODE_CHECK_PERIOD_SEC = 10
UPDATE_CURRENT_IP_CHECK_PERIOD_SEC = 60
TARGET_STATS_AUTO_PAGINATION_INTERVAL_SECONDS = 5
MIN_ALIVE_AVAILABILITY_PERCENTAGE = 50
DEFAULT_LOG_LEVEL = 'warn'
DEFAULT_LOG_SIZE = 5
MAX_AUTOSCALE_CPU_PERCENTAGE = 80
MAX_FAILED_FAILED_AUTOSCALE_TESTS = 10
DEFAULT_AUTOSCALE_TEST_SECONDS = 0.5

# ==== Sockets ====
PROXY_MAX_FAILURE_RATIO = 0.8
PROXY_MIN_VALIDATION_REQUESTS = 8


CLOUDFLARE_TAGS = [
    'cloudflare',
    'cf-spinner-please-wait',
    'we are checking your browser...',
    'Cloudflare Ray ID'
]

# ==== Error messages ====
GETTING_SERVER_IP_ERR_MSG = 'Can\'t get server IP. Packet sending failed. Check your VPN.'
NO_SUCCESSFUL_CONNECTIONS_ERR_MSG = 'There are no successful connections more than 2 min. ' \
    'Check your VPN or change host/port.' \
    'If you are using the proxylist then proxy validation might be in progress.'
YOUR_IP_WAS_CHANGED_ERR_MSG = 'Your IP was changed!!! Check VPN connection.'
CANNOT_SEND_REQUEST_ERR_MSG = 'Cannot send Request or Packet. Host does not respond.'
NO_MORE_PROXIES_ERR_MSG = 'There are no more operational proxies to work with host.'
MSG_YOUR_IP_WAS_CHANGED = 'IP changed'
MSG_CHECK_VPN_CONNECTION = 'Check VPN'
MSG_DONT_USE_VPN_WITH_PROXY = 'Do not use VPN with proxy'
NO_CONNECTIONS_ERR_MSG = f"There were no successful connections for more " \
    f"than {NO_SUCCESSFUL_CONNECTIONS_DIE_PERIOD_SEC // 60} minutes. " \
    f"Your attack is ineffective."
TARGET_DEAD_ERR_MSG = "[orange1]Target should be dead!"
NO_MORE_TARGETS_LEFT_ERR_MSG = 'No more valid targets left'
