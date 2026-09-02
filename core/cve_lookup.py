import json
import urllib.parse
import urllib.request


def search_cve(service_name, version, max_results=5):
    """Ψάχνει στο NVD API για CVEs με βάση την υπηρεσία και την έκδοση.

    Επιστρέφει μια λίστα από dictionaries με τα ευρήματα.
    """
    query = f"{service_name} {version}"
    encoded_query = urllib.parse.quote(query)

    # NVD API v2.0 endpoint
    url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={encoded_query}&resultsPerPage={max_results}"

    headers = {
        # Συνιστάται Custom User-Agent για να μην τρώει block από το API
        "User-Agent": "Network-Topology-Recon-Suite/1.0"
    }

    try:
        req = urllib.request.Request(url, headers=headers)
        # Timeout 5 δευτερόλεπτα για να μην κολλάει το CLI
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                return []

            data = json.loads(response.read().decode("utf-8"))
            vulnerabilities = data.get("vulnerabilities", [])

            results = []
            for item in vulnerabilities:
                cve_data = item.get("cve", {})
                cve_id = cve_data.get("id", "N/A")

                # Παίρνουμε την αγγλική περιγραφή
                descriptions = cve_data.get("descriptions", [])
                description = "No description available."
                for desc in descriptions:
                    if desc.get("lang") == "en":
                        description = desc.get("value", "")
                        break

                # Παίρνουμε το CVSS Score (v3.1 ή v3.0 ή v2)
                metrics = cve_data.get("metrics", {})
                cvss_score = "N/A"
                severity = "UNKNOWN"

                if "cvssMetricV31" in metrics:
                    cvss_data = metrics["cvssMetricV31"][0]["cvssData"]
                    cvss_score = cvss_data.get("baseScore", "N/A")
                    severity = cvss_data.get("baseSeverity", "UNKNOWN")
                elif "cvssMetricV30" in metrics:
                    cvss_data = metrics["cvssMetricV30"][0]["cvssData"]
                    cvss_score = cvss_data.get("baseScore", "N/A")
                    severity = cvss_data.get("baseSeverity", "UNKNOWN")

                results.append(
                    {
                        "id": cve_id,
                        "score": cvss_score,
                        "severity": severity,
                        "description": (
                            description[:120] + "..."
                            if len(description) > 120
                            else description
                        ),
                    }
                )

            return results

    except Exception:
        # Αν υπάρξει timeout ή error στο API, επιστρέφουμε άδεια λίστα
        return []


def format_cve_output(service_name, version, cve_list):
    """Μορφοποιεί τα αποτελέσματα για εκτύπωση στο τερματικό."""
    output = f"\n[+] Vulnerability Search Results for: {service_name} {version}\n"
    output += "=" * 70 + "\n"

    if not cve_list:
        output += "[-] No vulnerabilities found or API limit reached.\n"
        return output

    for cve in cve_list:
        output += f"• {cve['id']} | Score: {cve['score']} ({cve['severity']})\n"
        output += f"  Summary: {cve['description']}\n"
        output += "-" * 70 + "\n"

    return output
