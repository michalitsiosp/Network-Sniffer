#!/bin/bash
set -e

if [ "$EUID" -ne 0 ]; then
  echo -e "\033[91m[-] Error: Please run setup.sh as root (e.g., sudo ./setup.sh)\033[0m"
  exit 1
fi

INSTALL_DIR="/opt/networksniffer"
BIN_PATH="/usr/local/bin/NetworkSniffer"

echo "[*] Updating package list..."
apt update

echo "[*] Installing system dependencies (Nmap, Python venv, pcap, ping, sqlitebrowser)..."
apt install -y nmap python3-pip python3-venv iputils-ping libpcap-dev sqlitebrowser

echo "[*] Creating installation directory at $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"

echo "[*] Copying project files..."
rsync -a --exclude='venv' --exclude='pentest-venv' --exclude='.git' ./ "$INSTALL_DIR/"

echo "[*] Setting up Python Virtual Environment..."
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --upgrade pip
"$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

echo "[*] Creating global executable at $BIN_PATH..."
tee "$BIN_PATH" > /dev/null << 'EOF'
#!/bin/bash
cd /opt/networksniffer
exec /opt/networksniffer/venv/bin/python3 Scan.py "$@"
EOF

chmod +x "$BIN_PATH"

echo -e "\n\033[92m[+] Installation complete! You can now run the tool from anywhere using:\033[0m"
echo -e "\033[96msudo NetworkSniffer\033[0m\n"
