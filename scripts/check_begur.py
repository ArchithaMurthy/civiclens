import json
from pathlib import Path
from collections import Counter

cases = json.loads(Path("data/processed/civic_cases.json").read_text(encoding="utf-8"))

# --- Join confidence distribution ---
print("=== Ward join confidence distribution ===")
counts = Counter(c.get("ward_join_confidence", "MISSING") for c in cases)
for k, v in sorted(counts.items()):
    print(f"  {k}: {v}")

# --- Begur case ---
print("\n=== Begur cases ===")
begur = [c for c in cases if "Begur" in (c.get("ward_name") or c.get("primary_ward_name") or "")]
if not begur:
    # Try searching evidence items
    begur = [c for c in cases if any("Begur" in str(e) for e in c.get("evidence_items", []))]
    # Last resort: search ward_join_note
    if not begur:
        begur = [c for c in cases if "Begur" in c.get("ward_join_note", "")]

print(f"Found {len(begur)} Begur case(s)")
for c in begur[:3]:
    print(f"\n  case_id:            {c.get('case_id')}")
    print(f"  problem_title:      {c.get('problem_title')}")
    print(f"  ward_join_conf:     {c.get('ward_join_confidence')}")
    print(f"  ward_join_note:     {c.get('ward_join_note', '')[:140]}")
    print(f"  priority_score:     {c.get('priority_score')}")
    print(f"  priority_tier:      {c.get('priority_tier')}")
    for e in c.get("evidence_items", []):
        print(f"  evidence:           {e.get('description', '')[:120]}")

# --- Top-10 cases: join quality ---
print("\n=== Top 10 cases: join confidence ===")
top10 = sorted(cases, key=lambda c: c.get("priority_score", 0), reverse=True)[:10]
for c in top10:
    wn = c.get("ward_join_note", "")[:80]
    print(f"  [{c.get('ward_join_confidence')}] {c.get('problem_title','')[:55]:55s}  score={c.get('priority_score'):.3f}")

# --- Spot-check: does GEO-0044 / Begur cluster get datameet243=227? ---
print("\n=== Cases with ward_join_note mentioning datameet243=227 (Begur correct) ===")
dm227 = [c for c in cases if "datameet243=227" in c.get("ward_join_note", "")]
print(f"  Count: {len(dm227)}")
for c in dm227[:2]:
    print(f"  {c.get('case_id')} | {c.get('problem_title','')[:60]} | join={c.get('ward_join_confidence')}")
    print(f"  note: {c.get('ward_join_note','')[:140]}")
