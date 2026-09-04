import os
import re
import json
import difflib
from glob import glob

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

REPORT_PATTERN = re.compile(r"^report_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})_(.+)\.txt$")


def list_reports(directory="."):
    """
    Βρίσκει όλα τα report_*.txt αρχεία στον φάκελο, ομαδοποιημένα ανά vendor
    (netdiscover, nmap, traceroute, ping, cve).
    Επιστρέφει dict: {vendor: [(timestamp, filepath), ...]}, ταξινομημένο χρονολογικά.
    """
    grouped = {}
    for path in glob(os.path.join(directory, "report_*.txt")):
        filename = os.path.basename(path)
        match = REPORT_PATTERN.match(filename)
        if not match:
            continue
        timestamp, vendor = match.groups()
        grouped.setdefault(vendor, []).append((timestamp, path))

    for vendor in grouped:
        grouped[vendor].sort(key=lambda x: x[0])

    return grouped


def _load_content(filepath):
    """Διαβάζει το αρχείο· προσπαθεί JSON parse, αλλιώς επιστρέφει raw text."""
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()
    try:
        return json.loads(raw), True   # (data, is_structured)
    except (json.JSONDecodeError, ValueError):
        return raw, False


def _structured_diff(old_data, new_data):
    """
    Σύγκριση δύο λιστών από dicts (π.χ. netdiscover output).
    Ταιριάζει entries βάσει του πεδίου 'ip' (ή 'IP' αν υπάρχει).
    """
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
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
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


def compare_reports(old_path, new_path):
    """Συγκρίνει δύο report αρχεία και επιστρέφει readable diff."""
    old_data, old_structured = _load_content(old_path)
    new_data, new_structured = _load_content(new_path)

    header = (
        f"{CYAN}Comparing:{RESET}\n"
        f"  Previous: {os.path.basename(old_path)}\n"
        f"  Latest:   {os.path.basename(new_path)}\n"
    )

    if old_structured and new_structured and isinstance(old_data, list) and isinstance(new_data, list):
        body = _structured_diff(old_data, new_data)
    else:
        # fallback: αν το ένα είναι structured και το άλλο όχι, σύγκρινε ως text
        old_text = old_data if not old_structured else json.dumps(old_data, indent=4)
        new_text = new_data if not new_structured else json.dumps(new_data, indent=4)
        body = _text_diff(old_text, new_text)

    return header + "\n" + body


def interactive_compare(directory="."):
    """Interactive menu flow: επιλογή vendor -> επιλογή δύο reports -> εμφάνιση diff."""
    grouped = list_reports(directory)

    if not grouped:
        print(f"{RED}[-] No reports found in '{directory}'.{RESET}")
        return

    vendors = sorted(grouped.keys())
    print(f"\n{CYAN}Available report types:{RESET}")
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
    for i, (timestamp, path) in enumerate(reports, start=1):
        print(f"{CYAN}{i}. {timestamp}{RESET}")

    try:
        idx1 = int(input(f"{YELLOW}Select FIRST (older) report: {RESET}").strip()) - 1
        idx2 = int(input(f"{YELLOW}Select SECOND (newer) report: {RESET}").strip()) - 1
        old_path = reports[idx1][1]
        new_path = reports[idx2][1]
    except (ValueError, IndexError):
        print(f"{RED}[-] Invalid selection.{RESET}")
        return

    print()
    print(compare_reports(old_path, new_path))
