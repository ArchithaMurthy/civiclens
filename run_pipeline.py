"""
CivicLens — Main pipeline runner.

Executes all stages in sequence:
  1. Ingest + normalise
  2. Duplicate detection
  3. Problem clustering
  4. Evidence enrichment
  5. Case generation
  6. Prioritisation
  7. Save outputs

Usage:
    python run_pipeline.py
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def run():
    t0 = datetime.utcnow()
    print("=" * 60)
    print("CivicLens Pipeline — started", t0.strftime("%Y-%m-%d %H:%M:%S UTC"))
    print("=" * 60)

    # -------------------------------------------------------------------
    # Stage 1: Ingest
    # -------------------------------------------------------------------
    print("\n[1/7] Ingesting and normalising datasets…")
    from pipeline.ingest import load_all
    complaints, work_orders, ward_metrics = load_all()
    complaints_by_id = {c.complaint_id: c for c in complaints}
    print(f"  {len(complaints)} complaints, {len(work_orders)} work orders, {len(ward_metrics)} wards")

    # -------------------------------------------------------------------
    # Stage 2: Duplicate detection (road subset only)
    # -------------------------------------------------------------------
    print("\n[2/7] Duplicate detection on road infrastructure complaints…")
    from pipeline.dedup import DuplicateDetector, DUPLICATE, NEAR_DUPLICATE
    road_icmc = [c for c in complaints if c.source == "ichangemycity" and c.category == "road_infrastructure"]
    detector = DuplicateDetector(road_icmc)
    dup_candidates = detector.detect()
    exact_dups = [d for d in dup_candidates if d.duplicate_type == DUPLICATE]
    near_dups = [d for d in dup_candidates if d.duplicate_type == NEAR_DUPLICATE]
    related = [d for d in dup_candidates if d.duplicate_type == "related"]
    print(f"  {len(dup_candidates)} candidate pairs: {len(exact_dups)} exact, {len(near_dups)} near-dup, {len(related)} related")

    # Save dedup results
    dup_out = []
    for d in dup_candidates:
        dup_out.append({
            "complaint_id_a": d.complaint_id_a,
            "complaint_id_b": d.complaint_id_b,
            "duplicate_type": d.duplicate_type,
            "confidence": d.confidence,
            "signals": d.signals,
            "distance_km": d.distance_km,
            "days_apart": d.days_apart,
            "keep_id": d.keep_id,
        })
    with open(PROCESSED_DIR / "dedup_candidates.json", "w", encoding="utf-8") as f:
        json.dump(dup_out, f, ensure_ascii=False, indent=2)
    print(f"  Saved dedup_candidates.json ({len(dup_out)} pairs)")

    # -------------------------------------------------------------------
    # Stage 3: Problem clustering
    # -------------------------------------------------------------------
    print("\n[3/7] Problem clustering…")
    from pipeline.cluster import ProblemClusterer
    clusterer = ProblemClusterer(complaints)
    clusters, unclustered_ids = clusterer.run()
    geo_cls = [c for c in clusters if c.cluster_method == "geo_dbscan"]
    ward_cls = [c for c in clusters if c.cluster_method == "ward_temporal"]
    print(f"  {len(clusters)} clusters ({len(geo_cls)} geo, {len(ward_cls)} ward-temporal)")
    print(f"  {len(unclustered_ids)} unclustered road complaints")

    # -------------------------------------------------------------------
    # Stage 4: Enrichment
    # -------------------------------------------------------------------
    print("\n[4/7] Evidence enrichment…")
    from pipeline.enrich import EvidenceEnricher
    enricher = EvidenceEnricher(work_orders, ward_metrics)
    evidence_map = {}
    for cl in clusters:
        ev = enricher.enrich(cl)
        evidence_map[cl.cluster_id] = ev
    print(f"  Enriched {len(evidence_map)} clusters")

    # -------------------------------------------------------------------
    # Stage 5 + 6: Case generation + prioritisation
    # -------------------------------------------------------------------
    print("\n[5/7] Case generation…")
    from pipeline.cases import CaseGenerator
    case_gen = CaseGenerator(complaints_by_id)

    print("[6/7] Prioritisation scoring…")
    from pipeline.prioritise import PriorityScorer
    scorer = PriorityScorer(complaints_by_id)

    cases = []
    for cl in clusters:
        ev = evidence_map[cl.cluster_id]
        priority = scorer.score(cl, ev)
        case = case_gen.generate(cl, ev, priority)
        cases.append(case)

    # Sort by priority score
    cases.sort(key=lambda c: -c.priority_score)

    high = [c for c in cases if c.priority_tier == "HIGH"]
    medium = [c for c in cases if c.priority_tier == "MEDIUM"]
    low = [c for c in cases if c.priority_tier == "LOW"]
    print(f"  {len(cases)} cases: {len(high)} HIGH, {len(medium)} MEDIUM, {len(low)} LOW")

    # -------------------------------------------------------------------
    # Stage 7: Save outputs
    # -------------------------------------------------------------------
    print("\n[7/7] Saving outputs…")

    def _serialise(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not serialisable")

    # Full cases JSON
    cases_out = []
    for c in cases:
        d = {
            "case_id": c.case_id,
            "cluster_id": c.cluster_id,
            "cluster_method": c.cluster_method,
            "problem_title": c.problem_title,
            "problem_summary": c.problem_summary,
            "problem_category": c.problem_category,
            "representative_subcategory": c.representative_subcategory,
            "complaint_count": c.complaint_count,
            "unique_ward_count": c.unique_ward_count,
            "date_first_complaint": c.date_first_complaint,
            "date_last_complaint": c.date_last_complaint,
            "years_active": c.years_active,
            "complaint_chronology": c.complaint_chronology,
            "primary_ward_name": c.primary_ward_name,
            "primary_ward_id": c.primary_ward_id,
            "all_ward_names": c.all_ward_names,
            "centroid_lat": c.centroid_lat,
            "centroid_lon": c.centroid_lon,
            "geographic_extent_km": c.geographic_extent_km,
            "open_count": c.open_count,
            "resolved_count": c.resolved_count,
            "reopened_count": c.reopened_count,
            "unresolved_rate_pct": c.unresolved_rate_pct,
            "evidence_items": c.evidence_items,
            "hypotheses": c.hypotheses,
            "responsible_agency": c.responsible_agency,
            "agency_confidence": c.agency_confidence,
            "agency_attribution_note": c.agency_attribution_note,
            "priority_tier": c.priority_tier,
            "priority_score": c.priority_score,
            "priority_factors": c.priority_factors,
            "priority_rationale": c.priority_rationale,
            "cluster_confidence": c.cluster_confidence,
            "clustering_reasons": c.clustering_reasons,
            "ward_join_confidence": c.ward_join_confidence,
            "ward_join_note": c.ward_join_note,
            "recommended_next_steps": c.recommended_next_steps,
            "complaint_ids": c.complaint_ids,
            "work_order_ids": c.work_order_ids,
            "work_orders_detail": c.work_orders_detail,
            "representative_complaints": c.representative_complaints,
            "generated_at": c.generated_at,
        }
        cases_out.append(d)

    with open(PROCESSED_DIR / "civic_cases.json", "w", encoding="utf-8") as f:
        json.dump(cases_out, f, ensure_ascii=False, indent=2, default=_serialise)
    print(f"  Saved civic_cases.json ({len(cases_out)} cases)")

    # Summary CSV
    import csv
    summary_path = PROCESSED_DIR / "civic_cases_summary.csv"
    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "case_id", "priority_tier", "priority_score", "problem_title",
            "complaint_count", "primary_ward_name", "years_active",
            "unresolved_rate_pct", "open_count", "reopened_count",
            "responsible_agency", "cluster_method", "cluster_confidence",
        ])
        writer.writeheader()
        for c in cases:
            writer.writerow({
                "case_id": c.case_id,
                "priority_tier": c.priority_tier,
                "priority_score": c.priority_score,
                "problem_title": c.problem_title,
                "complaint_count": c.complaint_count,
                "primary_ward_name": c.primary_ward_name,
                "years_active": str(c.years_active),
                "unresolved_rate_pct": c.unresolved_rate_pct,
                "open_count": c.open_count,
                "reopened_count": c.reopened_count,
                "responsible_agency": c.responsible_agency,
                "cluster_method": c.cluster_method,
                "cluster_confidence": c.cluster_confidence,
            })
    print(f"  Saved civic_cases_summary.csv")

    # -------------------------------------------------------------------
    # Print top 10 cases
    # -------------------------------------------------------------------
    t1 = datetime.utcnow()
    elapsed = (t1 - t0).total_seconds()
    print(f"\n{'='*60}")
    print(f"Pipeline complete in {elapsed:.1f}s")
    print(f"{'='*60}")
    print(f"\nTOP 10 CIVIC CASES (by priority score):\n")
    for i, c in enumerate(cases[:10], 1):
        print(f"{i:2d}. [{c.priority_tier}] {c.problem_title}")
        print(f"     Score={c.priority_score:.3f} | Complaints={c.complaint_count} | Unresolved={c.unresolved_rate_pct}%")
        print(f"     Agency={c.responsible_agency} | Years={c.years_active}")
        print()


if __name__ == "__main__":
    run()
