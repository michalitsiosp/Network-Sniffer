from datetime import datetime
import json
import os
import sys

from core.compare import interactive_compare
from core.cve_lookup import format_cve_output, search_cve
from core.database import open_in_sqlitebrowser, save_report_to_db
from core.discovery import netdiscover, ping_target
from core.scanner import nmap_scan

# ΝΕΟ IMPORT: Εισαγωγή του Sniffer / Detector
from core.sniff import start_sniffer_menu
from core.traceroute import traceroute

# ANSI Color Codes
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


def clear_screen():
    os.system("clear" if os.name == "posix" else "cls")

def print_banner():
    print(
        r"  _   _      _                      _     ____        _  __  __           "
    )
    print(
        r" | \ | | ___| |___      _____  _ __| | __/ ___| _ __ (_)/ _|/ _| ___ _ __  "
    )
    print(
        r" |  \| |/ _ \ __\ \ /\ / / _ \| '__| |/ /\___ \| '_ \| | |_| |_ / _ \ '__| "
    )
    print(
        r" | |\  |  __/ |_ \ V  V / (_) | |  |   <  ___) | | | | |  _|  _|  __/ |    "
    )
    print(
        r" |_| \_|\___|\__| \_/\_/ \___/|_|  |_|\_\|____/|_| |_|_|_| |_|  \___|_|    "
    /n)
    

def sudo():
    if os.name == "posix":
        if os.geteuid() != 0:
            print(
                f"{RED}[-] Error: Root privileges required. Run with sudo.{RESET}"
            )
            sys.exit(1)


def save(data, vendor):
    choice = (
        input(
            f"\n{YELLOW}Do you want to store the report in DB? (y/n): {RESET}"
        )
        .strip()
        .lower()
    )
    if choice == "y":
        save_report_to_db(scan_type=vendor, data=data)


def main():
    sudo()
    while True:
        print_banner()
        print(f"{CYAN}1. ɴᴇᴛᴅɪꜱᴄᴏᴠᴇʀ (Local ARP Scan){RESET}")
        print(f"{CYAN}2. ᴛʀᴀᴄᴇʀᴏᴜᴛᴇ (ICMP Path Trace){RESET}")
        print(f"{CYAN}3. ɴᴍᴀᴘ Scan{RESET}")
        print(f"{CYAN}4. ᴘɪɴɢ ᴛᴀʀɢᴇᴛ{RESET}")
        print(f"{CYAN}5. CVE Lookup{RESET}")
        print(f"{CYAN}6. Compare Reports{RESET}")
        print(
            f"{CYAN}7. Network Sniffer & IDS (Live Traffic / Anomalies){RESET}"
        )
        print(f"{CYAN}8. Open Database (sqlitebrowser){RESET}")
        print(f"{CYAN}9. ᴇxɪᴛ{RESET}\n")

        apanthsh = input("Select option (1-9): ").strip()

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
            interactive_compare()
        elif apanthsh == "7":
            # Κλήση του sniffer από το core/sniff.py
            start_sniffer_menu()
        elif apanthsh == "8":
            open_in_sqlitebrowser()
        elif apanthsh == "9":
            sys.exit(0)

        input(f"\n{YELLOW}Press Enter to return to main menu...{RESET}")
        clear_screen()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{CYAN}[*] Exiting...{RESET}")
        sys.exit(0)
