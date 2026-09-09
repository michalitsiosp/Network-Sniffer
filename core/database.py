import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker


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
