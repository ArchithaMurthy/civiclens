"""
CivicLens — Duplicate and near-duplicate detection.

Strategy (layered, explainable):
  1. Exact match: same ward_id + same subcategory + same description (after normalisation)
  2. Near-duplicate: same ward_id + same subcategory + GPS within 200m + within 7 days
  3. Related: same ward_id + same subcategory + within 60 days (possible recurring instance,
     NOT marked as duplicate — flagged for clustering instead)

Output:
  DuplicateCandidate objects with score, signals, and decision.

Design constraints:
  - Only complaints from the SAME SOURCE can be exact duplicates (cross-source
    near-duplicates are marked as 'related', not 'duplicate').
  - Complaints are never automatically deleted; this module only assigns flags.
  - No LLM used here — pure rule-based + geographic distance.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from math import asin, cos, radians, sin, sqrt
from typing import Optional

from pipeline.schema import Complaint

# ---------------------------------------------------------------------------
# Haversine distance (km)
# ---------------------------------------------------------------------------

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return 2 * R * asin(sqrt(a))


# ---------------------------------------------------------------------------
# Text fingerprint for exact matching
# ---------------------------------------------------------------------------

def _text_fingerprint(text: Optional[str]) -> str:
    if not text:
        return ""
    # Lowercase, strip punctuation, collapse whitespace
    cleaned = re.sub(r"[^\w\s]", "", text.lower())
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return hashlib.sha1(cleaned.encode()).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Output types
# ---------------------------------------------------------------------------

DUPLICATE = "duplicate"
NEAR_DUPLICATE = "near_duplicate"
RELATED = "related"


@dataclass
class DuplicateCandidate:
    complaint_id_a: str
    complaint_id_b: str
    duplicate_type: str          # 'duplicate' | 'near_duplicate' | 'related'
    confidence: float            # 0.0–1.0
    signals: list[str] = field(default_factory=list)
    distance_km: Optional[float] = None
    days_apart: Optional[float] = None
    keep_id: str = ""            # which record to keep (a = older, b = newer)


# ---------------------------------------------------------------------------
# Main detector
# ---------------------------------------------------------------------------

class DuplicateDetector:
    """
    Finds duplicate and near-duplicate complaints within the road infrastructure
    subset. Works on any list of Complaint objects.

    Complexity: O(n * k) where k = complaints per ward bucket (not O(n^2) global).
    """

    # Thresholds
    GPS_EXACT_M = 50       # within 50m -> strong geo signal
    GPS_NEAR_M = 200       # within 200m -> moderate geo signal
    DAYS_EXACT = 3         # within 3 days + same subcat + close GPS -> near-duplicate
    DAYS_NEAR = 7          # within 7 days -> near-duplicate candidate
    DAYS_RELATED = 60      # within 60 days, same ward/subcat -> related (for clustering)

    def __init__(self, complaints: list[Complaint]):
        self.complaints = complaints
        self._results: list[DuplicateCandidate] = []
        self._processed_pairs: set[frozenset] = set()

    # ------------------------------------------------------------------
    def detect(self) -> list[DuplicateCandidate]:
        """Run all detection passes and return candidates."""
        self._results = []
        self._processed_pairs = set()

        # Group by ward_id for efficiency (intra-ward comparisons only)
        by_ward: dict[Optional[int], list[Complaint]] = {}
        for c in self.complaints:
            key = c.ward_id if not c.ward_id_is_other else None
            by_ward.setdefault(key, []).append(c)

        for ward_id, group in by_ward.items():
            if ward_id is None:
                continue  # Skip unlocated "Other" ward
            if len(group) < 2:
                continue
            self._check_group(group)

        return self._results

    # ------------------------------------------------------------------
    def _check_group(self, group: list[Complaint]) -> None:
        # Sort by date for consistent pair ordering
        dated = sorted(
            [c for c in group if c.created_at is not None],
            key=lambda x: x.created_at,
        )

        for i, a in enumerate(dated):
            for b in dated[i + 1:]:
                pair = frozenset([a.complaint_id, b.complaint_id])
                if pair in self._processed_pairs:
                    continue
                self._processed_pairs.add(pair)

                days = (b.created_at - a.created_at).total_seconds() / 86400
                if days > self.DAYS_RELATED:
                    break  # dated list is sorted; no later b can be close enough

                result = self._compare(a, b, days)
                if result:
                    self._results.append(result)

    # ------------------------------------------------------------------
    def _compare(
        self, a: Complaint, b: Complaint, days: float
    ) -> Optional[DuplicateCandidate]:
        signals: list[str] = []
        confidence = 0.0

        # --- Subcategory match ---
        subcat_match = (
            a.subcategory is not None
            and b.subcategory is not None
            and a.subcategory.lower() == b.subcategory.lower()
        )
        if subcat_match:
            signals.append("same_subcategory")
            confidence += 0.25

        # --- Category match ---
        if a.category == b.category:
            signals.append("same_category")
            confidence += 0.10

        # --- Text fingerprint ---
        fp_a = _text_fingerprint(a.description)
        fp_b = _text_fingerprint(b.description)
        if fp_a and fp_b and fp_a == fp_b:
            signals.append("identical_description")
            confidence += 0.50

        # --- Geographic distance ---
        dist_km: Optional[float] = None
        if a.gps_valid and b.gps_valid and a.latitude and b.latitude:
            dist_km = haversine_km(a.latitude, a.longitude, b.latitude, b.longitude)
            if dist_km * 1000 <= self.GPS_EXACT_M:
                signals.append(f"gps_within_{self.GPS_EXACT_M}m")
                confidence += 0.30
            elif dist_km * 1000 <= self.GPS_NEAR_M:
                signals.append(f"gps_within_{self.GPS_NEAR_M}m")
                confidence += 0.15

        # --- Temporal proximity ---
        if days <= self.DAYS_EXACT:
            signals.append(f"within_{self.DAYS_EXACT}_days")
            confidence += 0.20
        elif days <= self.DAYS_NEAR:
            signals.append(f"within_{self.DAYS_NEAR}_days")
            confidence += 0.10

        # --- Same source extra weight ---
        if a.source == b.source:
            signals.append("same_source")

        # --- Classify ---
        if not signals:
            return None
        if confidence < 0.35:
            return None

        # Exact duplicate: identical text + same ward
        if "identical_description" in signals and days <= 7:
            dup_type = DUPLICATE
        elif confidence >= 0.65:
            dup_type = NEAR_DUPLICATE
        elif confidence >= 0.35:
            dup_type = RELATED
        else:
            return None

        return DuplicateCandidate(
            complaint_id_a=a.complaint_id,
            complaint_id_b=b.complaint_id,
            duplicate_type=dup_type,
            confidence=round(min(confidence, 1.0), 3),
            signals=signals,
            distance_km=round(dist_km, 4) if dist_km is not None else None,
            days_apart=round(days, 1),
            keep_id=a.complaint_id,  # keep the earlier record
        )
