import json
import difflib
from core.database import SessionLocal, ScanReport, init_db

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"


def list_reports_from_db():
    """
    Αναζητά στη βάση δεδομένων όλα τα αποθηκευμένα reports, 
    ομαδοποιημένα ανά scan_type (vendor).
    Επιστρέφει dict: {scan_type: [(id, timestamp), ...]}, ταξινομημένο χρονολογικά.
    """
    init_db()  # Εξασφαλίζει ότι ο πίνακας "scans" υπάρχει, ακόμα κι αν δεν έχει γίνει ποτέ save
    session = SessionLocal()
    try:
        scans = session.query(ScanReport.id, ScanReport.scan_type, ScanReport.timestamp).order_by(ScanReport.timestamp.asc()).all()
    finally:
        session.close()

    grouped = {}
    for scan_id, scan_type, timestamp in scans:
        # Μετατροπή timestamp σε string αν χρειάζεται
        ts_str = timestamp.strftime("%Y-%m-%d_%H-%M-%S") if timestamp else "unknown_time"
        grouped.setdefault(scan_type, []).append((scan_id, ts_str))

    return grouped


def _load_content_from_db(scan_id):
    """Φέρνει τα raw_data ενός scan από τη βάση και προσπαθεί JSON parse."""
    session = SessionLocal()
    try:
        scan = session.query(ScanReport).filter(ScanReport.id == scan_id).first()
        if not scan:
            return None, False
        raw = scan.raw_data
    finally:
        session.close()

    try:
        return json.loads(raw), True  # (data, is_structured)
    except (json.JSONDecodeError, TypeError, ValueError):
        return raw, False


def _structured_diff(old_data, new_data):
    """Σύγκριση δύο λιστών από dicts (π.χ. netdiscover output)."""
    def key_of(entry):
        if isinstance(entry, dict):
            for k in ("ip", "IP", "address"):
                if k in entry:
                    return entry[k]
        return json.dumps(entry, sort_keys=True)

    old_map = {key_of(e): e for e in old_data} if isinstance(old_data, list) else {}
    new_map = {key_of(e): e for e in new_data} if isinstance(new_data, list) else {}

    added = [new_map[k] for k in new_map if k not in old_map]
    removed = [old_map[k] for k in old_map if k not in new_map]
    changed = []
    for k in new_map:
        if k in old_map and old_map[k] != new_map[k]:
            changed.append((old_map[k], new_map[k]))

    output = []
    if added:
        output.append(f"{GREEN}[+] New devices/entries found ({len(added)}):{RESET}")
        for entry in added:
            output.append(f"    {GREEN}+ {entry}{RESET}")
    if removed:
        output.append(f"{RED}[-] Devices/entries no longer seen ({len(removed)}):{RESET}")
        for entry in removed:
            output.append(f"    {RED}- {entry}{RESET}")
    if changed:
        output.append(f"{YELLOW}[~] Changed entries ({len(changed)}):{RESET}")
        for old_e, new_e in changed:
            output.append(f"    {YELLOW}~ {old_e}  ->  {new_e}{RESET}")
    if not added and not removed and not changed:
        output.append(f"{CYAN}[=] No differences found. Network state unchanged.{RESET}")

    return "\n".join(output)


def _text_diff(old_text, new_text):
    """Line-by-line diff για raw text reports (π.χ. nmap, traceroute)."""
    old_lines = old_text.splitlines() if old_text else []
    new_lines = new_text.splitlines() if new_text else []
    diff = difflib.unified_diff(
        old_lines, new_lines,
        fromfile="previous scan", tofile="latest scan",
        lineterm=""
    )

    output = []
    has_diff = False
    for line in diff:
        has_diff = True
        if line.startswith("+") and not line.startswith("+++"):
            output.append(f"{GREEN}{line}{RESET}")
        elif line.startswith("-") and not line.startswith("---"):
            output.append(f"{RED}{line}{RESET}")
        elif line.startswith("@@"):
            output.append(f"{CYAN}{line}{RESET}")
        else:
            output.append(line)

    if not has_diff:
        return f"{CYAN}[=] No differences found. Output unchanged.{RESET}"

    return "\n".join(output)


def compare_reports(old_id, new_id):
    """Συγκρίνει δύο reports από τη βάση βάσει των IDs τους."""
    old_data, old_structured = _load_content_from_db(old_id)
    new_data, new_structured = _load_content_from_db(new_id)

    header = (
        f"{CYAN}Comparing Database Records:{RESET}\n"
        f"  Previous Scan ID: {old_id}\n"
        f"  Latest Scan ID:   {new_id}\n"
    )

    if old_structured and new_structured and isinstance(old_data, list) and isinstance(new_data, list):
        body = _structured_diff(old_data, new_data)
    else:
        old_text = old_data if not old_structured else json.dumps(old_data, indent=4)
        new_text = new_data if not new_structured else json.dumps(new_data, indent=4)
        body = _text_diff(old_text, new_text)

    return header + "\n" + body


def interactive_compare():
    """Interactive menu flow: επιλογή τύπου σάρωσης -> επιλογή δύο ID reports -> εμφάνιση diff."""
    grouped = list_reports_from_db()

    if not grouped:
        print(f"{RED}[-] No reports found in the database.{RESET}")
        return

    vendors = sorted(grouped.keys())
    print(f"\n{CYAN}Available report types in Database:{RESET}")
    for i, vendor in enumerate(vendors, start=1):
        count = len(grouped[vendor])
        print(f"{CYAN}{i}. {vendor} ({count} report{'s' if count != 1 else ''}){RESET}")

    choice = input(f"\n{YELLOW}Select report type to compare: {RESET}").strip()
    try:
        vendor = vendors[int(choice) - 1]
    except (ValueError, IndexError):
        print(f"{RED}[-] Invalid selection.{RESET}")
        return

    reports = grouped[vendor]
    if len(reports) < 2:
        print(f"{RED}[-] Need at least 2 reports of type '{vendor}' to compare (found {len(reports)}).{RESET}")
        return

    print(f"\n{CYAN}Available '{vendor}' reports:{RESET}")
    for i, (scan_id, timestamp) in enumerate(reports, start=1):
        print(f"{CYAN}{i}. ID: {scan_id} | Time: {timestamp}{RESET}")

    try:
        idx1 = int(input(f"{YELLOW}Select FIRST (older) report number: {RESET}").strip()) - 1
        idx2 = int(input(f"{YELLOW}Select SECOND (newer) report number: {RESET}").strip()) - 1
        old_id = reports[idx1][0]
        new_id = reports[idx2][0]
    except (ValueError, IndexError):
        print(f"{RED}[-] Invalid selection.{RESET}")
        return

    print()
    print(compare_reports(old_id, new_id))
