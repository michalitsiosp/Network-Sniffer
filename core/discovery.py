import time
import sys
import urllib.request
from scapy.all import conf, IP, ICMP, Ether, ARP, srp, sr, get_if_addr

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"

def get_vendor(mac):
    try:
        url = f"https://api.macvendors.com/{mac}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=2) as response:
            return response.read().decode("utf-8")
    except Exception:
        return "Unknown Vendor"

def netdiscover(save_callback):
    my_ip = get_if_addr(conf.iface)
    target1 = ".".join(my_ip.split(".")[:-1]) + ".0/24"
    try:
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request = ARP(pdst=target1)
        packet = broadcast / arp_request
        answered, _ = srp(packet, timeout=3, verbose=0)
    except Exception as e:
        print(f"[-] Error: {e}")
        sys.exit(1)

    header = "IP Address\t\tMAC Address\t\tDevice\n" + "-" * 65 + "\n"
    report_data = header
    for sent, received in answered:
        vendor = get_vendor(received.hwsrc)
        line = f"{received.psrc:<16}\t{received.hwsrc}\t{vendor}\n"
        print(line, end="")
        report_data += line
        time.sleep(1)

    save_callback(report_data)

def ping_target(save_callback):
    target = input("Select your target IP/Domain: ").strip()
    if not target:
        print(f"{RED}[-] Target cannot be empty.{RESET}")
        return

    count = 4
    print(f"{CYAN}[*] Sending {count} ICMP Echo Requests to {target}...\n{RESET}")
    report_data = f"Ping Results for {target}:\n"
    received_count = 0

    for i in range(1, count + 1):
        start_time = time.time()
        ans, _ = sr(IP(dst=target, ttl=64) / ICMP(), timeout=2, verbose=0)
        rtt = round((time.time() - start_time) * 1000, 2)

        if ans:
            for sent, received in ans:
                if received.haslayer(ICMP) and received[ICMP].type == 0:
                    line = f"Reply from {received.src}: bytes={len(received)} time={rtt}ms TTL={received.ttl}\n"
                    print(f"{GREEN}[+]{RESET} {line}", end="")
                    report_data += line
                    received_count += 1
                    break
        else:
            line = f"Request timed out for packet {i}.\n"
            print(f"{RED}[-]{RESET} {line}", end="")
            report_data += line

        time.sleep(0.5)

    summary = f"\n--- {target} ping statistics ---\n{count} packets transmitted, {received_count} received, {round(((count-received_count)/count)*100, 1)}% packet loss\n"
    print(f"\n{CYAN}{summary}{RESET}")
    report_data += summary
    save_callback(report_data)
