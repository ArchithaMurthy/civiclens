"""
CivicLens — Shared schema definitions (Pydantic models).
All pipeline stages read and write these types.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, field_validator, model_validator


# ---------------------------------------------------------------------------
# Normalised complaint record
# ---------------------------------------------------------------------------

class Complaint(BaseModel):
    complaint_id: str                   # pipeline-assigned globally unique ID
    source: str                         # 'ichangemycity' | 'civicissue_govwatch'
    source_record_id: Optional[str]     # ID in the originating system (if any)

    created_at: Optional[datetime]      # parsed datetime; None if unparseable
    created_at_raw: str                 # original string preserved verbatim

    title: Optional[str]
    description: Optional[str]

    category: str                       # normalised category code (see CATEGORY_MAP)
    category_original: str              # original label from source
    subcategory: Optional[str]          # original subcategory label
    subcategory_normalised: Optional[str]  # normalised subcategory code

    status: str                         # 'open' | 'resolved' | 'in_progress' | 'reopened' | 'rejected' | 'closed' | 'unknown'
    status_original: str

    civic_agency: Optional[str]         # normalised agency code
    civic_agency_original: Optional[str]

    ward_id: Optional[int]              # source ward ID (1–199 in ICMC; None if unknown)
    ward_name: Optional[str]
    ward_id_is_other: bool              # True if ward_id=199 ("Other") in ICMC

    latitude: Optional[float]
    longitude: Optional[float]
    location_text: Optional[str]        # raw address / location string
    gps_valid: bool                     # True if coords are within BBMP bounding box

    comment_count: Optional[int]
    source_url: Optional[str]

    @field_validator('latitude', 'longitude', mode='before')
    @classmethod
    def coerce_float(cls, v):
        if v is None or str(v).strip() in ('', 'NULL', 'null', 'None'):
            return None
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    @field_validator('ward_id', mode='before')
    @classmethod
    def coerce_int(cls, v):
        if v is None or str(v).strip() in ('', 'NULL', 'null', 'None'):
            return None
        try:
            return int(v)
        except (ValueError, TypeError):
            return None

    @field_validator('comment_count', mode='before')
    @classmethod
    def coerce_int_comment(cls, v):
        if v is None or str(v).strip() in ('', 'NULL', 'null', 'None'):
            return None
        try:
            return int(float(v))
        except (ValueError, TypeError):
            return None


# ---------------------------------------------------------------------------
# Normalised work order
# ---------------------------------------------------------------------------

class WorkOrder(BaseModel):
    work_order_id: str
    source: str                         # 'kaun_bbmp'
    ward_no: Optional[int]              # original ward number in source
    datameet243_no: Optional[int]       # datameet243 ward number
    overlap_share: Optional[float]      # fraction of this ward covered by the work order ward
    is_primary: Optional[bool]
    description: Optional[str]
    contractor_name: Optional[str]
    contractor_phone: Optional[str]
    sanctioned_amount: Optional[float]  # INR
    net_paid: Optional[float]           # INR
    deduction: Optional[float]          # INR
    fy: Optional[str]                   # fiscal year e.g. '2024-25'
    work_category: Optional[str]        # pipeline-assigned keyword category
    data_source: Optional[str]


# ---------------------------------------------------------------------------
# Ward enrichment record
# ---------------------------------------------------------------------------

class WardMetrics(BaseModel):
    ward_no: int                        # datameet243 ward number
    ward_name: str
    assembly_constituency: Optional[str]
    pothole_complaints: Optional[int]   # from KAUN 2022 data
    pothole_data_year: Optional[int]
    road_crashes_2024: Optional[int]
    road_crashes_2025: Optional[int]
    fatal_crashes_2024: Optional[int]
    fatal_crashes_2025: Optional[int]
    spend_roads_and_infrastructure: Optional[float]  # INR
    spend_drainage: Optional[float]
    spend_grand_total: Optional[float]
    spend_period: Optional[str]
    total_work_orders: Optional[int]
    ac_road_length_km: Optional[float]
    ac_population_density: Optional[float]
