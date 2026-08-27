#!/bin/bash

echo "[*] Updating package list..."
sudo apt update

echo "[*] Installing Nmap and Python dependencies..."
sudo apt install -y nmap python3-pip

echo "[*] Installing Python packages from requirements.txt..."
pip3 install -r requirements.txt --break-system-packages 2>/dev/null || pip3 install -r requirements.txt

echo "[+] Installation complete! You can now run your script."
