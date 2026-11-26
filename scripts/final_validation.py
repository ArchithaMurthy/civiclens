import json
import sys
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")

cases = json.loads(Path("data/processed/civic_cases.json").read_text(encoding="utf-8"))

all_have_field = all("ward_join_confidence" in c for c in cases)
print(f"ward_join_confidence in all cases: {all_have_field}")

begur_notes = [
    (c["ward_join_confidence"], c["ward_join_note"])
    for c in cases if "Begur" in (c.get("ward_join_note") or "")
]
correct = [n for _, n in begur_notes if "datameet243=227" in n]
wrong = [n for _, n in begur_notes if "datameet243=204" in n]
print(f"Begur cases with CORRECT datameet243=227: {len(correct)}")
print(f"Begur cases with WRONG   datameet243=204: {len(wrong)}")

files = [
    "data/processed/sprint3_audit_report.md",
    "data/processed/sprint3_dashboard_spec.md",
    "data/processed/ward_name_to_datameet243.json",
    "data/processed/civic_cases.json",
]
for f in files:
    p = Path(f)
    status = "OK" if p.exists() else "MISSING"
    size = p.stat().st_size if p.exists() else 0
    print(f"  {f}: {status} ({size:,} bytes)")

tiers = Counter(c["priority_tier"] for c in cases)
jconf = Counter(c.get("ward_join_confidence", "MISSING") for c in cases)
print(f"Tiers: {dict(tiers)}")
print(f"Ward join confidence: {dict(jconf)}")
print(f"Total cases: {len(cases)}")
