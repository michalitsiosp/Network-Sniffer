import time
from scapy.all import IP, ICMP, sr

RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def traceroute(save_callback):
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

    save_callback(report_data)
