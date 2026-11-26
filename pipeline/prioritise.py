"""
CivicLens — Prioritisation scoring.

Transparent, configurable scoring of clusters into priority tiers.

Scoring factors:
  1. complaint_volume       (weight: 0.30) — total complaints in cluster
  2. recurrence_years       (weight: 0.25) — number of distinct years with complaints
  3. unresolved_rate        (weight: 0.20) — fraction of complaints still open/reopened
  4. reopened_rate          (weight: 0.10) — fraction explicitly re-opened
  5. crash_risk             (weight: 0.05) — road crashes in ward (if available; sparse)
  6. description_severity   (weight: 0.10) — keyword signals in descriptions

Each factor is normalised to [0, 1] individually, then weighted.
Final score is in [0, 1]; tier assignment:
  HIGH   (>= 0.55)
  MEDIUM (>= 0.35)
  LOW    (< 0.35)

All weights are configurable via SCORING_WEIGHTS.

Calibration notes (Sprint 5-4):
  - MAX_COMPLAINTS lowered 100->30 (P75 of cluster sizes = 14, P90 = 29)
  - MAX_YEARS lowered 4->3 (data spans 4 years; 3+ years should nearly max out)
  - crash_risk weight 0.10->0.05 (only 20% of clusters have ward crash data)
  - complaint_volume weight 0.25->0.30 (redistributed from crash_risk)
  - Thresholds HIGH>=0.55, MED>=0.35 produce ~top-15% / mid-50% / bottom-35% split
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from pipeline.cluster import ProblemCluster
from pipeline.enrich import ClusterEvidence

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SCORING_WEIGHTS = {
    "complaint_volume": 0.30,    # raised from 0.25 — primary signal
    "recurrence_years": 0.25,
    "unresolved_rate": 0.20,
    "reopened_rate": 0.10,
    "crash_risk": 0.05,          # lowered from 0.10 — only 20% of cases have ward crash data
    "description_severity": 0.10,
}

# Normalisation ceilings (recalibrated to actual data distribution)
MAX_COMPLAINTS = 30    # P90 of cluster sizes approx 29; was 100 (too generous)
MAX_YEARS = 3          # 3 out of 4 data years should score near max; was 4
MAX_CRASHES = 100      # score saturates at 100 crashes/year

# Safety keywords in complaint descriptions
SEVERITY_KEYWORDS = [
    "accident", "fell", "injured", "hurt", "dangerous", "fatal",
    "killed", "death", "broken", "collapsed", "flood", "unsafe",
    "bike fell", "fell down", "vehicle fell",
]

PRIORITY_HIGH = "HIGH"
PRIORITY_MEDIUM = "MEDIUM"
PRIORITY_LOW = "LOW"

# Tier thresholds — recalibrated Sprint 5-4 to actual score distribution
# Produces ~top-15% HIGH / mid-50% MEDIUM / bottom-35% LOW
TIER_HIGH_THRESHOLD = 0.55
TIER_MEDIUM_THRESHOLD = 0.35


# ---------------------------------------------------------------------------
# Output type
# ---------------------------------------------------------------------------

@dataclass
class PriorityScore:
    cluster_id: str
    overall_score: float          # [0, 1]
    priority_tier: str            # 'HIGH' | 'MEDIUM' | 'LOW'
    priority_score: float = 0.0   # alias for overall_score (for case generation)

    factor_scores: dict[str, float] = field(default_factory=dict)
    factor_values: dict[str, float] = field(default_factory=dict)
    scoring_notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Scorer
# ---------------------------------------------------------------------------

class PriorityScorer:
    def __init__(
        self,
        complaints_by_id: dict[str, object],  # complaint_id -> Complaint
        weights: dict[str, float] = None,
    ):
        self._complaints = complaints_by_id
        self._weights = weights or SCORING_WEIGHTS

    # ------------------------------------------------------------------
    def score(
        self, cluster: ProblemCluster, evidence: ClusterEvidence
    ) -> PriorityScore:
        factors: dict[str, float] = {}
        values: dict[str, float] = {}
        notes: list[str] = []

        # 1. Complaint volume
        v_vol = min(cluster.complaint_count / MAX_COMPLAINTS, 1.0)
        factors["complaint_volume"] = v_vol
        values["complaint_volume"] = cluster.complaint_count
        notes.append(f"Volume: {cluster.complaint_count} complaints (norm={v_vol:.2f})")

        # 2. Recurrence years
        v_rec = min(len(cluster.years_active) / MAX_YEARS, 1.0)
        factors["recurrence_years"] = v_rec
        values["recurrence_years"] = len(cluster.years_active)
        notes.append(f"Recurrence: {cluster.years_active} → {len(cluster.years_active)} years (norm={v_rec:.2f})")

        # 3. Unresolved rate
        v_unres = cluster.unresolved_rate
        factors["unresolved_rate"] = v_unres
        values["unresolved_rate"] = round(cluster.unresolved_rate * 100, 1)
        notes.append(f"Unresolved: {round(cluster.unresolved_rate*100)}% (norm={v_unres:.2f})")

        # 4. Re-opened rate
        total = cluster.complaint_count
        v_reopen = min(cluster.reopened_count / max(total, 1), 1.0)
        factors["reopened_rate"] = v_reopen
        values["reopened_rate"] = cluster.reopened_count
        notes.append(f"Re-opened: {cluster.reopened_count} complaints (norm={v_reopen:.2f})")

        # 5. Crash risk (road crashes in ward from KAUN 2024 data)
        crashes = evidence.ward_road_crashes_2024 or 0
        v_crash = min(crashes / MAX_CRASHES, 1.0)
        factors["crash_risk"] = v_crash
        values["crash_risk"] = crashes
        notes.append(f"Road crashes in ward (2024): {crashes} (norm={v_crash:.2f})")

        # 6. Description severity keywords
        member_ids = cluster.representative_complaint_ids
        kw_hits = 0
        for cid in member_ids:
            c = self._complaints.get(cid)
            if c and c.description:
                desc_lower = c.description.lower()
                kw_hits += sum(1 for kw in SEVERITY_KEYWORDS if kw in desc_lower)
        v_sev = min(kw_hits / (len(member_ids) * 2 + 1), 1.0)  # normalise loosely
        factors["description_severity"] = v_sev
        values["description_severity"] = kw_hits
        if kw_hits > 0:
            notes.append(f"Severity keywords in sample: {kw_hits} hits (norm={v_sev:.2f})")

        # Weighted sum
        overall = sum(
            self._weights.get(k, 0) * v for k, v in factors.items()
        )
        overall = round(min(overall, 1.0), 4)

        tier = PRIORITY_HIGH if overall >= TIER_HIGH_THRESHOLD else (PRIORITY_MEDIUM if overall >= TIER_MEDIUM_THRESHOLD else PRIORITY_LOW)

        return PriorityScore(
            cluster_id=cluster.cluster_id,
            overall_score=overall,
            priority_score=overall,
            priority_tier=tier,
            factor_scores={k: round(v, 4) for k, v in factors.items()},
            factor_values=values,
            scoring_notes=notes,
        )
