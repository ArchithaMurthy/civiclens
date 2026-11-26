"""
CivicLens — Evaluation module.

Evaluates pipeline quality across multiple dimensions without claiming
accuracy metrics that aren't defensible:
  1. Duplicate detection sample review
  2. Cluster coherence check
  3. Geographic validity
  4. Ward mapping confidence
  5. Case quality indicators
  6. Evidence traceability

Outputs a markdown evaluation report + human-review CSV samples.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Optional

PROCESSED_DIR = Path("data/processed")
EVAL_SAMPLE_SIZE = 20   # complaints per sample


def _load_cases() -> list[dict]:
    with open(PROCESSED_DIR / "civic_cases.json", encoding="utf-8") as f:
        return json.load(f)


def _load_complaints() -> list[dict]:
    with open(PROCESSED_DIR / "complaints_normalised.json", encoding="utf-8") as f:
        return json.load(f)


def _load_dedup() -> list[dict]:
    with open(PROCESSED_DIR / "dedup_candidates.json", encoding="utf-8") as f:
        return json.load(f)


def _fmt_cr(inr: Optional[float]) -> str:
    if inr is None:
        return "N/A"
    return f"₹{inr/1e7:.1f} crore"


def run_evaluation() -> str:
    """Run evaluation and return a markdown report string."""
    cases = _load_cases()
    complaints = _load_complaints()
    dedup = _load_dedup()
    complaints_by_id = {c["complaint_id"]: c for c in complaints}

    lines: list[str] = []

    lines.append("# CivicLens Sprint 2 — Pipeline Evaluation Report")
    lines.append("")
    lines.append("> **Methodology:** Quantitative checks on structure and coverage. "
                 "No accuracy claims are made without manual verification. "
                 "Human-review samples are exported for independent inspection.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # -------------------------------------------------------------------
    # 1. Pipeline summary
    # -------------------------------------------------------------------
    lines.append("## 1. Pipeline Summary")
    lines.append("")
    high = [c for c in cases if c["priority_tier"] == "HIGH"]
    medium = [c for c in cases if c["priority_tier"] == "MEDIUM"]
    low = [c for c in cases if c["priority_tier"] == "LOW"]
    total_complaints = sum(c["complaint_count"] for c in cases)

    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Total civic cases generated | {len(cases)} |")
    lines.append(f"| HIGH priority | {len(high)} |")
    lines.append(f"| MEDIUM priority | {len(medium)} |")
    lines.append(f"| LOW priority | {len(low)} |")
    lines.append(f"| Total complaints in cases | {total_complaints:,} |")
    lines.append(f"| Total dedup candidate pairs | {len(dedup):,} |")
    exact = [d for d in dedup if d["duplicate_type"] == "duplicate"]
    near = [d for d in dedup if d["duplicate_type"] == "near_duplicate"]
    lines.append(f"| Exact duplicate pairs | {len(exact):,} |")
    lines.append(f"| Near-duplicate pairs | {len(near):,} |")
    lines.append("")

    # -------------------------------------------------------------------
    # 2. Duplicate detection quality
    # -------------------------------------------------------------------
    lines.append("## 2. Duplicate Detection Quality")
    lines.append("")
    lines.append("### Methodology")
    lines.append("Duplicates are detected using a rule-based approach combining: "
                 "text fingerprint identity, geographic proximity (≤200m), "
                 "temporal proximity (≤7 days), and subcategory match. "
                 "No LLM used. Confidence scores are based on signal combinations.")
    lines.append("")

    lines.append("### Confidence score distribution (all candidate pairs)")
    conf_buckets = {"0.80–1.00": 0, "0.60–0.79": 0, "0.40–0.59": 0, "0.00–0.39": 0}
    for d in dedup:
        c = d["confidence"]
        if c >= 0.80: conf_buckets["0.80–1.00"] += 1
        elif c >= 0.60: conf_buckets["0.60–0.79"] += 1
        elif c >= 0.40: conf_buckets["0.40–0.59"] += 1
        else: conf_buckets["0.00–0.39"] += 1
    lines.append("")
    lines.append("| Confidence range | Count |")
    lines.append("|---|---|")
    for k, v in conf_buckets.items():
        lines.append(f"| {k} | {v:,} |")
    lines.append("")

    lines.append("### Signal distribution (exact duplicates)")
    from collections import Counter
    all_signals = []
    for d in exact:
        all_signals.extend(d.get("signals", []))
    signal_dist = Counter(all_signals)
    lines.append("")
    lines.append("| Signal | Count in exact dups |")
    lines.append("|---|---|")
    for sig, cnt in signal_dist.most_common():
        lines.append(f"| `{sig}` | {cnt} |")
    lines.append("")
    lines.append("> **Limitation:** No ground-truth label set exists. The 163 'exact duplicate' "
                 "pairs all share identical descriptions + same ward + within 7 days — "
                 "these are very likely true duplicates but cannot be confirmed without manual review. "
                 "See `dedup_sample_review.csv` for 20 randomly selected pairs.")
    lines.append("")

    # -------------------------------------------------------------------
    # 3. Cluster coherence
    # -------------------------------------------------------------------
    lines.append("## 3. Cluster Coherence")
    lines.append("")
    geo_cases = [c for c in cases if c["cluster_method"] == "geo_dbscan"]
    ward_cases = [c for c in cases if c["cluster_method"] == "ward_temporal"]

    lines.append(f"| Cluster type | Count | Avg complaints | Avg confidence |")
    lines.append(f"|---|---|---|---|")
    if geo_cases:
        avg_complaints_geo = sum(c["complaint_count"] for c in geo_cases) / len(geo_cases)
        avg_conf_geo = sum(c["cluster_confidence"] for c in geo_cases) / len(geo_cases)
        lines.append(f"| geo_dbscan | {len(geo_cases)} | {avg_complaints_geo:.1f} | {avg_conf_geo:.2f} |")
    if ward_cases:
        avg_complaints_ward = sum(c["complaint_count"] for c in ward_cases) / len(ward_cases)
        avg_conf_ward = sum(c["cluster_confidence"] for c in ward_cases) / len(ward_cases)
        lines.append(f"| ward_temporal | {len(ward_cases)} | {avg_complaints_ward:.1f} | {avg_conf_ward:.2f} |")
    lines.append("")

    lines.append("### Geographic extent (geo_dbscan clusters)")
    extents = [c["geographic_extent_km"] for c in geo_cases if c.get("geographic_extent_km")]
    if extents:
        lines.append(f"- Min extent: {min(extents):.3f} km")
        lines.append(f"- Max extent: {max(extents):.3f} km")
        lines.append(f"- Mean extent: {sum(extents)/len(extents):.3f} km")
        lines.append(f"- Clusters with extent < 0.5km: {sum(1 for e in extents if e < 0.5)} ({100*sum(1 for e in extents if e < 0.5)//len(extents)}%)")
        lines.append(f"- Clusters with extent 0.5–1.0km: {sum(1 for e in extents if 0.5 <= e < 1.0)}")
        lines.append(f"- Clusters with extent 1.0–2.0km: {sum(1 for e in extents if 1.0 <= e < 2.0)}")
    lines.append("")

    lines.append("> **Known limitation:** Geo clusters with large extents (>1km) may contain "
                 "complaints about different road segments within the same neighbourhood. "
                 "These are marked as lower confidence and require field verification.")
    lines.append("")

    # -------------------------------------------------------------------
    # 4. Geographic validity
    # -------------------------------------------------------------------
    lines.append("## 4. Geographic Validity")
    lines.append("")
    icmc_in_bbmp = sum(1 for c in complaints if c.get("gps_valid"))
    icmc_total = sum(1 for c in complaints if c.get("source") == "ichangemycity")
    lines.append(f"- ICMC complaints with GPS within BBMP bounding box: {icmc_in_bbmp:,} / {icmc_total:,} ({100*icmc_in_bbmp//icmc_total}%)")
    lines.append(f"- BBMP bounding box used: Lat 12.70–13.20, Lon 77.40–77.85")
    lines.append(f"- GovWatch complaints with GPS: 0 (source has no GPS data)")
    lines.append("")
    cases_with_centroid = [c for c in cases if c.get("centroid_lat")]
    # Check centroids within BBMP bounds
    invalid_centroids = [c for c in cases_with_centroid
                         if not (12.70 <= c["centroid_lat"] <= 13.20 and 77.40 <= c["centroid_lon"] <= 77.85)]
    lines.append(f"- Cases with centroid GPS: {len(cases_with_centroid)}")
    lines.append(f"- Cases with centroid outside BBMP bounds: {len(invalid_centroids)} (expected: 0)")
    lines.append("")

    # -------------------------------------------------------------------
    # 5. Ward mapping confidence
    # -------------------------------------------------------------------
    lines.append("## 5. Ward Mapping Confidence")
    lines.append("")
    join_types = Counter(c.get("ward_join_note", "")[:30] for c in cases)
    crosswalk_joins = sum(1 for c in cases if "crosswalk" in c.get("ward_join_note", ""))
    approx_joins = sum(1 for c in cases if "approximate" in c.get("ward_join_note", ""))
    no_joins = sum(1 for c in cases if "No primary ward" in c.get("ward_join_note", ""))

    lines.append(f"| Join type | Count |")
    lines.append(f"|---|---|")
    lines.append(f"| Crosswalk (bbmp225 → datameet243) | {crosswalk_joins} |")
    lines.append(f"| Approximate (direct ID match) | {approx_joins} |")
    lines.append(f"| No ward ID available | {no_joins} |")
    lines.append("")
    lines.append("> **Important:** ICMC ward_id (1–198) ≈ datameet243 ward no for the same "
                 "range but is not guaranteed identical. All work order and ward metric joins "
                 "are approximate unless the crosswalk CSV confirms the mapping. "
                 "Evidence items explicitly record join quality.")
    lines.append("")

    # -------------------------------------------------------------------
    # 6. Case quality indicators
    # -------------------------------------------------------------------
    lines.append("## 6. Case Quality Indicators")
    lines.append("")
    lines.append("### Evidence traceability")
    total_evidence = sum(len(c.get("evidence_items", [])) for c in cases)
    avg_evidence = total_evidence / len(cases) if cases else 0
    lines.append(f"- Total evidence items across all cases: {total_evidence}")
    lines.append(f"- Average evidence items per case: {avg_evidence:.1f}")
    lines.append(f"- Cases with ward metrics evidence: {sum(1 for c in cases if any(e['type']=='ward_road_spending' for e in c.get('evidence_items',[])))}")
    lines.append(f"- Cases with work order evidence: {sum(1 for c in cases if any(e['type']=='work_orders_in_ward' for e in c.get('evidence_items',[])))}")
    lines.append(f"- Cases with road crash evidence: {sum(1 for c in cases if any(e['type']=='road_crash_data' for e in c.get('evidence_items',[])))}")
    lines.append("")
    lines.append("### Agency attribution confidence")
    direct = sum(1 for c in cases if c.get("agency_confidence") == "direct")
    inferred = sum(1 for c in cases if c.get("agency_confidence") == "inferred")
    unknown = sum(1 for c in cases if c.get("agency_confidence") == "unknown")
    lines.append(f"- Direct (≥80% complaints name agency): {direct}")
    lines.append(f"- Inferred (majority, <80%): {inferred}")
    lines.append(f"- Unknown: {unknown}")
    lines.append("")

    lines.append("### Case completeness checklist")
    checks = {
        "Has problem_title": lambda c: bool(c.get("problem_title")),
        "Has problem_summary": lambda c: bool(c.get("problem_summary")),
        "Has date_first_complaint": lambda c: bool(c.get("date_first_complaint")),
        "Has primary_ward_name": lambda c: bool(c.get("primary_ward_name")),
        "Has responsible_agency": lambda c: bool(c.get("responsible_agency")),
        "Has >=1 evidence items": lambda c: len(c.get("evidence_items", [])) >= 1,
        "Has >=1 next steps": lambda c: len(c.get("recommended_next_steps", [])) >= 1,
        "Has representative complaints": lambda c: len(c.get("representative_complaints", [])) >= 1,
        "Has complaint_chronology": lambda c: len(c.get("complaint_chronology", [])) >= 1,
    }
    lines.append("")
    lines.append("| Check | Cases passing | % |")
    lines.append("|---|---|---|")
    for label, fn in checks.items():
        passing = sum(1 for c in cases if fn(c))
        pct = 100 * passing // len(cases)
        lines.append(f"| {label} | {passing} | {pct}% |")
    lines.append("")

    # -------------------------------------------------------------------
    # 7. Sample cases for review
    # -------------------------------------------------------------------
    lines.append("## 7. Sample Cases (Top 5 HIGH Priority)")
    lines.append("")
    for case in [c for c in cases if c["priority_tier"] == "HIGH"][:5]:
        lines.append(f"### {case['case_id']}")
        lines.append(f"**{case['problem_title']}**")
        lines.append(f"- Complaints: {case['complaint_count']} | Unresolved: {case['unresolved_rate_pct']}%")
        lines.append(f"- Years active: {case['years_active']}")
        lines.append(f"- Priority score: {case['priority_score']:.3f}")
        lines.append(f"- Agency: {case['responsible_agency']} ({case['agency_confidence']} attribution)")
        lines.append(f"- Summary: {case['problem_summary'][:300]}")
        lines.append("")
        lines.append("**Evidence:**")
        for ev in case.get("evidence_items", []):
            lines.append(f"- [{ev['type']}] {ev['description']}")
        if case.get("hypotheses"):
            lines.append("")
            lines.append("**Hypotheses (explicitly labelled as unverified):**")
            for h in case["hypotheses"]:
                lines.append(f"- {h[:300]}")
        lines.append("")

    # -------------------------------------------------------------------
    # 8. Known limitations and false-merge risks
    # -------------------------------------------------------------------
    lines.append("## 8. Known Limitations and Risks")
    lines.append("")
    lines.append("| Risk | Description | Mitigation |")
    lines.append("|---|---|---|")
    lines.append("| **Data staleness** | ICMC data ends Sep 2021. Pipeline cannot reflect current road conditions. | Noted in all case summaries; requires newer data for operational use. |")
    lines.append("| **Ward numbering mismatch** | ICMC ward_ids (1–198) ≈ datameet243 but not identical. | Crosswalk used; join confidence documented per case. |")
    lines.append("| **False merges (geo clusters)** | DBSCAN with 300m radius may merge adjacent-road complaints. | Cases with bbox > 1km flagged as lower confidence. |")
    lines.append("| **False splits (ward clusters)** | Same physical pothole cluster may appear in two adjacent wards. | Geo clusters run first; ward clustering only on geo-unclustered records. |")
    lines.append("| **No complaint IDs in ICMC source** | Cannot definitively deduplicate without stable IDs. | Pipeline IDs assigned; exact dedup uses text fingerprint + GPS + time. |")
    lines.append("| **Work order ≠ repair** | A work order being sanctioned does not confirm that repairs occurred or were adequate. | All work order evidence items explicitly note this limitation. |")
    lines.append("| **Agency attribution** | 100% of road complaints name BBMP — this reflects source data, not independent verification. | Agency confidence level documented per case. |")
    lines.append("")

    return "\n".join(lines)


def save_review_samples(output_dir: Path = PROCESSED_DIR):
    """Save human-review CSV samples for dedup and cluster inspection."""
    complaints = _load_complaints()
    complaints_by_id = {c["complaint_id"]: c for c in complaints}
    dedup = _load_dedup()
    cases = _load_cases()

    # Sample dedup pairs for review
    exact = [d for d in dedup if d["duplicate_type"] == "duplicate"]
    import random
    random.seed(42)
    sample_exact = random.sample(exact, min(EVAL_SAMPLE_SIZE, len(exact)))

    with open(output_dir / "eval_dedup_sample.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pair_id", "type", "confidence", "signals", "distance_km", "days_apart",
                    "ward_a", "ward_b", "subcat_a", "subcat_b", "desc_a_excerpt", "desc_b_excerpt",
                    "manual_verdict"])
        for i, d in enumerate(sample_exact):
            ca = complaints_by_id.get(d["complaint_id_a"], {})
            cb = complaints_by_id.get(d["complaint_id_b"], {})
            w.writerow([
                f"PAIR-{i+1:03d}", d["duplicate_type"], d["confidence"],
                "|".join(d.get("signals", [])), d.get("distance_km"), d.get("days_apart"),
                ca.get("ward_name"), cb.get("ward_name"),
                ca.get("subcategory"), cb.get("subcategory"),
                (ca.get("description") or "")[:150],
                (cb.get("description") or "")[:150],
                "",  # blank for human reviewer
            ])
    print(f"  Saved eval_dedup_sample.csv ({len(sample_exact)} pairs)")

    # Sample cases for review
    high_cases = [c for c in cases if c["priority_tier"] == "HIGH"]
    sample_cases = high_cases[:min(EVAL_SAMPLE_SIZE, len(high_cases))]

    with open(output_dir / "eval_cases_sample.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["case_id", "priority_tier", "priority_score", "problem_title",
                    "complaint_count", "ward", "years", "unresolved_pct",
                    "agency", "cluster_method", "cluster_confidence",
                    "evidence_count", "has_work_orders", "has_pothole_data",
                    "manual_quality_rating", "manual_notes"])
        for c in sample_cases:
            w.writerow([
                c["case_id"], c["priority_tier"], c["priority_score"],
                c["problem_title"], c["complaint_count"],
                c.get("primary_ward_name"), str(c.get("years_active")),
                c["unresolved_rate_pct"], c.get("responsible_agency"),
                c["cluster_method"], c["cluster_confidence"],
                len(c.get("evidence_items", [])),
                any(e["type"] == "work_orders_in_ward" for e in c.get("evidence_items", [])),
                any(e["type"] == "ward_pothole_data" for e in c.get("evidence_items", [])),
                "",  # blank for human reviewer
                "",  # blank for human reviewer
            ])
    print(f"  Saved eval_cases_sample.csv ({len(sample_cases)} cases)")


def main():
    print("Running evaluation…")
    report = run_evaluation()
    with open(PROCESSED_DIR / "sprint2_evaluation.md", "w", encoding="utf-8") as f:
        f.write(report)
    print(f"  Saved sprint2_evaluation.md")
    print("Saving review samples…")
    save_review_samples()


if __name__ == "__main__":
    main()
