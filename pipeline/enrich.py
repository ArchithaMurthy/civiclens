"""
CivicLens — Evidence enrichment.

For each cluster, attach available evidence from:
  1. KAUN ward metrics (pothole count 2022, spending, road crashes)
  2. KAUN work orders (road/drain works in matching ward, FY 2023-26)
  3. Ward crosswalk (join quality indicator)

IMPORTANT constraints:
  - Ward join: ICMC ward numbering (1-199) is NOT the same as bbmp225 numbering.
    The correct join is via ward NAME matching: ICMC ward_name -> bbmp225_name_en
    -> datameet243_no. The pre-computed lookup in ward_name_to_datameet243.json
    (built in Sprint 3) is used. For 15 ward names with no match, the join
    falls back to 'unknown' and no enrichment is applied.
  - Work orders: we can say "work orders exist in this ward for road work".
    We CANNOT say a specific work order fixed or caused a specific complaint.
  - Contractor data: we include contractor names for context only.
    We do NOT infer misconduct from deduction percentages or blacklist flags.
  - All inferences are explicitly labelled as 'hypothesis', not 'fact'.
"""
from __future__ import annotations

import csv
import difflib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from pipeline.cluster import ProblemCluster
from pipeline.schema import WardMetrics, WorkOrder

RAW_DIR = Path("data/raw")
PROC_DIR = Path("data/processed")


# ---------------------------------------------------------------------------
# Ward crosswalk loader — name-based (correct approach)
# ---------------------------------------------------------------------------

def _load_name_crosswalk() -> dict[str, dict]:
    """
    Returns {icmc_ward_name: {datameet243_no, overlap_confidence, match_method, ...}}

    Uses the pre-computed lookup built in Sprint 3 scripts/run_sprint3_audit.py.
    If the file doesn't exist, builds it on the fly from the raw crosswalk CSV.
    """
    lookup_path = PROC_DIR / "ward_name_to_datameet243.json"
    if lookup_path.exists():
        with open(lookup_path, encoding="utf-8") as f:
            return json.load(f)

    # Build on the fly if lookup not cached
    cw_path = RAW_DIR / "kaun_ward_crosswalk.csv"
    cw_rows = []
    with open(cw_path, encoding="utf-8") as f:
        cw_rows = list(csv.DictReader(f))
    cw_names = [r["bbmp225_name_en"].strip() for r in cw_rows]
    cw_by_name = {r["bbmp225_name_en"].strip(): r for r in cw_rows}

    lookup: dict[str, dict] = {}
    for row in cw_rows:
        name = row["bbmp225_name_en"].strip()
        try:
            dm_no = int(row["datameet243_no"]) if row.get("datameet243_no") else None
            bbmp_no = int(row["bbmp225_no"]) if row.get("bbmp225_no") else None
            oc = float(row["overlap_confidence"]) if row.get("overlap_confidence") else None
        except ValueError:
            continue
        lookup[name] = {
            "datameet243_no": dm_no,
            "bbmp225_no": bbmp_no,
            "overlap_confidence": oc,
            "match_method": "exact_name",
        }
    return lookup


# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

@dataclass
class ClusterEvidence:
    cluster_id: str

    # Ward metrics evidence (direct join)
    ward_metrics: Optional[WardMetrics] = None
    ward_join_confidence: str = "none"   # 'direct' | 'crosswalk' | 'approximate' | 'none'
    ward_join_note: str = ""

    # Work orders (road/drain in same ward)
    road_work_orders: list[WorkOrder] = field(default_factory=list)
    road_work_order_count: int = 0
    road_work_order_total_sanctioned: Optional[float] = None  # INR
    road_work_order_fys: list[str] = field(default_factory=list)

    # Computed enrichment fields
    ward_pothole_count_2022: Optional[int] = None
    ward_road_spending_inr: Optional[float] = None
    ward_road_crashes_2024: Optional[int] = None
    ward_fatal_crashes_2024: Optional[int] = None

    # Contextual notes (hypotheses clearly labelled)
    context_notes: list[str] = field(default_factory=list)
    hypotheses: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Enricher
# ---------------------------------------------------------------------------

class EvidenceEnricher:
    def __init__(
        self,
        work_orders: list[WorkOrder],
        ward_metrics: list[WardMetrics],
    ):
        self._name_crosswalk = _load_name_crosswalk()

        # Index work orders by datameet243_no
        self._wo_by_ward: dict[int, list[WorkOrder]] = {}
        for wo in work_orders:
            wid = wo.datameet243_no
            if wid is not None:
                self._wo_by_ward.setdefault(wid, []).append(wo)

        # Index ward metrics by ward_no (datameet243 numbering)
        self._metrics_by_ward: dict[int, WardMetrics] = {
            m.ward_no: m for m in ward_metrics
        }

    def enrich(self, cluster: ProblemCluster) -> ClusterEvidence:
        ev = ClusterEvidence(cluster_id=cluster.cluster_id)

        # --- Ward mapping (name-based, correct approach) ---
        # ICMC ward_id numbering != bbmp225_no != datameet243_no.
        # Correct chain: ICMC ward_name -> bbmp225_name_en (name match) -> datameet243_no.
        # Pre-computed lookup: data/processed/ward_name_to_datameet243.json
        ward_name = cluster.primary_ward_name
        datameet_id: Optional[int] = None
        join_confidence = "none"
        join_note = "No ward name available on cluster."

        if ward_name:
            if ward_name in self._name_crosswalk:
                entry = self._name_crosswalk[ward_name]
                datameet_id = entry.get("datameet243_no")
                oc = entry.get("overlap_confidence")
                method = entry.get("match_method", "unknown")
                join_confidence = "exact_name" if method == "exact_name" else "fuzzy_name"
                join_note = (
                    f"ICMC ward_name='{ward_name}' matched to datameet243={datameet_id} "
                    f"via {method} (overlap_confidence={oc})."
                )
            else:
                join_note = (
                    f"ICMC ward_name='{ward_name}' not found in name crosswalk "
                    f"(one of the 15 unmatched wards). No enrichment applied."
                )

        ev.ward_join_confidence = join_confidence
        ev.ward_join_note = join_note

        if datameet_id is None:
            return ev

        # --- Ward metrics ---
        metrics = self._metrics_by_ward.get(datameet_id)
        if metrics:
            ev.ward_metrics = metrics
            ev.ward_pothole_count_2022 = metrics.pothole_complaints
            ev.ward_road_spending_inr = metrics.spend_roads_and_infrastructure
            ev.ward_road_crashes_2024 = metrics.road_crashes_2024
            ev.ward_fatal_crashes_2024 = metrics.fatal_crashes_2024

        # --- Work orders ---
        wos = self._wo_by_ward.get(datameet_id, [])
        road_wos = [w for w in wos if w.work_category in ("road", "drain")]
        ev.road_work_orders = road_wos
        ev.road_work_order_count = len(road_wos)
        if road_wos:
            totals = [w.sanctioned_amount for w in road_wos if w.sanctioned_amount]
            ev.road_work_order_total_sanctioned = sum(totals) if totals else None
            ev.road_work_order_fys = sorted({w.fy for w in road_wos if w.fy})

        # --- Contextual notes (factual, not inferential) ---
        if ev.ward_pothole_count_2022:
            ev.context_notes.append(
                f"Ward had {ev.ward_pothole_count_2022} pothole complaints logged in KAUN 2022 data."
            )
        if ev.ward_road_spending_inr:
            cr = ev.ward_road_spending_inr / 1e7
            period = metrics.spend_period if metrics else "unknown period"
            ev.context_notes.append(
                f"Ward road/infrastructure spend: ₹{cr:.1f} crore ({period})."
            )
        if ev.road_work_order_count > 0:
            total_cr = (ev.road_work_order_total_sanctioned or 0) / 1e7
            fys = ", ".join(ev.road_work_order_fys)
            ev.context_notes.append(
                f"{ev.road_work_order_count} road/drain work order(s) in ward "
                f"(sanctioned ₹{total_cr:.1f} crore, FY {fys})."
            )
        if ev.ward_road_crashes_2024:
            ev.context_notes.append(
                f"Ward recorded {ev.ward_road_crashes_2024} road crashes in 2024 "
                f"({ev.ward_fatal_crashes_2024 or 0} fatal)."
            )

        # --- Hypotheses (explicitly labelled as unverified) ---
        if cluster.unresolved_rate >= 0.50 and ev.road_work_order_count > 0:
            ev.hypotheses.append(
                "HYPOTHESIS (unverified): Road work contracts exist in this ward, yet "
                f"{round(cluster.unresolved_rate*100)}% of complaints remain unresolved. "
                "This may indicate that repairs were incomplete, inadequate, or that the "
                "work was performed in different road segments. Independent verification required."
            )
        if cluster.reopened_count > 0:
            ev.hypotheses.append(
                f"HYPOTHESIS (unverified): {cluster.reopened_count} complaint(s) were "
                "re-opened after being marked resolved. This may indicate short-term or "
                "superficial repairs that did not address the underlying problem."
            )

        return ev
