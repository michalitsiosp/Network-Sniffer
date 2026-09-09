# Network Sniffer

**Network Topology Reconnaissance Suite** — a Python-based network analysis tool built on Scapy, combining ICMP traceroute with automated ARP subnet discovery, MAC vendor identification, and target pinging.

Built for security audits, system administrators, and network reconnaissance.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux%2FUnix-lightgrey)

---

## Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation--setup)
- [Usage](#usage)
- [Example Output](#example-output)
- [Project Structure](#project-structure)
- [Uninstalling](#uninstalling)
- [Legal Notice](#legal-notice)
- [License](#license)

---

## Features

| Feature | Description |
|---|---|
| **Path Discovery (Traceroute)** | Maps router hops to a remote host/domain using raw ICMP packets. |
| **Auto Subnet Detection** | Automatically queries the active network interface to target the current local IPv4 subnet (e.g. `192.168.1.0/24`). |
| **Active Host Discovery (Netdiscover)** | Uses Layer 2 ARP broadcast queries to reveal live devices on the local network (LAN). |
| **MAC Vendor Identification** | Resolves physical MAC addresses to hardware manufacturers (e.g. Apple, Xiaomi, TP-Link) via REST API queries. |
| **Ping Target** | Sends ICMP pings to a specified target through Scapy. |
| **Compare Files** | Compares two output files to spot hidden or new vendors and IPs. |
| **Traffic Analyzer** | Shows real-time network traffic on the interface you choose. |

---

## Requirements

- **OS:** Linux / Unix-based system
- **Python:** 3.8+ (3.10+ recommended)
- **Permissions:** Root / sudo (required for Scapy raw socket creation, netdiscover, and nmap operations)

### Python Dependencies (`requirements.txt`)

```
SQLAlchemy>=2.0.0
scapy>=2.5.0
```

---

## Installation & Setup

The easiest way to install the tool is with the included setup script:

```bash
# Clone the repository
git clone https://github.com/michalitsiosp/Network-Topology-Reconnaissance-Suite.git
cd Network-Topology-Reconnaissance-Suite

# Make the setup script executable and run it with sudo
chmod +x setup.sh
sudo ./setup.sh
```

`setup.sh` will:
1. Install the required system packages.
2. Create an isolated Python virtual environment at `/opt/networksniffer/venv`.
3. Install the necessary libraries (`SQLAlchemy`, `scapy`).
4. Make the tool available system-wide as the `NetworkSniffer` command.

---

## Usage

Once installed, run the suite from anywhere on your system with:

```bash
sudo NetworkSniffer
```

Root/sudo is required because the tool opens raw sockets to send and receive ICMP/ARP packets.

From the interactive menu you can:
- Run a traceroute to a host or domain
- Discover active devices on the local subnet (auto-detected or custom)
- Ping a specific target
- Compare two output files to spot changes (new vendors/IPs)

---

## Example Output

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

---

## Project Structure

```text
Network-Topology-Reconnaissance-Suite/
├── Scan.py                   # Main entry point of the application
├── setup.sh                  # Automated installation script
├── requirements.txt          # Python dependencies (scapy, sqlalchemy, etc.)
├── network_sniffer.db        # SQLite database (auto-generated)
├── LICENSE                   # License file
├── README.md                 # Project documentation
└── core/                     # Application core modules
    ├── compare.py            # File and data comparison module
    ├── database.py           # SQLite database management & SQLAlchemy models
    └── sniff.py               # Packet sniffer & anomaly detector (Scapy)
```

---

## Uninstalling

To completely remove NetworkSniffer from your system, run the included uninstall script:

```bash
chmod +x uninstall.sh
sudo ./uninstall.sh
```

The script will:
1. Ask for confirmation before making any changes.
2. Remove the `NetworkSniffer` command from `/usr/local/bin`.
3. Remove the installation directory `/opt/networksniffer` (including the Python virtual environment).
4. Optionally remove leftover data files, such as `network_sniffer.db`, if it finds any.

If `uninstall.sh` is not available, you can remove the tool manually:

```bash
sudo rm -f /usr/local/bin/NetworkSniffer
sudo rm -rf /opt/networksniffer
```

---

## Legal Notice

This tool is intended for educational purposes, security audits, and administration of networks you own or are explicitly authorized to test. Running scanning/reconnaissance tools against third-party networks without permission may violate local law. Users are solely responsible for lawful use of this tool.

---

## License

Distributed under the MIT License. See the `LICENSE` file for details.

---

## Contributing

Pull requests and suggestions are welcome. For larger changes, open an issue first to discuss what you'd like to change.

## Contact

For questions or bug reports, open an [issue](https://github.com/michalitsiosp/Network-Topology-Reconnaissance-Suite/issues) on the repository.
