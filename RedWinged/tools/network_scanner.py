# Improved network_scanner.py: Added random user agents, more comments, error handling

import requests
import socket
import os
import random
from tools.shared import USER_AGENTS  # Import from shared (fixes circular)

def website_info_scanner(url):
    """Scan website for public info with random user agent."""
    try:
        if not url.startswith('http'):
            url = 'https://' + url
        headers = {'User-Agent': random.choice(USER_AGENTS)}
        response = requests.get(url, headers=headers, timeout=10)
        print("Status Code:", response.status_code)
        print("Headers:", response.headers)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching website info: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def ip_scanner(ip):
    """Retrieve public hostname info for IP."""
    try:
        host = socket.gethostbyaddr(ip)
        print("Hostname:", host[0])
        print("Aliases:", host[1])
        print("IPs:", host[2])
    except socket.herror as e:
        print(f"Hostname error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def ip_port_scanner(ip):
    """Scan common ports ethically (owned systems only)."""
    common_ports = [80, 443, 22, 21, 25]
    print("Scanning common ports (ethical use only on owned systems)...")
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, port))
            if result == 0:
                print(f"Port {port} is open")
            else:
                print(f"Port {port} is closed")
            sock.close()
        except Exception as e:
            print(f"Error scanning port {port}: {e}")

def ip_pinger(ip):
    """Ping IP to check reachability (macOS command)."""
    try:
        response = os.system(f"ping -c 4 {ip}")
        if response == 0:
            print("IP is reachable")
        else:
            print("IP is not reachable")
    except Exception as e:
        print(f"Error pinging IP: {e}")