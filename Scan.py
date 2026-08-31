import os
import sys
import json
import time
import logging
import subprocess
import urllib.request
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from cve_lookup import format_cve_output, search_cve
# Scapy Imports
import scapy.config
from scapy.all import conf, IP, ICMP, Ether, ARP, sr, srp, get_if_addr

# Silence Scapy Warnings
logging.getLogger("scapy").setLevel(logging.CRITICAL)
conf.verb = 0

# ANSI Color Codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


def clear_screen():
    os.system("clear" if os.name == "posix" else "cls")


def print_banner():
	print(r"  _   _       _                _             _____        _  __  __          ")
	print(r" | \ | |     | |              | |           / ____|      (_)/ _|/ _|         ")
	print(r" |  \| | ___ | |___      _____| |_ | |     | (___  _ __  _| |_| |_ ___ _ __  ")
	print(r" | . ` |/ _ \ __\ \ /\ / / _ \| '__| |/ /   \___ \| '_ \| |  _|  _/ _ \ '__| ")
	print(r" | |\  |  __/ |_ \ V  V / (_) | |  |   <    ____) | | | | | | | ||  __/ |    ")
	print(r" |_| \_|\___|\__| \_/\_/ \___/|_|  |_|\_\  |_____/|_| |_|_|_| |_| \___|_|    ")
	print(r"                                                                             ")



# Sudo Privileges Check
def sudo():
    if os.name == "posix":
        if os.geteuid() != 0:
            print(f"{RED}[-] Error: Root privileges required. Run with sudo.{RESET}")
            sys.exit(1)
    else:
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print(f"{RED}[-] Error: Administrator privileges required.{RESET}")
                sys.exit(1)
        except Exception:
            pass


# Save Report
def save(data):
    choice = input(f"\n{YELLOW}Do you want to store the report? (y/n): {RESET}").strip().lower()
    if choice == "y":
        try:
            now = datetime.now()
            f_time = now.strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"report_{f_time}.json"

            with open(filename, "w", encoding="utf-8") as file:
                if isinstance(data, (dict, list)):
                    json.dump(data, file, indent=4)
                else:
                    file.write(str(data))

            print(f"{GREEN}[+] Report saved successfully as '{filename}'!{RESET}")
        except Exception as e:
            print(f"{RED}[-] Error saving report: {e}{RESET}")


# find vendor
def get_vendor(mac):
    try:
        url = f"https://api.macvendors.com/{mac}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=2) as response:
            return response.read().decode("utf-8")
    except Exception:
        return "Unknown Vendor"


# netdiscover.py
def netdiscover():
    my_ip = get_if_addr(conf.iface)  # returns eg "192.168.55.12"
    target1 = ".".join(my_ip.split(".")[:-1]) + ".0/24"
    try:
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request = ARP(pdst=target1)
        packet = broadcast / arp_request
        answered, unanswered = srp(packet, timeout=3, verbose=0)
    except Exception as e:
        print(f"[-] Error: {e} ")
        sys.exit(1)

    header = "IP Address\t\tMAC Address\t\tDevice\n" + "-" * 65 + "\n"
    report_data = header
    for sent, received in answered:
        vendor = get_vendor(received.hwsrc)
        line = f"{received.psrc:<16}\t{received.hwsrc}\t{vendor}\n"
        print(line, end="")  # print to screen
        report_data += line  # add to report
        time.sleep(1)

    save(report_data)

# Traceroute
def traceroute():
    target = input("Write target IP or domain: ").strip()
    if not target:
        print(f"{RED}[-] Target cannot be empty.{RESET}")
        return

    print(f"{CYAN}[*] Tracing route to {target} (max 30 hops)...\n{RESET}")

    header = f"{'TTL':<5}\t{'Router IP':<16}\t{'Response/Summary'}\n" + "-" * 55 + "\n"
    print(header, end="")
    report_data = header

    ping_reached = False
    ttl = 1

    try:
        while not ping_reached and ttl <= 30:
            start_time = time.time()
            ans, _ = sr(IP(dst=target, ttl=ttl) / ICMP(), timeout=2, verbose=0)
            rtt = round((time.time() - start_time) * 1000, 2)

            if ans:
                for sent, received in ans:
                    line = f"{ttl:<5}\t{received.src:<16}\t{received.summary()} ({rtt} ms)\n"
                    print(line, end="")
                    report_data += line

                    if received.haslayer(ICMP) and received[ICMP].type == 0:
                        ping_reached = True
                        break
            else:
                line = f"{ttl:<5}\t*\t\t\tRequest timed out.\n"
                print(f"{ttl:<5}\t*\t\t\t{RED}Request timed out.{RESET}")
                report_data += line

            ttl += 1

        if not ping_reached:
            msg = "\n[-] Target was not reached within the TTL limit.\n"
            print(msg)
            report_data += msg

    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Traceroute stopped by user.{RESET}")
    
    save(report_data)


# Nmap Scan
def nmap_scan():
    target = input("Enter target IP or Network (e.g., 192.168.1.1): ").strip()
    if not target:
        print(f"{RED}[-] Target cannot be empty.{RESET}")
        return

    print("\nSelect Scan Type:")
    print("1. Quick Scan (Fast Top Ports)")
    print("2. Service & Script Scan (Standard -sV -sC)")
    print("3. Aggressive OS & Port Scan (-A -T4)")
    print("4. Full Stealth Scan all ports (-sS -p- -Pn -T2)")
    ap = input("\nEnter choice (1-4): ").strip()

    if ap == "1":
        args = ["nmap", "-F", target]
    elif ap == "2":
        args = ["nmap", "-sV", "-sC", target]
    elif ap == "3":
        args = ["nmap", "-A", "-T4", target]
    else:
        args = ["nmap", "-sS", "-p-", "-Pn", "--max-rate", "100", "-T2", target]

    print(f"\n{CYAN}[*] Running command: {' '.join(args)}{RESET}\n")

    try:
        result = subprocess.run(args, capture_output=True, text=True, check=True)
        print(result.stdout)
        save(result.stdout)
    except FileNotFoundError:
        print(f"{RED}[-] Error: Nmap is not installed or not in PATH.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}[-] Error executing Nmap: {e}{RESET}")
        if e.stdout:
            print(e.stdout)
            save(e.stdout)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[-] Scan cancelled by user.{RESET}")


# Ping Target (Πλήρως Αναβαθμισμένο)
def ping_target():
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
    
    save(report_data)


# Main Menu
def main():
    sudo()
    while True:
        print_banner()
        print(f"{CYAN}1. ɴᴇᴛᴅɪꜱᴄᴏᴠᴇʀ (Local ARP Scan){RESET}")
        print(f"{CYAN}2. ᴛʀᴀᴄᴇʀᴏᴜᴛᴇ (ICMP Path Trace){RESET}")
        print(f"{CYAN}3. ɴᴍᴀᴘ Scan{RESET}")
        print(f"{CYAN}4. ᴘɪɴɢ ᴛᴀʀɢᴇᴛ{RESET}")
        print(f"{CYAN}5. CVE Lookup{RESET}")
        print(f"{CYAN}6. ᴇxɪᴛ{RESET}\n")

        apanthsh = input("Select option (1-6): ").strip()

        if apanthsh == "1":
            netdiscover()
        elif apanthsh == "2":
            traceroute()
        elif apanthsh == "3":
            nmap_scan()
        elif apanthsh == "4":
            ping_target()
        elif apanthsh == "5":
            service = input(
                "Enter Service Name (e.g. Apache, OpenSSH): "
            ).strip()
            version = input("Enter Version (e.g. 2.4.49, 8.2p1): ").strip()

            if service and version:
                print(
                    f"\n[*] Searching NVD Database for {service} {version}..."
                )
                cves = search_cve(service, version)
                report = format_cve_output(service, version, cves)
                print(report)
                save(report)  # Αποθήκευση στο report file σου
            else:
                print("[-] Service and version are required.")

        elif apanthsh == "6":
            print(f"{CYAN}[*] Exiting Network Toolkit... Goodbye!{RESET}")
            sys.exit(0)
        else:
            print(
                f"{RED}[!] Invalid option. Please enter a number from 1 to 6.{RESET}\n"
            )

        input(f"\n{YELLOW}Press Enter to return to main menu...{RESET}")
        clear_screen()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{CYAN}[*] Exiting...{RESET}")
        sys.exit(0)
