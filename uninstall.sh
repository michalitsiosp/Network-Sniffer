#!/bin/bash
#
# uninstall.sh — Removes NetworkSniffer (Network Topology Reconnaissance Suite)
# from the system: virtual environment, global executable, and optionally
# leftover data files (SQLite database, logs).
#
set -e

# ANSI Color Codes
RED="\033[91m"
GREEN="\033[92m"
YELLOW="\033[93m"
CYAN="\033[96m"
RESET="\033[0m"

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------

# Must run as root, since the installer placed files under /opt and /usr/local/bin
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[-] Error: Please run uninstall.sh as root (e.g., sudo ./uninstall.sh)${RESET}"
  exit 1
fi

INSTALL_DIR="/opt/networksniffer"
BIN_PATH="/usr/local/bin/NetworkSniffer"

# Optional leftover data (created while the tool runs, not by setup.sh)
DB_CANDIDATES=(
  "$INSTALL_DIR/network_sniffer.db"
  "./network_sniffer.db"
  "$HOME/network_sniffer.db"
)

echo -e "${CYAN}==================================================${RESET}"
echo -e "${CYAN}   NetworkSniffer — Uninstaller${RESET}"
echo -e "${CYAN}==================================================${RESET}"
echo ""

# ---------------------------------------------------------------------------
# Confirmation prompt
# ---------------------------------------------------------------------------
read -r -p "$(echo -e "${YELLOW}[?] This will remove NetworkSniffer and its virtual environment. Continue? [y/N]: ${RESET}")" CONFIRM
case "$CONFIRM" in
  [yY][eE][sS]|[yY])
    ;;
  *)
    echo -e "${RED}[-] Uninstall cancelled.${RESET}"
    exit 0
    ;;
esac

echo ""
echo -e "${YELLOW}[*] Starting uninstallation of NetworkSniffer...${RESET}"

# ---------------------------------------------------------------------------
# 1. Remove the global executable / symlink
# ---------------------------------------------------------------------------
if [ -e "$BIN_PATH" ]; then
    echo -e "[*] Removing executable from $BIN_PATH..."
    rm -f "$BIN_PATH"
else
    echo -e "[*] Executable $BIN_PATH not found, skipping."
fi

# ---------------------------------------------------------------------------
# 2. Remove the installation directory (includes the Python virtual environment)
# ---------------------------------------------------------------------------
if [ -d "$INSTALL_DIR" ]; then
    echo -e "[*] Removing installation directory $INSTALL_DIR..."
    rm -rf "$INSTALL_DIR"
else
    echo -e "[*] Installation directory $INSTALL_DIR not found, skipping."
fi

# ---------------------------------------------------------------------------
# 3. Optionally remove leftover data (SQLite database, comparison outputs)
# ---------------------------------------------------------------------------
FOUND_DATA=0
for path in "${DB_CANDIDATES[@]}"; do
    if [ -f "$path" ]; then
        FOUND_DATA=1
    fi
done

if [ "$FOUND_DATA" -eq 1 ]; then
    echo ""
    read -r -p "$(echo -e "${YELLOW}[?] Leftover data files were found (e.g. network_sniffer.db). Remove them too? [y/N]: ${RESET}")" REMOVE_DATA
    case "$REMOVE_DATA" in
      [yY][eE][sS]|[yY])
        for path in "${DB_CANDIDATES[@]}"; do
            if [ -f "$path" ]; then
                echo -e "[*] Removing $path..."
                rm -f "$path"
            fi
        done
        ;;
      *)
        echo -e "[*] Keeping leftover data files."
        ;;
    esac
fi

# ---------------------------------------------------------------------------
# 4. Verify removal
# ---------------------------------------------------------------------------
if [ ! -e "$BIN_PATH" ] && [ ! -d "$INSTALL_DIR" ]; then
    echo ""
    echo -e "${GREEN}[+] NetworkSniffer has been completely removed from your system!${RESET}"
else
    echo ""
    echo -e "${RED}[-] Some components could not be removed. Please check permissions and try again.${RESET}"
    exit 1
fi
