# Network Reconnaissance Tool (Scapy)

A Python-based cybersecurity and network discovery tool that combines **Traceroute** (ICMP) and **Netdiscover** (ARP Scanning) functionalities to analyze network targets and discover local active devices.

## Features
* **Traceroute:** Maps packet routing hops to a target domain or IP using ICMP packets.
* **Auto-Subnet Discovery:** Automatically detects the local gateway and subnet range (LAN) using Scapy's interface bindings.
* **Netdiscover (ARP Scan):** Identifies active host IP addresses and MAC addresses on the local network.

## Prerequisites
* Linux OS
* Python 3.x
* Scapy library

## Installation

1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
   cd YOUR_REPOSITORY_NAME
