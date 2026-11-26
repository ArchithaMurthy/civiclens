"""
CivicLens — Ingestion module.

Loads raw datasets and returns normalised Complaint, WorkOrder, and WardMetrics lists.
Preserves all original records; does not write to data/raw/.

Usage:
    from pipeline.ingest import load_all
    complaints, work_orders, ward_metrics = load_all()
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from pipeline.schema import Complaint, WardMetrics, WorkOrder
from pipeline.normalise import (
    AGENCY_MAP,
    BBMP_LAT_MAX,
    BBMP_LAT_MIN,
    BBMP_LON_MAX,
    BBMP_LON_MIN,
    CATEGORY_MAP,
    STATUS_MAP,
)

RAW_DIR = Path("data/raw")

# ---------------------------------------------------------------------------
# Date parsing — handles mixed formats found in ichangemycity
# ---------------------------------------------------------------------------

_DATE_PATTERNS = [
    # M/D/YYYY H:MM or M/D/YYYY H:MM AM/PM
    (r"^(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?(?:\s*(AM|PM))?$", "mdy_slash_time"),
    # D-M-YYYY H:MM or D-M-YYYY H:MM:SS
    (r"^(\d{1,2})-(\d{1,2})-(\d{4})\s+(\d{1,2}):(\d{2})(?::(\d{2}))?$", "dmy_hyphen_time"),
    # M/D/YYYY (date only)
    (r"^(\d{1,2})/(\d{1,2})/(\d{4})$", "mdy_slash"),
    # D-M-YYYY (date only)
    (r"^(\d{1,2})-(\d{1,2})-(\d{4})$", "dmy_hyphen"),
    # ISO-like YYYY-MM-DDTHH:MM:SS
    (r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})", "iso"),
]


def _parse_date(raw: str) -> Optional[datetime]:
    if not raw or not raw.strip():
        return None
    raw = raw.strip()

    # Try ISO first (GovWatch dates)
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        pass

    for pattern, fmt in _DATE_PATTERNS:
        m = re.match(pattern, raw, re.IGNORECASE)
        if not m:
            continue
        g = m.groups()
        try:
            if fmt == "mdy_slash_time":
                month, day, year = int(g[0]), int(g[1]), int(g[2])
                hour, minute = int(g[3]), int(g[4])
                sec = int(g[5]) if g[5] else 0
                ampm = g[6]
                if ampm and ampm.upper() == "PM" and hour != 12:
                    hour += 12
                elif ampm and ampm.upper() == "AM" and hour == 12:
                    hour = 0
                return datetime(year, month, day, hour, minute, sec)
            elif fmt == "dmy_hyphen_time":
                day, month, year = int(g[0]), int(g[1]), int(g[2])
                hour, minute = int(g[3]), int(g[4])
                sec = int(g[5]) if g[5] else 0
                return datetime(year, month, day, hour, minute, sec)
            elif fmt == "mdy_slash":
                month, day, year = int(g[0]), int(g[1]), int(g[2])
                return datetime(year, month, day)
            elif fmt == "dmy_hyphen":
                day, month, year = int(g[0]), int(g[1]), int(g[2])
                return datetime(year, month, day)
        except (ValueError, OverflowError):
            continue

    return None


# ---------------------------------------------------------------------------
# GPS validation
# ---------------------------------------------------------------------------

def _gps_valid(lat: Optional[float], lon: Optional[float]) -> bool:
    if lat is None or lon is None:
        return False
    return (BBMP_LAT_MIN <= lat <= BBMP_LAT_MAX) and (BBMP_LON_MIN <= lon <= BBMP_LON_MAX)


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def _norm_category(raw: str) -> str:
    return CATEGORY_MAP.get(raw.strip().lower(), "other")


def _norm_agency(raw: Optional[str]) -> Optional[str]:
    if not raw or raw.strip().lower() in ("null", "none", ""):
        return None
    key = raw.strip().lower()
    return AGENCY_MAP.get(key, raw.strip())  # pass-through if not in map


def _norm_status(raw: str) -> str:
    return STATUS_MAP.get(raw.strip().lower(), "unknown")


def _make_id(source: str, index: int, seed: str = "") -> str:
    h = hashlib.sha1(f"{source}:{index}:{seed}".encode()).hexdigest()[:8]
    return f"{source.upper()[:4]}-{index:05d}-{h}"


# ---------------------------------------------------------------------------
# Load I Change My City complaints
# ---------------------------------------------------------------------------

def _load_ichangemycity() -> list[Complaint]:
    path = RAW_DIR / "ichangemycity_complaints.csv"
    complaints: list[Complaint] = []

    with open(path, encoding="cp1252", errors="replace") as f:
        for i, row in enumerate(csv.DictReader(f)):
            created_raw = row.get("created_at", "").strip()
            lat = Complaint.__fields__["latitude"].default  # just use validator
            lon_raw = row.get("longitude", "").strip()
            lat_raw = row.get("latitude", "").strip()

            category_raw = row.get("category_title", "").strip()
            status_raw = row.get("complaint_status_title", "").strip()
            agency_raw = row.get("civic_agency_title", "").strip()
            ward_id_raw = row.get("ward_id", "").strip()

            c = Complaint(
                complaint_id=_make_id("ICMC", i, row.get("title", "")),
                source="ichangemycity",
                source_record_id=None,
                created_at=_parse_date(created_raw),
                created_at_raw=created_raw,
                title=row.get("title", "").strip() or None,
                description=row.get("description", "").strip() or None,
                category=_norm_category(category_raw),
                category_original=category_raw,
                subcategory=row.get("sub_category_title", "").strip() or None,
                subcategory_normalised=None,
                status=_norm_status(status_raw),
                status_original=status_raw,
                civic_agency=_norm_agency(agency_raw),
                civic_agency_original=agency_raw or None,
                ward_id=ward_id_raw if ward_id_raw.isdigit() else None,
                ward_name=row.get("ward_title", "").strip() or None,
                ward_id_is_other=(ward_id_raw == "199"),
                latitude=lat_raw or None,
                longitude=lon_raw or None,
                location_text=row.get("location", "").strip() or None,
                gps_valid=_gps_valid(
                    float(lat_raw) if lat_raw else None,
                    float(lon_raw) if lon_raw else None,
                ),
                comment_count=row.get("comment_count", "").strip() or None,
                source_url=None,
            )
            complaints.append(c)

    return complaints


# ---------------------------------------------------------------------------
# Load GovWatch / CivicIssue issues
# ---------------------------------------------------------------------------

def _load_govwatch(path_name: str = "civicissue_issues.json") -> list[Complaint]:
    path = RAW_DIR / path_name
    complaints: list[Complaint] = []

    with open(path, encoding="utf-8", errors="replace") as f:
        records = json.load(f)

    for i, rec in enumerate(records):
        created_raw = rec.get("date", "")
        category_raw = rec.get("category", "").strip()
        area = rec.get("area", "").strip()
        ward_name = rec.get("ward_name", "").strip() or None
        ward_no_raw = str(rec.get("ward_no", "")).strip()

        c = Complaint(
            complaint_id=_make_id("GW", i, str(rec.get("id", ""))),
            source="civicissue_govwatch",
            source_record_id=str(rec.get("id", "")),
            created_at=_parse_date(created_raw),
            created_at_raw=created_raw,
            title=None,
            description=rec.get("text", "").strip() or None,
            category=_norm_category(category_raw),
            category_original=category_raw,
            subcategory=None,
            subcategory_normalised=None,
            status="open",
            status_original=rec.get("status", "open"),
            civic_agency=None,
            civic_agency_original=None,
            ward_id=int(ward_no_raw) if ward_no_raw.isdigit() else None,
            ward_name=ward_name,
            ward_id_is_other=False,
            latitude=None,
            longitude=None,
            location_text=area or None,
            gps_valid=False,
            comment_count=None,
            source_url=rec.get("source_url", "").strip() or None,
        )
        complaints.append(c)

    return complaints


# ---------------------------------------------------------------------------
# Load KAUN work orders
# ---------------------------------------------------------------------------

def load_work_orders() -> list[WorkOrder]:
    path = RAW_DIR / "kaun_work_orders_all_wards.json"
    work_orders: list[WorkOrder] = []

    road_kw = ["road", "tarring", "asphal", "pothole", "white top", "whitetopping",
               "resurfac", "laying", "macadam", "concreting", "bda road", "bbmp road"]
    drain_kw = ["drain", "swd", "stormwater", "storm water", "nalla", "culvert", "desilting"]
    footpath_kw = ["footpath", "footway", "pavement", "pedestrian"]
    streetlight_kw = ["streetlight", "street light", "lighting"]
    water_kw = ["water", "bwssb", "sewage", "pipeline", "ug drainage"]

    def classify(desc: str) -> str:
        d = (desc or "").lower()
        if any(k in d for k in road_kw):
            return "road"
        if any(k in d for k in drain_kw):
            return "drain"
        if any(k in d for k in footpath_kw):
            return "footpath"
        if any(k in d for k in streetlight_kw):
            return "streetlight"
        if any(k in d for k in water_kw):
            return "water"
        return "other"

    with open(path, encoding="utf-8", errors="replace") as f:
        data = json.load(f)

    for rec in data.get("work_orders", []):
        desc = rec.get("description", "")
        sa = rec.get("sanctioned_amount")
        np_ = rec.get("net_paid")
        ded = rec.get("deduction")
        wo = WorkOrder(
            work_order_id=str(rec.get("work_order_id", "")),
            source="kaun_bbmp",
            ward_no=rec.get("ward_no"),
            datameet243_no=rec.get("datameet243_no"),
            overlap_share=rec.get("overlap_share"),
            is_primary=rec.get("is_primary"),
            description=desc or None,
            contractor_name=rec.get("contractor_name") or None,
            contractor_phone=rec.get("contractor_phone") or None,
            sanctioned_amount=float(sa) if sa is not None else None,
            net_paid=float(np_) if np_ is not None else None,
            deduction=float(ded) if ded is not None else None,
            fy=rec.get("fy") or None,
            work_category=classify(desc),
            data_source=rec.get("data_source") or None,
        )
        work_orders.append(wo)

    return work_orders


# ---------------------------------------------------------------------------
# Load KAUN ward metrics
# ---------------------------------------------------------------------------

def load_ward_metrics() -> list[WardMetrics]:
    path = RAW_DIR / "kaun_ward_metrics.csv"
    metrics: list[WardMetrics] = []

    def _int(v: str) -> Optional[int]:
        try:
            return int(float(v)) if v.strip() else None
        except (ValueError, TypeError):
            return None

    def _float(v: str) -> Optional[float]:
        try:
            return float(v) if v.strip() else None
        except (ValueError, TypeError):
            return None

    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ward_no_raw = row.get("ward_no", "").strip()
            if not ward_no_raw.isdigit():
                continue
            m = WardMetrics(
                ward_no=int(ward_no_raw),
                ward_name=row.get("ward_name", "").strip(),
                assembly_constituency=row.get("assembly_constituency", "").strip() or None,
                pothole_complaints=_int(row.get("pothole_complaints", "")),
                pothole_data_year=_int(row.get("pothole_data_year", "")),
                road_crashes_2024=_int(row.get("road_crashes_2024", "")),
                road_crashes_2025=_int(row.get("road_crashes_2025", "")),
                fatal_crashes_2024=_int(row.get("fatal_crashes_2024", "")),
                fatal_crashes_2025=_int(row.get("fatal_crashes_2025", "")),
                spend_roads_and_infrastructure=_float(row.get("spend_roads_and_infrastructure", "")),
                spend_drainage=_float(row.get("spend_drainage", "")),
                spend_grand_total=_float(row.get("spend_grand_total", "")),
                spend_period=row.get("spend_period", "").strip() or None,
                total_work_orders=_int(row.get("total_work_orders", "")),
                ac_road_length_km=_float(row.get("ac_road_length_km", "")),
                ac_population_density=_float(row.get("ac_population_density", "")),
            )
            metrics.append(m)

    return metrics


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def load_all() -> tuple[list[Complaint], list[WorkOrder], list[WardMetrics]]:
    """Load and return all normalised datasets."""
    print("Loading I Change My City complaints…", flush=True)
    icmc = _load_ichangemycity()
    print(f"  Loaded {len(icmc)} ICMC complaints", flush=True)

    print("Loading GovWatch issues…", flush=True)
    gw = _load_govwatch()
    print(f"  Loaded {len(gw)} GovWatch complaints", flush=True)

    complaints = icmc + gw

    print("Loading KAUN work orders…", flush=True)
    work_orders = load_work_orders()
    print(f"  Loaded {len(work_orders)} work orders", flush=True)

    print("Loading KAUN ward metrics…", flush=True)
    ward_metrics = load_ward_metrics()
    print(f"  Loaded {len(ward_metrics)} ward metric rows", flush=True)

    return complaints, work_orders, ward_metrics
