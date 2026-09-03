import os
import sys
import json
from datetime import datetime

# Core Modules Imports
from core.cve_lookup import format_cve_output, search_cve
from core.discovery import netdiscover, ping_target
from core.traceroute import traceroute
from core.scanner import nmap_scan

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


def sudo():
    if os.name == "posix":
        if os.geteuid() != 0:
            print(f"{RED}[-] Error: Root privileges required. Run with sudo.{RESET}")
            sys.exit(1)


def save(data, vendor):
    choice = input(f"\n{YELLOW}Do you want to store the report? (y/n): {RESET}").strip().lower()
    if choice == "y":
        try:
            now = datetime.now()
            f_time = now.strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"report_{f_time}_{vendor}.txt"

            with open(filename, "w", encoding="utf-8") as file:
                if isinstance(data, (dict, list)):
                    json.dump(data, file, indent=4)
                else:
                    file.write(str(data))

            print(f"{GREEN}[+] Report saved successfully as '{filename}'!{RESET}")
        except Exception as e:
            print(f"{RED}[-] Error saving report: {e}{RESET}")


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
            netdiscover(lambda data: save(data, "netdiscover"))
        elif apanthsh == "2":
            traceroute(lambda data: save(data, "traceroute"))
        elif apanthsh == "3":
            nmap_scan(lambda data: save(data, "nmap"))
        elif apanthsh == "4":
            ping_target(lambda data: save(data, "ping"))
        elif apanthsh == "5":
            service = input("Enter Service Name: ").strip()
            version = input("Enter Version: ").strip()
            if service and version:
                cves = search_cve(service, version)
                report = format_cve_output(service, version, cves)
                print(report)
                save(report, "cve")
        elif apanthsh == "6":
            sys.exit(0)

        input(f"\n{YELLOW}Press Enter to return to main menu...{RESET}")
        clear_screen()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{CYAN}[*] Exiting...{RESET}")
        sys.exit(0)
