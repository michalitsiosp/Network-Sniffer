# Network Topology Reconnaissance Suite

A Python-based network analysis tool leveraging **Scapy** to combine **ICMP Traceroute** with automated **ARP Subnet Discovery** and **MAC Vendor Identification**.

Designed for security audits, system administrators, and network reconnaissance.

---

## Key Features

* **Path Discovery (Traceroute):** Maps router hops to a remote host/domain using raw ICMP packets.
* **Auto Subnet Detection:** Automatically queries the active network interface to target the current IPv4 local subnet (e.g., `192.168.1.0/24`).
* **Active Host Discovery (Netdiscover):** Uses Layer 2 ARP broadcast queries to reveal live devices on the local area network (LAN).
* **MAC Vendor Identification:** Resolves physical MAC addresses to hardware manufacturers (e.g., Apple, Xiaomi, TP-Link) via REST API queries.

---

## Requirements

* **OS:** Linux / Unix-based system
* **Python:** 3.8+
* **Permissions:** Root / `sudo` privileges (required for Scapy raw socket creation)

---

## Installation & Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/michalitsiosp/Network-Topology-Reconnaissance-Suite.git
   cd Network-Topology-Reconnaissance-Suite
   ```

2. **Setup:**

   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Usage**

   Run the suite by supplying a target hostname or IP address for the traceroute component:

   ```bash
   sudo python3 Main.py
   ```

4. **Example**

   ```
    _   _                    _       _____       _  __  __
   | \ | |                  | |     / ____|     (_)/ _|/ _|
   |  \| | ___| |___      _____  _ __| | __ | (___  _ __  _| |_| |_ ___ _ __
   | . ` |/ _ \ __\ \ /\ / / _ \| '__| |/ /  \___ \| '_ \| |  _|  _/ _ \ '__|
   | |\  |  __/ |_ \ V  V / (_) | |  |   <    ____) | | | | | | | ||  __/ |
   |_| \_|\___|\__| \_/\_/ \___/|_|  |_|\_\ |_____/|_| |_|_|_| |_| \___|_|

   [*] Tracing route to example.com
   TTL    Router/IP        Response
   -------------------------------------------------------
   1      192.168.1.1      IP / ICMP 192.168.1.1 > ...
   2      198.51.100.1     IP / ICMP 198.51.100.1 > ...
   ...
   12     203.0.113.50     IP / ICMP 203.0.113.50 > ...

   IP Address               MAC Address             Device
   -----------------------------------------------------------------
   192.168.1.1              ##:##:##:##:##:##       TP-Link Corporation Limited
   192.168.1.15             ##:##:##:##:##:##       Intel Corporate
   ```
