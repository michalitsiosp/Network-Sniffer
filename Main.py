import json
from datetime import datetime
import os
import subprocess #for Nmap
import urllib.request #for api
import sys #for pre run input
import time
from scapy.all import srp, Ether, ARP, conf, IP, sr, ICMP , get_if_addr
import logging
logging.getLogger("scapy").setLevel(logging.CRITICAL)
conf.verb = 0
print(r"  _   _       _                _             _____        _  __  __          ")
print(r" | \ | |     | |              | |           / ____|      (_)/ _|/ _|         ")
print(r" |  \| | ___ | |___      _____| |_ | |     | (___  _ __  _| |_| |_ ___ _ __  ")
print(r" | . ` |/ _ \ __\ \ /\ / / _ \| '__| |/ /   \___ \| '_ \| |  _|  _/ _ \ '__| ")
print(r" | |\  |  __/ |_ \ V  V / (_) | |  |   <    ____) | | | | | | | ||  __/ |    ")
print(r" |_| \_|\___|\__| \_/\_/ \___/|_|  |_|\_\  |_____/|_| |_|_|_| |_| \___|_|    ")
print(r"                                                                             ")

# ANSI codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


#save_report
def save(data):
    choice = input(f"{YELLOW}Do you want to store the report?{RESET}{GREEN} y/n: {RESET}").strip().lower()

    if choice == "y":
        try:
            now = datetime.now()
            f = now.strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"report_{f}.json"

            with open(filename, "w", encoding="utf-8") as file:
                if isinstance(data, (dict, list)):
                    json.dump(data, file, indent=4)
                else:
                    file.write(str(data))

            print(f"{GREEN}the report {f} is saved!{RESET}")
        except Exception as e:
            print(f"{RED}Error saving report: {e}{RESET}")#sudo privileges
#sudo privileges
def sudo():
        if os.name == 'posix':
                #code for Linux/Mac
                if os.geteuid() != 0:
                        print(f"{RED}[-] Error: Root privileges required{RESET}")
                        sys.exit(1)
        else:
                #code for Windows
                try:
                        import ctypes
                        if not ctypes.windll.shell32.IsUserAnAdmin():
                                print(f"{RED}[-] Error: Administrator  privileges required{RESET}")
                                sys.exit(1)
                except:
                        pass





#traceroute.py
def traceroute():
    target = input("write target ip: ").strip()
    if not target:
        print("[-] Target cannot be empty.")
        return

    print(f"{CYAN}[*] Tracing route to {target}\n{RESET}")

    # 1. Εκτύπωση και αποθήκευση του header
    header = "TTL\tRouter/IP\t\tResponse\n" + "-" * 55 + "\n"
    print(header, end="")
    report_data = header

    ping = False
    ttl = 1

    try:
        while not ping and ttl <= 30:
            # Στέλνουμε το ICMP πακέτο με το τρέχον TTL
            ans, unans = sr(
                IP(dst=target, ttl=ttl) / ICMP(), timeout=1, verbose=0
            )

            if ans:
                # Απάντησε κάποιος router ή ο τελικός στόχος
                for sent, received in ans:
                    line = f"{ttl}\t{received.src:<15}\t{received.summary()}\n"
                    print(line, end="")
                    report_data += line

                    if received.type == 0:  # ICMP Echo Reply (στόχος)
                        ping = True
                        break
            else:
                line = f"{ttl}\t*\t\t\tRequest timed out.\n"
                print(f"{ttl}\t*\t\t\t{RED}Request timed out.{RESET}")
                report_data += line

            ttl += 1
            time.sleep(0.2)

        if not ping:
            msg = "\n[-] Target was not reached within the TTL limit.\n"
            print(msg)
            report_data += msg

    except KeyboardInterrupt:
        print(
            f"\n{YELLOW}[!] Traceroute stopped by user. Saving gathered data...{RESET}"
        )
    save(report_data)

#find vendor
def get_vendor(mac):
    try:
        url = f"https://api.macvendors.com/{mac}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=2) as response:
            return response.read().decode("utf-8")
    except Exception:
        return "Unknown Vendor"


#netdiscover.py
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
        report_data  = header
        for sent, received in answered:
                vendor = get_vendor(received.hwsrc)
                line = f"{received.psrc:<16}\t{received.hwsrc}\t{vendor}\n"
                print(line, end="")  # print to screen
                report_data += line  # add to report
                time.sleep(1)
        save(report_data)

def nmap_scan():
    target = input("Enter target IP or Network (e.g., 192.168.1.1): ").strip()
    if not target:
        # 1. Διόρθωση στο κλείσιμο των quotes
        print(f"{RED}[-] Target cannot be empty.{RESET}")
        return

    print("\nSelect Scan Type:")
    print("1. Quick Scan (Fast Top Ports)")
    print("2. Service & Script Scan (Standard -sV -sC)")
    print("3. Aggressive OS & Port Scan (Comprehensive -A -T4)")
    print("4. Full stealth Scan all ports -sS -p- -Pn --max-rate 100 -T2")
    ap = input("\nEnter choice (1-4): ").strip()

    # Δεν χρειάζεται το "sudo" στη λίστα εφόσον το Python script τρέχει ως root
    if ap == "1":
        print(f"\n[*] Starting Quick Scan on {target}...\n")
        args = ["nmap", "-F", target]
    elif ap == "2":
        print(f"\n[*] Starting Service & Script Scan on {target}...\n")
        args = ["nmap", "-sV", "-sC", target]
    elif ap == "3":
        print(f"\n[*] Starting Aggressive Scan on {target}...\n")
        args = ["nmap", "-A", "-T4", target]
    else:
        print(f"\n[*] Starting Full Stealth Scan on {target}\n")
        args = [
            "nmap","-sS","-p-","-Pn","--max-rate","100","-T2",target,]

    try:
        result = subprocess.run(
            args, capture_output=True, text=True, check=True
        )

        # Εμφάνιση στην οθόνη και αποθήκευση
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

# main menu
def main():
    sudo()
    while True:
        print("\n    𝗠 𝗘 𝗡 𝗨    ")
        print(f"{CYAN}1. ɴᴇᴛᴅɪꜱᴄᴏᴠᴇʀ{RESET}")
        print(f"{CYAN}2. ᴛʀᴀᴄᴇʀᴏᴜᴛᴇ{RESET}")
        print(f"{CYAN}3. ɴᴍᴀᴘ Scan{RESET}")
        print(f"{CYAN}4. ᴇxɪᴛ{RESET}")

        apanthsh = input("Select from (1-4): ").strip()

        if apanthsh == "1":
            netdiscover()
            for i in range(1, 4):
                print("-" * 80)
                print("-" * 80)

        elif apanthsh == "2":
            traceroute()
            for i in range(1, 4):
                print("-" * 80)
                print("-" * 80)

        elif apanthsh == "3":
            nmap_scan()

        elif apanthsh == "4":
            print("--Exit--")
            break

        else:
            print(
                f"{RED}[!] Invalid option. Please enter a number from 1 to 4.{RESET}\n"
            )
if __name__=="__main__":
	try:
		 main()
	except KeyboardInterrupt:
		sys.exit(0)
