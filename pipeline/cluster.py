"""
CivicLens — Problem clustering.

Groups road infrastructure complaints into recurring civic problem clusters.

Strategy:
  - Two-pass clustering:
    1. GEOGRAPHIC: DBSCAN on GPS coordinates (eps ~ 300m) to find spatial clusters.
       Only run on complaints with valid GPS.
    2. WARD: For complaints without GPS or in sparse areas, group by ward_id +
       subcategory. Only if the ward group has >= 3 complaints across >= 2 years.

  Cluster acceptance criteria:
    - Minimum 5 complaints.
    - Complaints span at least 2 different years (recurrence signal).
    - Geographic diameter <= 1.5 km (coherent location).

  Unclustered complaints are retained with cluster_id = None.

  No LLM used. Clustering is purely spatial + temporal.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from math import radians
from typing import Optional
import re

import numpy as np
from sklearn.cluster import DBSCAN

from pipeline.schema import Complaint

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EARTH_RADIUS_KM = 6371.0
GPS_EPS_KM = 0.30          # 300m cluster radius
MIN_SAMPLES = 5             # min complaints to form a geo cluster
MIN_YEARS = 2               # cluster must span >= 2 distinct years
MAX_DIAMETER_KM = 2.0       # cluster must be spatially coherent
WARD_MIN_COMPLAINTS = 5     # ward-level group min size
WARD_MIN_YEARS = 2          # ward group must span >= 2 years

# Subcategories to include in road focus set
ROAD_FOCUS_SUBCATS = {
    "fixing/reparing potholes",
    "fixing/repairing potholes",
    "tarring or asphalting of existing road",
    "tarring or asphalting of mud/kutcha/unpaved road",
    "flooding/waterlogging of roads and footpaths",
    "construction of roadside drains",
    "desilting existing roadside drains",
    "removal of roadside debris (construction material)",
    "repair of bridge and culverts",
    "repair of existing footpaths",
    "construction of roadside drains",
}


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class ProblemCluster:
    cluster_id: str
    cluster_method: str              # 'geo_dbscan' | 'ward_temporal'
    category: str
    representative_subcategory: str  # most common subcategory

    complaint_ids: list[str] = field(default_factory=list)
    complaint_count: int = 0

    # Temporal
    date_first: Optional[datetime] = None
    date_last: Optional[datetime] = None
    years_active: list[int] = field(default_factory=list)

    # Geographic
    centroid_lat: Optional[float] = None
    centroid_lon: Optional[float] = None
    bounding_box_km: Optional[float] = None  # diagonal of bbox
    ward_ids: list[int] = field(default_factory=list)
    ward_names: list[str] = field(default_factory=list)
    primary_ward_id: Optional[int] = None
    primary_ward_name: Optional[str] = None

    # Quality
    confidence: float = 0.0
    clustering_reasons: list[str] = field(default_factory=list)

    # Status summary
    open_count: int = 0
    resolved_count: int = 0
    reopened_count: int = 0
    unresolved_rate: float = 0.0

    # Representative complaints (for display)
    representative_complaint_ids: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Helper: get year from datetime
# ---------------------------------------------------------------------------

def _year(c: Complaint) -> Optional[int]:
    return c.created_at.year if c.created_at else None


# ---------------------------------------------------------------------------
# Clusterer
# ---------------------------------------------------------------------------

class ProblemClusterer:
    def __init__(self, complaints: list[Complaint]):
        # Keep only road focus set
        self.road_complaints = [
            c for c in complaints
            if c.category == "road_infrastructure"
            and not c.ward_id_is_other
            and c.source == "ichangemycity"  # GPS-sourced only for now
        ]
        self.clusters: list[ProblemCluster] = []
        self.unclustered_ids: set[str] = set()

    def run(self) -> tuple[list[ProblemCluster], list[str]]:
        """Return (clusters, unclustered_complaint_ids)."""
        assigned: set[str] = set()

        # Pass 1: geo DBSCAN on GPS complaints
        gps_complaints = [c for c in self.road_complaints if c.gps_valid and c.latitude]
        geo_clusters = self._geo_cluster(gps_complaints)
        for cl in geo_clusters:
            self.clusters.append(cl)
            assigned.update(cl.complaint_ids)

        # Pass 2: ward temporal clustering for remaining
        remaining = [c for c in self.road_complaints if c.complaint_id not in assigned]
        ward_clusters = self._ward_cluster(remaining)
        for cl in ward_clusters:
            self.clusters.append(cl)
            assigned.update(cl.complaint_ids)

        # Unclustered
        all_ids = {c.complaint_id for c in self.road_complaints}
        self.unclustered_ids = all_ids - assigned

        return self.clusters, list(self.unclustered_ids)

    # ------------------------------------------------------------------
    def _geo_cluster(self, complaints: list[Complaint]) -> list[ProblemCluster]:
        if not complaints:
            return []

        coords = np.array([[radians(c.latitude), radians(c.longitude)] for c in complaints])
        eps_rad = GPS_EPS_KM / EARTH_RADIUS_KM

        db = DBSCAN(eps=eps_rad, min_samples=MIN_SAMPLES, algorithm="ball_tree", metric="haversine")
        labels = db.fit_predict(coords)

        clusters: list[ProblemCluster] = []
        unique_labels = set(labels)
        unique_labels.discard(-1)

        for label in sorted(unique_labels):
            idxs = [i for i, l in enumerate(labels) if l == label]
            members = [complaints[i] for i in idxs]

            # Apply acceptance criteria
            years = sorted({_year(c) for c in members if _year(c)})
            if len(years) < MIN_YEARS:
                continue  # Must span >= 2 years

            cl = self._build_cluster(
                cluster_id=f"GEO-{label:04d}",
                method="geo_dbscan",
                members=members,
                years=years,
            )
            if cl:
                clusters.append(cl)

        return clusters

    # ------------------------------------------------------------------
    def _ward_cluster(self, complaints: list[Complaint]) -> list[ProblemCluster]:
        """Group by ward_id + normalised_subcategory."""
        from collections import defaultdict

        groups: dict[tuple, list[Complaint]] = defaultdict(list)
        for c in complaints:
            if c.ward_id is None:
                continue
            sub = (c.subcategory or "").strip().lower()
            # Only group within focus subcategories
            if sub not in ROAD_FOCUS_SUBCATS:
                sub = "road_general"
            groups[(c.ward_id, sub)].append(c)

        clusters: list[ProblemCluster] = []
        for (ward_id, sub), members in groups.items():
            if len(members) < WARD_MIN_COMPLAINTS:
                continue
            years = sorted({_year(c) for c in members if _year(c)})
            if len(years) < WARD_MIN_YEARS:
                continue

            cl_id = f"WARD-{ward_id:03d}-{sub[:8].replace('/', '').replace(' ','_').upper()}"
            cl = self._build_cluster(
                cluster_id=cl_id,
                method="ward_temporal",
                members=members,
                years=years,
            )
            if cl:
                clusters.append(cl)

        return clusters

    # ------------------------------------------------------------------
    def _build_cluster(
        self,
        cluster_id: str,
        method: str,
        members: list[Complaint],
        years: list[int],
    ) -> Optional[ProblemCluster]:
        # Dominant subcategory
        from collections import Counter
        sub_counter = Counter(c.subcategory for c in members if c.subcategory)
        rep_subcat = sub_counter.most_common(1)[0][0] if sub_counter else "unknown"

        # Temporal range
        dated = [c for c in members if c.created_at]
        date_first = min(c.created_at for c in dated) if dated else None
        date_last = max(c.created_at for c in dated) if dated else None

        # Geographic centroid
        gps_members = [c for c in members if c.gps_valid and c.latitude]
        centroid_lat = centroid_lon = None
        bbox_km = None
        if gps_members:
            lats = [c.latitude for c in gps_members]
            lons = [c.longitude for c in gps_members]
            centroid_lat = sum(lats) / len(lats)
            centroid_lon = sum(lons) / len(lons)
            # Bounding box diagonal
            from pipeline.dedup import haversine_km
            bbox_km = haversine_km(min(lats), min(lons), max(lats), max(lons))
            if method == "geo_dbscan" and bbox_km > MAX_DIAMETER_KM:
                return None  # Too spread out for geo cluster

        # Ward info
        from collections import Counter as C2
        ward_counter = C2(
            (c.ward_id, c.ward_name) for c in members if c.ward_id and not c.ward_id_is_other
        )
        ward_ids = [wid for (wid, _), _ in ward_counter.most_common()]
        ward_names = [wn for (_, wn), _ in ward_counter.most_common()]
        primary = ward_counter.most_common(1)
        primary_ward_id = primary[0][0][0] if primary else None
        primary_ward_name = primary[0][0][1] if primary else None

        # Status
        open_c = sum(1 for c in members if c.status in ("open", "reopened"))
        resolved_c = sum(1 for c in members if c.status == "resolved")
        reopened_c = sum(1 for c in members if c.status == "reopened")
        total = len(members)
        unresolved_rate = open_c / total if total else 0.0

        # Confidence score
        confidence = 0.0
        reasons = []
        if len(years) >= 3:
            confidence += 0.40
            reasons.append(f"complaints_in_{len(years)}_distinct_years")
        elif len(years) == 2:
            confidence += 0.25
            reasons.append("complaints_in_2_distinct_years")
        if total >= 20:
            confidence += 0.20
            reasons.append(f"{total}_complaints_in_cluster")
        elif total >= 10:
            confidence += 0.15
            reasons.append(f"{total}_complaints_in_cluster")
        elif total >= 5:
            confidence += 0.10
        if gps_members and method == "geo_dbscan":
            confidence += 0.20
            reasons.append("gps_coherent_cluster")
        if unresolved_rate >= 0.40:
            confidence += 0.10
            reasons.append(f"{round(unresolved_rate*100)}pct_unresolved")
        if reopened_c > 0:
            confidence += 0.05
            reasons.append(f"{reopened_c}_reopened_complaints")
        confidence = min(confidence, 1.0)

        # Representative complaints: highest comment count or most recent
        sorted_members = sorted(members, key=lambda c: (-(c.comment_count or 0), c.created_at or datetime.min))
        rep_ids = [c.complaint_id for c in sorted_members[:5]]

        return ProblemCluster(
            cluster_id=cluster_id,
            cluster_method=method,
            category="road_infrastructure",
            representative_subcategory=rep_subcat,
            complaint_ids=[c.complaint_id for c in members],
            complaint_count=total,
            date_first=date_first,
            date_last=date_last,
            years_active=years,
            centroid_lat=centroid_lat,
            centroid_lon=centroid_lon,
            bounding_box_km=round(bbox_km, 3) if bbox_km is not None else None,
            ward_ids=list(dict.fromkeys(ward_ids)),        # deduplicated, order preserved
            ward_names=list(dict.fromkeys(ward_names)),
            primary_ward_id=primary_ward_id,
            primary_ward_name=primary_ward_name,
            confidence=round(confidence, 3),
            clustering_reasons=reasons,
            open_count=open_c,
            resolved_count=resolved_c,
            reopened_count=reopened_c,
            unresolved_rate=round(unresolved_rate, 3),
            representative_complaint_ids=rep_ids,
        )
