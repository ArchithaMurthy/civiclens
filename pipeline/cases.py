"""
CivicLens — Civic intelligence case generation.

For each cluster + evidence + priority score, produces a structured CivicCase.

Every factual claim is traceable to a source record.
Hypotheses are explicitly labelled.
The LLM is NOT used in this module — all case content is derived from data.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from pipeline.cluster import ProblemCluster
from pipeline.enrich import ClusterEvidence
from pipeline.prioritise import PriorityScore
from pipeline.schema import Complaint


# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

@dataclass
class CivicCase:
    case_id: str
    cluster_id: str
    cluster_method: str

    # Headline
    problem_title: str
    problem_summary: str
    problem_category: str
    representative_subcategory: str

    # Volume
    complaint_count: int
    unique_ward_count: int

    # Temporal
    date_first_complaint: Optional[str]   # ISO date string
    date_last_complaint: Optional[str]
    years_active: list[int]
    complaint_chronology: list[dict]      # [{year, count}]

    # Geographic
    primary_ward_name: Optional[str]
    primary_ward_id: Optional[int]
    all_ward_names: list[str]
    centroid_lat: Optional[float]
    centroid_lon: Optional[float]
    geographic_extent_km: Optional[float]

    # Status
    open_count: int
    resolved_count: int
    reopened_count: int
    unresolved_rate_pct: float

    # Evidence
    evidence_items: list[dict]            # [{type, description, source, traceable_to}]
    hypotheses: list[str]

    # Agency
    responsible_agency: Optional[str]
    agency_confidence: str                # 'direct' | 'inferred' | 'unknown'
    agency_attribution_note: str

    # Priority
    priority_tier: str
    priority_score: float
    priority_factors: dict[str, float]
    priority_rationale: str

    # Cluster quality
    cluster_confidence: float
    clustering_reasons: list[str]
    ward_join_confidence: str   # 'exact_name' | 'fuzzy_name' | 'none'
    ward_join_note: str

    # Recommended next steps
    recommended_next_steps: list[str]

    # All complaint IDs contributing to this case (Gap G1 fix)
    complaint_ids: list[str]

    # Work order IDs for the ward matching this case (Sprint 5-5)
    work_order_ids: list[str]
    work_orders_detail: list[dict]  # compact work order records for UI display

    # Representative complaints (for review)
    representative_complaints: list[dict]

    # Metadata
    generated_at: str


# ---------------------------------------------------------------------------
# Case generator
# ---------------------------------------------------------------------------

class CaseGenerator:
    def __init__(self, complaints_by_id: dict[str, Complaint]):
        self._c = complaints_by_id

    def generate(
        self,
        cluster: ProblemCluster,
        evidence: ClusterEvidence,
        priority: PriorityScore,
    ) -> CivicCase:
        case_id = f"CASE-{cluster.cluster_id}"

        # --- Title and summary ---
        ward_label = cluster.primary_ward_name or (
            ", ".join(cluster.ward_names[:2]) if cluster.ward_names else "unknown ward"
        )
        subcat = cluster.representative_subcategory
        years_str = f"{min(cluster.years_active)}–{max(cluster.years_active)}"

        problem_title = (
            f"Recurring {subcat} — {ward_label} ({years_str})"
        )

        # Build a data-only summary (no fabricated content)
        open_pct = round(cluster.unresolved_rate * 100)
        problem_summary = (
            f"{cluster.complaint_count} citizen complaints about '{subcat}' "
            f"were recorded in {ward_label} between "
            f"{cluster.date_first.strftime('%B %Y') if cluster.date_first else 'unknown'} "
            f"and {cluster.date_last.strftime('%B %Y') if cluster.date_last else 'unknown'}, "
            f"spanning {len(cluster.years_active)} calendar year(s). "
            f"{open_pct}% of these complaints remain unresolved (status: Open or Re-opened). "
        )
        if cluster.reopened_count > 0:
            problem_summary += (
                f"{cluster.reopened_count} complaint(s) were re-opened after initially being resolved. "
            )

        # --- Complaint chronology ---
        from collections import Counter
        year_counts = Counter()
        for cid in cluster.complaint_ids:
            c = self._c.get(cid)
            if c and c.created_at:
                year_counts[c.created_at.year] += 1
        complaint_chronology = [
            {"year": y, "count": year_counts[y]}
            for y in sorted(year_counts.keys())
        ]

        # --- Evidence items ---
        evidence_items: list[dict] = []

        evidence_items.append({
            "type": "complaint_volume",
            "description": f"{cluster.complaint_count} complaints recorded in source dataset.",
            "source": "I Change My City (ichangemycity.com) via OpenCity",
            "traceable_to": "data/raw/ichangemycity_complaints.csv",
        })
        evidence_items.append({
            "type": "complaint_status",
            "description": (
                f"Status distribution: Open={cluster.open_count}, "
                f"Resolved={cluster.resolved_count}, "
                f"Re-opened={cluster.reopened_count}."
            ),
            "source": "I Change My City",
            "traceable_to": "data/raw/ichangemycity_complaints.csv (complaint_status_title field)",
        })
        if evidence.ward_pothole_count_2022:
            evidence_items.append({
                "type": "ward_pothole_data",
                "description": f"KAUN 2022 data: ward recorded {evidence.ward_pothole_count_2022} pothole complaints.",
                "source": "KAUN Bengaluru (bengaluru.kaun.city)",
                "traceable_to": "data/raw/kaun_ward_metrics.csv (pothole_complaints field, pothole_data_year=2022)",
            })
        if evidence.ward_road_spending_inr:
            cr = evidence.ward_road_spending_inr / 1e7
            period = evidence.ward_metrics.spend_period if evidence.ward_metrics else "unknown"
            evidence_items.append({
                "type": "ward_road_spending",
                "description": f"Ward road/infrastructure spending: ₹{cr:.1f} crore ({period}).",
                "source": "KAUN Bengaluru",
                "traceable_to": "data/raw/kaun_ward_metrics.csv (spend_roads_and_infrastructure field)",
            })
        if evidence.road_work_order_count > 0:
            total_cr = (evidence.road_work_order_total_sanctioned or 0) / 1e7
            fys = ", ".join(evidence.road_work_order_fys)
            evidence_items.append({
                "type": "work_orders_in_ward",
                "description": (
                    f"{evidence.road_work_order_count} road/drain work order(s) sanctioned in ward "
                    f"(₹{total_cr:.1f} crore, FY {fys}). Note: work order ward mapping uses "
                    f"datameet243 numbering ({evidence.ward_join_confidence} join)."
                ),
                "source": "KAUN Bengaluru (via BBMP/opencity.in)",
                "traceable_to": "data/raw/kaun_work_orders_all_wards.json",
            })
        if evidence.ward_road_crashes_2024:
            evidence_items.append({
                "type": "road_crash_data",
                "description": (
                    f"Ward recorded {evidence.ward_road_crashes_2024} road crashes in 2024, "
                    f"of which {evidence.ward_fatal_crashes_2024 or 0} were fatal."
                ),
                "source": "KAUN Bengaluru",
                "traceable_to": "data/raw/kaun_ward_metrics.csv (road_crashes_2024, fatal_crashes_2024 fields)",
            })

        # --- Agency attribution ---
        # Use the actual civic_agency field from complaints — BBMP is by far dominant
        agency_counts = {}
        for cid in cluster.complaint_ids:
            c = self._c.get(cid)
            if c and c.civic_agency:
                agency_counts[c.civic_agency] = agency_counts.get(c.civic_agency, 0) + 1
        resp_agency = max(agency_counts, key=agency_counts.get) if agency_counts else None
        if resp_agency and agency_counts.get(resp_agency, 0) / cluster.complaint_count >= 0.80:
            agency_conf = "direct"
            agency_note = (
                f"{agency_counts[resp_agency]} of {cluster.complaint_count} complaints "
                f"explicitly name {resp_agency} as the responsible agency in the source data."
            )
        elif resp_agency:
            agency_conf = "inferred"
            agency_note = (
                f"{resp_agency} appears as agency in {agency_counts.get(resp_agency,0)} complaints "
                f"(majority, but not ≥80%)."
            )
        else:
            agency_conf = "unknown"
            agency_note = "No agency information in source records for this cluster."
            resp_agency = None

        # --- Recommended next steps ---
        steps: list[str] = [
            f"File an RTI (Right to Information) request to BBMP requesting the road repair history "
            f"for {ward_label} for the period {years_str}.",
        ]
        if evidence.road_work_order_count > 0:
            steps.append(
                f"Request inspection records for the {evidence.road_work_order_count} work order(s) "
                f"sanctioned in this ward to verify whether road works covered the affected stretch."
            )
        steps.append(
            "Re-survey affected stretch using a civic volunteer or journalist to document current road condition."
        )
        if cluster.reopened_count > 0:
            steps.append(
                f"Investigate the {cluster.reopened_count} re-opened complaint(s) to determine whether "
                "patchwork repairs were applied and failed."
            )
        if evidence.ward_road_crashes_2024 and evidence.ward_road_crashes_2024 > 20:
            steps.append(
                "Cross-reference crash location data with cluster centroid to assess whether road condition "
                "may be a contributing factor to road accidents."
            )

        # --- Priority rationale ---
        top_factors = sorted(
            priority.factor_scores.items(), key=lambda x: -x[1]
        )[:3]
        priority_rationale = (
            f"Priority tier {priority.priority_tier} (score={priority.priority_score:.2f}). "
            f"Top scoring factors: "
            + ", ".join(f"{k}={v:.2f}" for k, v in top_factors)
            + "."
        )

        # --- Work order IDs and details ---
        wo_ids = [wo.work_order_id for wo in evidence.road_work_orders]
        wo_detail = []
        for wo in evidence.road_work_orders:
            cr = (wo.sanctioned_amount / 1e7) if wo.sanctioned_amount else None
            wo_detail.append({
                "work_order_id": wo.work_order_id,
                "fy": wo.fy,
                "description": (wo.description or "")[:200],
                "contractor_name": wo.contractor_name,
                "sanctioned_crore": round(cr, 2) if cr is not None else None,
                "work_category": wo.work_category,
            })

        # --- Representative complaints ---
        rep_complaints = []
        for cid in cluster.representative_complaint_ids:
            c = self._c.get(cid)
            if c:
                rep_complaints.append({
                    "complaint_id": c.complaint_id,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                    "ward_name": c.ward_name,
                    "subcategory": c.subcategory,
                    "status": c.status,
                    "description_excerpt": (c.description or "")[:300],
                    "latitude": c.latitude,
                    "longitude": c.longitude,
                })

        return CivicCase(
            case_id=case_id,
            cluster_id=cluster.cluster_id,
            cluster_method=cluster.cluster_method,
            problem_title=problem_title,
            problem_summary=problem_summary,
            problem_category=cluster.category,
            representative_subcategory=subcat,
            complaint_count=cluster.complaint_count,
            unique_ward_count=len(set(cluster.ward_ids)),
            date_first_complaint=cluster.date_first.date().isoformat() if cluster.date_first else None,
            date_last_complaint=cluster.date_last.date().isoformat() if cluster.date_last else None,
            years_active=cluster.years_active,
            complaint_chronology=complaint_chronology,
            primary_ward_name=cluster.primary_ward_name,
            primary_ward_id=cluster.primary_ward_id,
            all_ward_names=cluster.ward_names,
            centroid_lat=cluster.centroid_lat,
            centroid_lon=cluster.centroid_lon,
            geographic_extent_km=cluster.bounding_box_km,
            open_count=cluster.open_count,
            resolved_count=cluster.resolved_count,
            reopened_count=cluster.reopened_count,
            unresolved_rate_pct=round(cluster.unresolved_rate * 100, 1),
            evidence_items=evidence_items,
            hypotheses=evidence.hypotheses,
            responsible_agency=resp_agency,
            agency_confidence=agency_conf,
            agency_attribution_note=agency_note,
            priority_tier=priority.priority_tier,
            priority_score=priority.priority_score,
            priority_factors=priority.factor_scores,
            priority_rationale=priority_rationale,
            cluster_confidence=cluster.confidence,
            clustering_reasons=cluster.clustering_reasons,
            ward_join_confidence=evidence.ward_join_confidence,
            ward_join_note=evidence.ward_join_note,
            recommended_next_steps=steps,
            complaint_ids=cluster.complaint_ids,
            work_order_ids=wo_ids,
            work_orders_detail=wo_detail,
            representative_complaints=rep_complaints,
            generated_at=datetime.utcnow().isoformat(),
        )
