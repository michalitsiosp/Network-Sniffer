#!/bin/bash
set -e

INSTALL_DIR="/opt/networksniffer"
BIN_PATH="/usr/local/bin/NetworkSniffer"

echo "[*] Updating package list..."
sudo apt update

echo "[*] Installing Nmap, Python pip, and ping tools..."
sudo apt install -y nmap python3-pip iputils-ping

echo "[*] Installing Python packages from requirements.txt..."
pip3 install -r requirements.txt --break-system-packages 2>/dev/null || pip3 install -r requirements.txt

echo "[*] Installing NetworkSniffer to $INSTALL_DIR..."
sudo mkdir -p "$INSTALL_DIR"
sudo cp -r ./* "$INSTALL_DIR"

sudo tee "$BIN_PATH" > /dev/null << 'EOF'
#!/bin/bash
cd /opt/networksniffer
exec python3 Scan.py "$@"
EOF

sudo chmod +x "$BIN_PATH"

echo "[+] Installation complete! Run it with: sudo NetworkSniffer"
