import json
import os
import shutil
import subprocess
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker

RED = "\033[91m"
GREEN = "\033[92m"
CYAN = "\033[96m"
RESET = "\033[0m"


DB_NAME = "network_sniffer.db"
engine = create_engine(f"sqlite:///{DB_NAME}", echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class ScanReport(Base):
    __tablename__ = "scans"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now)
    scan_type = Column(String(50), nullable=False)  # Παράδειγμα: 'nmap', 'ping'
    target = Column(String(100), nullable=True)
    raw_data = Column(Text, nullable=False)        # Τα αποτελέσματα σε μορφή κειμένου ή JSON


def init_db():
    """Δημιουργεί τον πίνακα στη βάση αν δεν υπάρχει."""
    Base.metadata.create_all(bind=engine)

def save_report_to_db(scan_type, data, target="Local"):
    """Αποθηκεύει το report στη SQLite."""
    init_db()
    session = SessionLocal()
    try:
        # Αν τα δεδομένα είναι λίστα ή λεξικό, τα κάνουμε JSON string
        if isinstance(data, (dict, list)):
            formatted_data = json.dumps(data, indent=4)
        else:
            formatted_data = str(data)

        new_scan = ScanReport(
            scan_type=scan_type,
            target=target,
            raw_data=formatted_data
        )
        session.add(new_scan)
        session.commit()
        print(f"\033[92m[+] Report saved!\033[0m")
    except Exception as e:
        session.rollback()
        print(f"\033[91m[-] Database error: {e}\033[0m")
    finally:
        session.close()


def open_in_sqlitebrowser():
    """Ανοίγει το αρχείο SQLite (network_sniffer.db) με το DB Browser for SQLite (sqlitebrowser)."""
    db_path = os.path.abspath(DB_NAME)

    if not os.path.exists(db_path):
        print(
            f"{RED}[-] Database file not found at {db_path}.{RESET}\n"
            f"    Run a scan and save at least one report first."
        )
        return

    if shutil.which("sqlitebrowser") is None:
        print(
            f"{RED}[-] sqlitebrowser is not installed.{RESET}\n"
            f"    Install it with: {CYAN}sudo apt install sqlitebrowser{RESET}"
        )
        return

    print(f"{CYAN}[*] Opening {db_path} in sqlitebrowser...{RESET}")
    try:
        # Non-blocking: the CLI menu stays usable while the GUI window is open
        subprocess.Popen(
            ["sqlitebrowser", db_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"{GREEN}[+] sqlitebrowser launched.{RESET}")
    except FileNotFoundError:
        print(f"{RED}[-] Could not find the sqlitebrowser executable.{RESET}")
    except Exception as e:
        print(f"{RED}[-] Failed to launch sqlitebrowser: {e}{RESET}")
