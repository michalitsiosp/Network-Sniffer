from collections import defaultdict
import sys
import time
from scapy.all import IP, TCP, UDP, conf, sniff

# ANSI Colors
RED = "\033[91m"
RESET = "\033[0m"


class NetworkDetector:

    def __init__(self, syn_threshold=20, port_threshold=15, time_window=10):
        self.SYN_THRESHOLD = syn_threshold
        self.PORT_THRESHOLD = port_threshold
        self.TIME_WINDOW = time_window

        self.syn_counter = defaultdict(int)
        self.port_tracker = defaultdict(set)

        self.alerted_port_scan = set()
        self.alerted_syn_flood = set()

        self.last_reset = time.time()

    def detect_anomalies(self, src_ip, port, flags=None):
        if time.time() - self.last_reset > self.TIME_WINDOW:
            self.syn_counter.clear()
            self.port_tracker.clear()
            self.alerted_port_scan.clear()
            self.alerted_syn_flood.clear()
            self.last_reset = time.time()

        if port:
            self.port_tracker[src_ip].add(port)
            if (
                len(self.port_tracker[src_ip]) > self.PORT_THRESHOLD
                and src_ip not in self.alerted_port_scan
            ):
                print(
                    f"\n{RED}[ALERT] 🚨 Possible Port Scan from {src_ip}! "
                    f"(Scanned >{self.PORT_THRESHOLD} ports){RESET}\n"
                )
                self.alerted_port_scan.add(src_ip)

        if flags == "S":
            self.syn_counter[src_ip] += 1
            if (
                self.syn_counter[src_ip] > self.SYN_THRESHOLD
                and src_ip not in self.alerted_syn_flood
            ):
                print(
                    f"\n{RED}[ALERT] 🚨 Possible SYN Flood / DoS from {src_ip}! "
                    f"(>{self.SYN_THRESHOLD} SYN packets){RESET}\n"
                )
                self.alerted_syn_flood.add(src_ip)

    def process_packet(self, packet):
        if packet.haslayer(IP):
            src_ip = packet[IP].src
            dst_ip = packet[IP].dst
            port = None
            flags = None

            if packet.haslayer(TCP):
                port = packet[TCP].dport
                flags = str(packet[TCP].flags)
                print(f"[TCP] {src_ip} -> {dst_ip}:{port} | Flags: {flags}")

            elif packet.haslayer(UDP):
                port = packet[UDP].dport
                print(f"[UDP] {src_ip} -> {dst_ip}:{port}")

            self.detect_anomalies(src_ip, port, flags)


def start_sniffer_menu():
    """Συνάρτηση που καλείται από το κεντρικό Scan.py"""
    print("\n--- Available Interfaces ---")
    print(conf.ifaces)
    iface = input("\nSelect interface to sniff on: ").strip()

    if not iface:
        print("[-] Invalid interface.")
        return

    detector = NetworkDetector(
        syn_threshold=20, port_threshold=15, time_window=10
    )
    print(
        f"\n[*] Starting Sniffer & Anomaly Detector on {iface}... (Press Ctrl+C to stop)\n"
    )

    try:
        sniff(iface=iface, prn=detector.process_packet, store=False)
    except KeyboardInterrupt:
        print("\n[*] Stopping Sniffer...")
