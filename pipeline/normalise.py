"""
CivicLens — Category and agency normalisation maps.

CATEGORY_MAP: maps raw source category strings -> normalised codes.
AGENCY_MAP:   maps raw agency strings -> canonical short codes.
STATUS_MAP:   maps raw status strings -> normalised status codes.
ROAD_SUBCATS: subcategory labels that belong to the 'road' focus set.
"""

# ---------------------------------------------------------------------------
# Category normalisation
# ---------------------------------------------------------------------------
# Format: {lower-stripped source string: normalised_code}

CATEGORY_MAP: dict[str, str] = {
    # Road / infrastructure
    "mobility - roads, footpaths and infrastructure": "road_infrastructure",
    "mobility": "road_infrastructure",
    # Garbage
    "garbage and unsanitary practices": "garbage",
    "waste": "garbage",
    # Traffic
    "traffic and road safety": "traffic_safety",
    "traffic": "traffic_safety",
    # Streetlights
    "street lighting": "streetlight",
    "streetlights": "streetlight",
    "electricity": "electricity",
    "electricity and power supply": "electricity",
    # Water
    "water supply and services": "water_supply",
    "water": "water_supply",
    # Sewage
    "sewerage systems": "sewage",
    "sewage": "sewage",
    # Storm water / flooding
    "storm water drains": "flooding",
    "flooding": "flooding",
    # Yellow spot (public urination/defecation)
    "yellow spot": "sanitation",
    # Animals
    "animal husbandry": "animal",
    "animals": "animal",
    # Pollution
    "pollution": "pollution",
    # Parks
    "parks": "parks",
    # Crime / safety
    "crime and safety": "safety",
    # Community infrastructure
    "community infrastructure and services": "community_infrastructure",
    # Roads in GovWatch
    "roads": "road_infrastructure",
    # Others
    "others": "other",
    "other": "other",
}

SUBCATEGORY_ROAD_SET = {
    "fixing/reparing potholes",
    "fixing/repairing potholes",
    "tarring or asphalting of existing road",
    "tarring or asphalting of mud/kutcha/unpaved road",
    "flooding/waterlogging of roads and footpaths",
    "construction of roadside drains",
    "desilting existing roadside drains",
    "removal of roadside debris (construction material)",
    "repair of bridge and culverts",
}

# ---------------------------------------------------------------------------
# Civic agency normalisation
# ---------------------------------------------------------------------------
AGENCY_MAP: dict[str, str] = {
    "bbmp": "BBMP",
    "bruhat bengaluru mahanagara palike": "BBMP",
    "btp": "BTP",
    "bangalore traffic police": "BTP",
    "bwssb": "BWSSB",
    "bangalore water supply and sewerage board": "BWSSB",
    "bescom": "BESCOM",
    "bangalore electricity supply company": "BESCOM",
    "bmtc": "BMTC",
    "bcp": "BCP",
    "kspcb": "KSPCB",
    "karnataka state pollution control board": "KSPCB",
    "ksfes": "KSFES",
    "bda": "BDA",
    "ksrtc": "KSRTC",
    "null": None,
    "": None,
}

# ---------------------------------------------------------------------------
# Status normalisation
# ---------------------------------------------------------------------------
STATUS_MAP: dict[str, str] = {
    "open": "open",
    "resolved": "resolved",
    "on-the-job": "in_progress",
    "re-opened": "reopened",
    "rejected": "rejected",
    "closed": "closed",
    "unknown": "unknown",
    "": "unknown",
}

# ---------------------------------------------------------------------------
# BBMP bounding box for GPS validation (approximate)
# ---------------------------------------------------------------------------
BBMP_LAT_MIN = 12.70
BBMP_LAT_MAX = 13.20
BBMP_LON_MIN = 77.40
BBMP_LON_MAX = 77.85
