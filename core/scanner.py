import subprocess

RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def nmap_scan(save_callback):
    target = input("Enter target IP or Network (e.g., 192.168.1.1): ").strip()
    if not target:
        print(f"{RED}[-] Target cannot be empty.{RESET}")
        return

    print("\nSelect Scan Type:")
    print("1. Quick Scan (Fast Top Ports -Pn)")
    print("2. Service & Script Scan (Standard -sV -sC -Pn)")
    print("3. Aggressive OS & Port Scan (-A -T4 -Pn)")
    print("4. Full Stealth Scan all ports (-sS -p- -Pn -T2)")
    ap = input("\nEnter choice (1-4): ").strip()

    if ap == "1":
        args = ["nmap", "-F", "-Pn", target]
    elif ap == "2":
        args = ["nmap", "-sV", "-sC", "-Pn", target]
    elif ap == "3":
        args = ["nmap", "-A", "-T4", "-Pn", target]
    else:
        args = ["nmap", "-sS", "-p-", "-Pn", "--max-rate", "100", "-T2", target]

    print(f"\n{CYAN}[*] Running command: {' '.join(args)}{RESET}\n")

    try:
        result = subprocess.run(args, capture_output=True, text=True, check=True)
        print(result.stdout)
        save_callback(result.stdout)
    except FileNotFoundError:
        print(f"{RED}[-] Error: Nmap is not installed or not in PATH.{RESET}")
    except subprocess.CalledProcessError as e:
        print(f"{RED}[-] Error executing Nmap: {e}{RESET}")
        if e.stdout:
            print(e.stdout)
            save_callback(e.stdout)
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[-] Scan cancelled by user.{RESET}")
