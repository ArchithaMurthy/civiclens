"""
Pre-process civic_cases.json into two sets of files for the React frontend:

  public/data/cases_index.json        — compact list of all 298 cases (for table/overview)
  public/data/cases/CASE-ID.json      — one file per case with full detail + all_complaints

Sprint 5-2 addition: each per-case file now includes an `all_complaints` array that
contains a compact record for every complaint_id in that case, resolved from
complaints_normalised.json. This lets CaseDetail display all complaints without a
separate lookup fetch.

Compact complaint schema (fields only needed by Case Detail table):
  complaint_id, created_at (date only), ward_name, subcategory, status,
  description (first 160 chars), latitude, longitude
"""
import json
from pathlib import Path

SRC = Path("data/processed/civic_cases.json")
COMPLAINTS_SRC = Path("data/processed/complaints_normalised.json")
OUT_INDEX = Path("civiclens-ui/public/data/cases_index.json")
OUT_FULL = Path("civiclens-ui/public/data/cases")
OUT_FULL.mkdir(parents=True, exist_ok=True)

print("Loading complaints…")
complaints_raw = json.loads(COMPLAINTS_SRC.read_text(encoding="utf-8"))

# Build a fast lookup: complaint_id → compact record
complaints_map: dict[str, dict] = {}
for r in complaints_raw:
    desc = (r.get("description") or r.get("title") or "").strip()
    entry: dict = {
        "complaint_id": r["complaint_id"],
        "created_at":   (r.get("created_at") or "")[:10],
        "ward_name":    r.get("ward_name") or "",
        "subcategory":  r.get("subcategory") or "",
        "status":       r.get("status") or "",
        "description":  desc[:160],
    }
    lat = r.get("latitude")
    lon = r.get("longitude")
    if lat is not None and lon is not None:
        entry["latitude"] = lat
        entry["longitude"] = lon
    complaints_map[r["complaint_id"]] = entry

print(f"Loaded {len(complaints_map)} complaint records")

print("Loading cases…")
cases = json.loads(SRC.read_text(encoding="utf-8"))

index = []
for c in cases:
    # --- Compact index row ---
    index.append({
        "case_id":                   c["case_id"],
        "cluster_id":                c["cluster_id"],
        "cluster_method":            c["cluster_method"],
        "problem_title":             c["problem_title"],
        "representative_subcategory": c["representative_subcategory"],
        "primary_ward_name":         c.get("primary_ward_name") or "Unknown",
        "complaint_count":           c["complaint_count"],
        "unresolved_rate_pct":       c["unresolved_rate_pct"],
        "open_count":                c["open_count"],
        "resolved_count":            c["resolved_count"],
        "reopened_count":            c["reopened_count"],
        "priority_tier":             c["priority_tier"],
        "priority_score":            c["priority_score"],
        "ward_join_confidence":      c.get("ward_join_confidence", "none"),
        "responsible_agency":        c.get("responsible_agency") or "Unknown",
        "years_active":              c.get("years_active", []),
        "date_first_complaint":      c.get("date_first_complaint"),
        "date_last_complaint":       c.get("date_last_complaint"),
        "centroid_lat":              c.get("centroid_lat"),
        "centroid_lon":              c.get("centroid_lon"),
        "geographic_extent_km":      c.get("geographic_extent_km"),
        "has_gps":                   c.get("centroid_lat") is not None,
    })

    # --- Full case detail with embedded all_complaints ---
    all_complaints = []
    missing = []
    for cid in c.get("complaint_ids", []):
        rec = complaints_map.get(cid)
        if rec:
            all_complaints.append(rec)
        else:
            missing.append(cid)
    if missing:
        print(f"  WARNING {c['case_id']}: {len(missing)} complaint IDs not found in normalised data")

    full = dict(c)
    full["all_complaints"] = all_complaints  # added field

    out_path = OUT_FULL / f"{c['case_id']}.json"
    out_path.write_text(json.dumps(full, ensure_ascii=False), encoding="utf-8")

OUT_INDEX.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")

# Stats
sizes = [( OUT_FULL / f"{c['case_id']}.json").stat().st_size for c in cases]
total_kb = sum(sizes) / 1024
max_kb = max(sizes) / 1024
print(f"\nIndex: {len(index)} cases -> {OUT_INDEX} ({OUT_INDEX.stat().st_size/1024:.0f} KB)")
print(f"Full:  {len(cases)} case files, total {total_kb:.0f} KB, max {max_kb:.0f} KB")
