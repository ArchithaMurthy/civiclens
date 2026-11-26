import json
import sys
from pathlib import Path
from collections import Counter

sys.stdout.reconfigure(encoding="utf-8")
cases = json.loads(Path("data/processed/civic_cases.json").read_text(encoding="utf-8"))

print("=== Ward join confidence distribution ===")
counts = Counter(c.get("ward_join_confidence", "MISSING") for c in cases)
for k, v in sorted(counts.items()):
    print(f"  {k}: {v}")

print()
begur = [c for c in cases if "Begur" in (c.get("ward_join_note") or "")]
print(f"Begur cases (by ward_join_note): {len(begur)}")
for c in begur[:2]:
    cid = c["case_id"]
    score = c["priority_score"]
    jconf = c["ward_join_confidence"]
    note = c["ward_join_note"][:130]
    print(f"  {cid} | score={score} | join={jconf}")
    print(f"  note: {note}")
    for e in c.get("evidence_items", []):
        d = e.get("description", "")
        if any(x in d for x in ["KAUN", "pothole", "work order", "crash"]):
            print(f"  ev: {d[:110]}")

print()
dm227 = [c for c in cases if "datameet243=227" in (c.get("ward_join_note") or "")]
print(f"Cases enriched to datameet243=227 (Begur correct): {len(dm227)}")
dm204 = [c for c in cases if "datameet243=204" in (c.get("ward_join_note") or "")]
print(f"Cases enriched to datameet243=204 (old wrong Kumaraswamy Layout): {len(dm204)}")

# Overall enrichment stats
enriched = [c for c in cases if c.get("ward_join_confidence") not in ("none", None)]
print(f"\nCases with enrichment (join != none): {len(enriched)}")
none_cases = [c for c in cases if c.get("ward_join_confidence") == "none"]
print(f"Cases with no enrichment (ward_id=199 'Other' etc): {len(none_cases)}")
