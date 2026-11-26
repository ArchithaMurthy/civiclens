"""
Build public/data/complaints_lookup.json — a compact keyed lookup of only the
complaints that appear in at least one civic case.

Output schema (per entry):
  complaint_id → {
    created_at, ward_name, subcategory, status,
    description, latitude, longitude
  }

Keeps only the fields needed by the Case Detail complaint table.
Only complaints referenced in civic_cases.json are included (~3,895).
"""
import json
from pathlib import Path

CASES_SRC = Path("data/processed/civic_cases.json")
COMPLAINTS_SRC = Path("data/processed/complaints_normalised.json")
OUT = Path("civiclens-ui/public/data/complaints_lookup.json")

print("Loading cases…")
cases = json.loads(CASES_SRC.read_text(encoding="utf-8"))

# Collect all complaint_ids referenced in cases
needed_ids: set[str] = set()
for c in cases:
    needed_ids.update(c.get("complaint_ids", []))
print(f"Need {len(needed_ids)} complaint IDs from {len(cases)} cases")

print("Loading complaints…")
complaints = json.loads(COMPLAINTS_SRC.read_text(encoding="utf-8"))

lookup: dict[str, dict] = {}
missing = 0
for r in complaints:
    cid = r["complaint_id"]
    if cid not in needed_ids:
        continue
    desc = r.get("description") or r.get("title") or ""
    entry: dict = {
        "d": (r.get("created_at") or "")[:10],      # date only (10 chars)
        "w": r.get("ward_name") or "",
        "s": r.get("subcategory") or "",
        "t": r.get("status") or "",
        "x": desc[:120].strip(),
    }
    lat = r.get("latitude")
    lon = r.get("longitude")
    if lat is not None and lon is not None:
        entry["la"] = lat
        entry["lo"] = lon
    lookup[cid] = entry

found = len(lookup)
missing = len(needed_ids) - found
print(f"Found {found}/{len(needed_ids)} complaint IDs in normalised data ({missing} missing)")

OUT.write_text(json.dumps(lookup, ensure_ascii=False), encoding="utf-8")
size_kb = OUT.stat().st_size / 1024
print(f"Written: {OUT} ({size_kb:.0f} KB)")
