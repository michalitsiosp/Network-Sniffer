 κανε μου και ενα uninstall.sh πληρες

Ορίστε ένα πλήρες και ασφαλές script απεγκατάστασης (uninstall.sh) που αφαιρεί όλα τα αρχεία, το Virtual Environment, την εκτελέσιμη εντολή και καθαρίζει το σύστημα.
Δημιουργία του uninstall.sh

Δημιούργησε το αρχείο στον κεντρικό φάκελο του project:
Bash

nano uninstall.sh

Επικόλλησε τον παρακάτω κώδικα:
Bash

#!/bin/bash
set -e

# ANSI Color Codes
RED="\033[91m"
GREEN="\033[92m"
YELLOW="\033[93m"
CYAN="\033[96m"
RESET="\033[0m"

# Έλεγχος αν ο χρήστης τρέχει το script ως root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[-] Error: Please run uninstall.sh as root (e.g., sudo ./uninstall.sh)${RESET}"
  exit 1
fi

INSTALL_DIR="/opt/networksniffer"
BIN_PATH="/usr/local/bin/NetworkSniffer"

echo -e "${YELLOW}[*] Starting uninstallation of NetworkSniffer...${RESET}"

# 1. Αφαίρεση του global executable
if [ -f "$BIN_PATH" ]; then
    echo -e "[*] Removing executable from $BIN_PATH..."
    rm -f "$BIN_PATH"
else
    echo -e "[*] Executable $BIN_PATH not found, skipping."
fi

# 2. Αφαίρεση του καταλόγου εγκατάστασης (μαζί με το Virtual Environment)
if [ -d "$INSTALL_DIR" ]; then
    echo -e "[*] Removing installation directory $INSTALL_DIR..."
    rm -rf "$INSTALL_DIR"
else
    echo -e "[*] Installation directory $INSTALL_DIR not found, skipping."
fi

echo -e "${GREEN}[+] NetworkSniffer has been completely removed from your system!${RESET}"

Δικαιώματα εκτέλεσης

Κάνε το script εκτελέσιμο τρέχοντας:
Bash

chmod +x uninstall.sh

Πώς να το χρησιμοποιήσεις

Όποτε θέλεις να αφαιρέσεις πλήρως την εφαρμογή από το σύστημα (από το /opt και το /usr/local/bin), αρκεί να τρέξεις:
Bash

sudo ./uninstall.sh

Ενημέρωση του README.md

Μπορείς να προσθέσεις την παρακάτω ενότητα στο README.md για να γνωρίζει ο χρήστης πώς γίνεται η απεγκατάσταση:
