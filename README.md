# Network Sniffer

**Network Topology Reconnaissance Suite** — a Python-based network analysis tool built on Scapy, combining ICMP traceroute, automated ARP subnet discovery, MAC vendor identification, Nmap scanning, CVE lookup, and a live traffic sniffer with basic anomaly detection.

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
| **Netdiscover (ARP Scan)** | Uses Layer 2 ARP broadcast queries to reveal live devices on the local network (LAN), auto-detecting the current `/24` subnet. |
| **Traceroute** | Maps router hops to a remote host/domain using raw ICMP packets. |
| **Nmap Scan** | Runs Nmap against a target with four presets: quick scan, service/script scan, aggressive OS scan, and full stealth scan. |
| **Ping Target** | Sends ICMP pings to a specified target through Scapy. |
| **CVE Lookup** | Queries the NVD API for known vulnerabilities matching a given service name and version. |
| **Compare Reports** | Diffs two saved reports from the database (same scan type) and highlights what was added, removed, or changed. |
| **Network Sniffer & IDS** | Captures live traffic on a chosen interface and flags basic anomalies (possible port scans, SYN floods). |
| **Open Database (sqlitebrowser)** | Launches DB Browser for SQLite pointed at `network_sniffer.db` so you can browse saved reports with a GUI. |
| **MAC Vendor Identification** | Resolves MAC addresses to hardware manufacturers (e.g. Apple, Xiaomi, TP-Link) via the macvendors.com API. |

---

## Requirements

- **OS:** Linux / Unix-based system
- **Python:** 3.8+ (3.10+ recommended)
- **Permissions:** Root / sudo (required for Scapy raw socket creation, ARP scanning, and packet sniffing)
- **System tools:** `nmap` (Nmap Scan), `sqlitebrowser` (Open Database option) — both installed automatically by `setup.sh`

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
git clone https://github.com/michalitsiosp/Network-Sniffer.git
cd Network-Sniffer

# Make the setup script executable and run it with sudo
chmod +x setup.sh
sudo ./setup.sh
```

`setup.sh` will:
1. Install the required system packages (`nmap`, `python3-venv`, `libpcap-dev`, `iputils-ping`, `sqlitebrowser`).
2. Create an isolated Python virtual environment at `/opt/networksniffer/venv`.
3. Install the necessary Python libraries (`SQLAlchemy`, `scapy`).
4. Make the tool available system-wide as the `NetworkSniffer` command.

---

## Usage

Once installed, run the suite from anywhere on your system with:

```bash
sudo NetworkSniffer
```

Root/sudo is required because the tool opens raw sockets to send and receive ICMP/ARP packets and to sniff live traffic.

From the interactive menu you can:

1. **Netdiscover** — scan the local `/24` subnet for live hosts and their MAC vendors.
2. **Traceroute** — trace the route to a host or domain, hop by hop.
3. **Nmap Scan** — run a quick, standard, aggressive, or full stealth Nmap scan against a target.
4. **Ping Target** — send ICMP echo requests to a host and see round-trip times.
5. **CVE Lookup** — search the NVD database for vulnerabilities affecting a service/version.
6. **Compare Reports** — pick two saved reports of the same type and view a diff.
7. **Network Sniffer & IDS** — capture live traffic on an interface and get alerted on possible port scans or SYN floods.
8. **Open Database (sqlitebrowser)** — open `network_sniffer.db` in DB Browser for SQLite to inspect saved reports directly.
9. **Exit**

After most scans you'll be asked whether to save the report to the local SQLite database (`network_sniffer.db`) — say yes if you want to use **Compare Reports** or browse it later with **Open Database**.

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
Network-Sniffer/
├── Scan.py                   # Main entry point / interactive menu
├── setup.sh                  # Automated installation script
├── uninstall.sh               # Automated removal script
├── requirements.txt          # Python dependencies (scapy, SQLAlchemy)
├── network_sniffer.db        # SQLite database (auto-generated on first save)
├── LICENSE                   # License file
├── SECURITY.md                # Security policy
├── README.md                 # Project documentation
└── core/                     # Application core modules
    ├── discovery.py          # Netdiscover (ARP scan) & ping
    ├── traceroute.py          # ICMP traceroute
    ├── scanner.py             # Nmap scan wrapper
    ├── cve_lookup.py           # NVD CVE lookup
    ├── sniff.py                # Live packet sniffer & anomaly detector
    ├── compare.py              # Report comparison / diffing
    └── database.py             # SQLite models, save/query, sqlitebrowser launcher
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

For questions or bug reports, open an [issue](https://github.com/michalitsiosp/Network-Sniffer/issues) on the repository.
