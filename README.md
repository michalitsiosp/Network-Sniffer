# 🛰️ Network Sniffer

**Network Topology Reconnaissance Suite** — Ένα εργαλείο δικτυακής ανάλυσης βασισμένο σε Python και Scapy, που συνδυάζει ICMP Traceroute, αυτόματη ανακάλυψη υποδικτύου μέσω ARP, αναγνώριση κατασκευαστή MAC, και ping στόχου.

Σχεδιασμένο για security audits, system administrators, και network reconnaissance.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Linux%2FUnix-lightgrey)

---

## 📑 Περιεχόμενα

- [Βασικά Χαρακτηριστικά](#-βασικά-χαρακτηριστικά)
- [Προαπαιτούμενα](#-προαπαιτούμενα)
- [Εγκατάσταση](#️-εγκατάσταση--ρύθμιση)
- [Χρήση](#-χρήση)
- [Παράδειγμα Εξόδου](#-παράδειγμα-εξόδου)
- [Δομή Έργου](#-δομή-έργου)
- [Αποεγκατάσταση](#-αποεγκατάσταση)
- [Νομική Σημείωση](#️-νομική-σημείωση)
- [Άδεια Χρήσης](#-άδεια-χρήσης)

---

## 🚀 Βασικά Χαρακτηριστικά

| Λειτουργία | Περιγραφή |
|---|---|
| **Path Discovery (Traceroute)** | Χαρτογραφεί τα router hops προς έναν απομακρυσμένο host/domain χρησιμοποιώντας raw ICMP πακέτα. |
| **Auto Subnet Detection** | Ανιχνεύει αυτόματα το ενεργό δικτυακό interface για να στοχεύσει το τρέχον τοπικό IPv4 υποδίκτυο (π.χ. `192.168.1.0/24`). |
| **Active Host Discovery (Netdiscover)** | Χρησιμοποιεί ερωτήματα ARP broadcast σε επίπεδο 2 (Layer 2) για να αποκαλύψει ενεργές συσκευές στο τοπικό δίκτυο (LAN). |
| **MAC Vendor Identification** | Αντιστοιχίζει φυσικές διευθύνσεις MAC σε κατασκευαστές υλικού (π.χ. Apple, Xiaomi, TP-Link) μέσω REST API ερωτημάτων. |
| **Ping Target** | Στέλνει ICMP pings σε συγκεκριμένο στόχο μέσω Scapy. |
| **Compare Files** | Συγκρίνει 2 αρχεία εξόδου για να εντοπίσει κρυφούς/νέους vendors και IPs. |

---

## 📋 Προαπαιτούμενα

- **Λειτουργικό Σύστημα:** Linux / Unix-based system
- **Python:** 3.8+ (συνιστάται 3.10+)
- **Δικαιώματα:** Root / sudo (απαραίτητα για δημιουργία raw sockets από το Scapy, netdiscover, και λειτουργίες nmap)

### Python Dependencies (`requirements.txt`)

```
SQLAlchemy>=2.0.0
scapy>=2.5.0
```

---

## ⚙️ Εγκατάσταση & Ρύθμιση

Ο πιο εύκολος και καθαρός τρόπος εγκατάστασης του εργαλείου είναι μέσω του αυτοματοποιημένου script:

```bash
# Κλωνοποίηση του repository
git clone https://github.com/michalitsiosp/Network-Topology-Reconnaissance-Suite.git
cd Network-Topology-Reconnaissance-Suite

# Δώστε δικαίωμα εκτέλεσης στο setup script και τρέξτε το με sudo
chmod +x setup.sh
sudo ./setup.sh
```

Το `setup.sh`:
1. Εγκαθιστά αυτόματα όλα τα απαραίτητα πακέτα συστήματος.
2. Δημιουργεί απομονωμένο Python Virtual Environment στο `/opt/networksniffer/venv`.
3. Εγκαθιστά τις απαραίτητες βιβλιοθήκες (`SQLAlchemy`, `scapy`).
4. Κάνει το εργαλείο διαθέσιμο παντού στο σύστημα ως εντολή `NetworkSniffer`.

---

## ▶️ Χρήση

Μετά την εγκατάσταση, μπορείτε να τρέξετε τη σουίτα από οπουδήποτε στο σύστημά σας με:

```bash
sudo NetworkSniffer
```

> **Σημείωση:** Απαιτούνται δικαιώματα root/sudo, καθώς το εργαλείο δημιουργεί raw sockets για την αποστολή και λήψη ICMP/ARP πακέτων.

Μέσα από το interactive menu μπορείτε να επιλέξετε:
- Traceroute προς host/domain
- Ανακάλυψη ενεργών συσκευών στο τοπικό υποδίκτυο (auto-detected ή custom)
- Ping σε συγκεκριμένο στόχο
- Σύγκριση δύο αρχείων εξόδου για εντοπισμό αλλαγών (νέοι vendors/IPs)

---

## 🖥️ Παράδειγμα Εξόδου

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
192.168.1.15              ##:##:##:##:##:##       Intel Corporate
```

---

## 📁 Δομή Έργου

```
Network-Topology-Reconnaissance-Suite/
├── setup.sh                 # Script αυτόματης εγκατάστασης
├── requirements.txt          # Python dependencies
├── src/                       # Πηγαίος κώδικας εργαλείου
├── docs/                      # Τεκμηρίωση (προαιρετικό)
└── README.md
```

---

## 🧹 Αποεγκατάσταση

Αν το `setup.sh` παρέχει αντίστοιχο uninstall script, μπορείτε να τρέξετε:

```bash
sudo ./uninstall.sh
```

Διαφορετικά, μπορείτε να αφαιρέσετε χειροκίνητα το virtual environment και το symlink της εντολής:

```bash
sudo rm -rf /opt/networksniffer
sudo rm -f /usr/local/bin/NetworkSniffer
```

---

## ⚠️ Νομική Σημείωση

Αυτό το εργαλείο προορίζεται **αποκλειστικά για εκπαιδευτικούς σκοπούς, security audits, και διαχείριση δικτύων που σας ανήκουν ή για τα οποία έχετε ρητή εξουσιοδότηση**. Η χρήση εργαλείων σάρωσης/reconnaissance σε δίκτυα τρίτων χωρίς άδεια μπορεί να παραβιάζει τοπική νομοθεσία. Ο χρήστης φέρει την αποκλειστική ευθύνη για τη νόμιμη χρήση του εργαλείου.

---

## 📄 Άδεια Χρήσης

Διανέμεται υπό την άδεια **MIT**. Δείτε το αρχείο `LICENSE` για περισσότερες λεπτομέρειες.

---

## 🤝 Συνεισφορά

Pull requests και προτάσεις είναι ευπρόσδεκτες! Για σημαντικές αλλαγές, ανοίξτε πρώτα ένα issue για να συζητήσουμε τι θα θέλατε να αλλάξετε.

## 📬 Επικοινωνία

Για ερωτήσεις ή αναφορά προβλημάτων, ανοίξτε ένα [issue](https://github.com/michalitsiosp/Network-Topology-Reconnaissance-Suite/issues) στο repository.
