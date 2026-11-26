"""
Gather stats from civic_cases.json for dashboard spec grounding.
"""
import json
import sys
from pathlib import Path
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding="utf-8")

cases = json.loads(Path("data/processed/civic_cases.json").read_text(encoding="utf-8"))

print(f"Total cases: {len(cases)}")

# Tier distribution
tiers = Counter(c["priority_tier"] for c in cases)
print(f"\nTier distribution: {dict(tiers)}")

# Top wards by case count
ward_counts = Counter(c.get("primary_ward_name") or "Unknown" for c in cases)
print(f"\nTop 10 wards by case count:")
for w, n in ward_counts.most_common(10):
    print(f"  {w}: {n} cases")

# Top wards by HIGH cases
high_wards = Counter(c.get("primary_ward_name") or "Unknown" for c in cases if c["priority_tier"] == "HIGH")
print(f"\nWards with HIGH cases:")
for w, n in high_wards.most_common():
    print(f"  {w}: {n}")

# Score range
scores = [c["priority_score"] for c in cases]
print(f"\nScore range: {min(scores):.3f} - {max(scores):.3f}")
print(f"Score mean: {sum(scores)/len(scores):.3f}")

# Cluster method split
methods = Counter(c["cluster_method"] for c in cases)
print(f"\nCluster methods: {dict(methods)}")

# Complaint volume distribution
vols = [c["complaint_count"] for c in cases]
vols.sort(reverse=True)
print(f"\nComplaint volume: max={max(vols)} min={min(vols)} median={sorted(vols)[len(vols)//2]}")
print(f"Cases with 50+ complaints: {sum(1 for v in vols if v >= 50)}")
print(f"Cases with 20+ complaints: {sum(1 for v in vols if v >= 20)}")

# Unresolved rate
ur = [c["unresolved_rate_pct"] for c in cases]
print(f"\nUnresolved rate: max={max(ur):.1f}% min={min(ur):.1f}% mean={sum(ur)/len(ur):.1f}%")
print(f"Cases with 100% unresolved: {sum(1 for x in ur if x == 100.0)}")
print(f"Cases with 50%+ unresolved: {sum(1 for x in ur if x >= 50.0)}")

# Top categories
cats = Counter(c["problem_category"] for c in cases)
print(f"\nTop categories: {dict(cats)}")

# Has GPS centroid
gps = sum(1 for c in cases if c.get("centroid_lat") is not None)
print(f"\nCases with GPS centroid: {gps} / {len(cases)}")

# Geographic extent
extents = [c.get("geographic_extent_km") for c in cases if c.get("geographic_extent_km")]
if extents:
    print(f"Geo extent range: {min(extents):.2f} - {max(extents):.2f} km (n={len(extents)})")

# Agency distribution
agencies = Counter(c.get("responsible_agency") or "Unknown" for c in cases)
print(f"\nAgency distribution: {dict(agencies.most_common(5))}")
agency_conf = Counter(c.get("agency_confidence") for c in cases)
print(f"Agency confidence: {dict(agency_conf)}")

# Ward join confidence
join_conf = Counter(c.get("ward_join_confidence") for c in cases)
print(f"\nWard join confidence: {dict(join_conf)}")

# Years active distribution
years_active = Counter(len(c.get("years_active", [])) for c in cases)
print(f"\nYears active distribution: {dict(years_active)}")

# Top subcategories
subcats = Counter(c.get("representative_subcategory") for c in cases)
print(f"\nTop 10 subcategories:")
for s, n in subcats.most_common(10):
    print(f"  {s}: {n}")
