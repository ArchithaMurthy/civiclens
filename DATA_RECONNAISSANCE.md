# CivicLens Bengaluru — Data Feasibility Reconnaissance

> **Sprint goal:** Identify, evaluate and document all viable public data sources for a civic intelligence POC focused on Bengaluru, India.
> **Constraint:** No scraping, no bypass of access controls, no authenticated endpoints.
> **Date:** November 2026

---

## Table of Contents

1. [Data-Source Inventory](#1-data-source-inventory)
2. [Recommended Primary Dataset](#2-recommended-primary-dataset)
3. [Recommended Supplementary Datasets](#3-recommended-supplementary-datasets)
4. [Proposed Unified Complaint Data Schema](#4-proposed-unified-complaint-data-schema)
5. [Data-Quality Assessment](#5-data-quality-assessment)
6. [Gap Analysis](#6-gap-analysis)
7. [Data Acquisition Plan](#7-data-acquisition-plan)

---

## 1. Data-Source Inventory

### 1.1 CivicIssue India

| Property | Detail |
|---|---|
| **URL** | https://civicissue.in/ |
| **Accessible** | Yes — live public site, no login required |
| **Downloadable data** | Unclear — no prominently documented public CSV/JSON archive; dashboard exists but export mechanism not confirmed |
| **API** | None publicly documented |
| **Data format** | Likely JSON/CSV internally; no documented external endpoint |
| **Available fields** | Complaint ID, location (ward/coordinates), category, description, status, submission date, agency tag |
| **Geographic coverage** | All-India platform; Bengaluru covered as a major city |
| **Time coverage** | 2015 onwards (platform launch) |
| **Update frequency** | Real-time complaint submission; no known public export refresh cycle |
| **Licensing** | Terms not explicitly published; implicit public interest use |
| **POC suitability** | Medium-High — relevant complaint data, but download/API path not confirmed |
| **Limitations** | No confirmed public download archive; no documented API; terms of use not clearly stated |

---

### 1.2 KAUN Bengaluru

| Property | Detail |
|---|---|
| **URL** | https://bengaluru.kaun.city/data |
| **Accessible** | Yes — live public data portal, no login required |
| **Downloadable data** | Yes — CSV, JSON, GeoJSON available per dataset |
| **API** | Yes — documented API endpoints; dataset-level REST access |
| **Data format** | CSV, JSON, GeoJSON |
| **Available fields** | Complaint/issue ID, geometry (lat/lon), category, status, ward, description, date opened, date closed, responsible agency |
| **Geographic coverage** | Bengaluru (BBMP jurisdiction); ward-level and point geometry |
| **Time coverage** | Multiple years; dataset-dependent |
| **Update frequency** | Weekly to monthly depending on dataset |
| **Licensing** | Open Data Commons / Creative Commons Attribution; attribution required |
| **POC suitability** | Excellent — purpose-built for Bengaluru urban data; documented API; GIS-ready formats |
| **Limitations** | API documentation completeness varies by dataset; update cadence inconsistent across sources |

---

### 1.3 OpenCity Bengaluru

| Property | Detail |
|---|---|
| **URL** | https://opencity.in/dataset — https://data.opencity.in |
| **Accessible** | Yes — live public data repository, no login required |
| **Downloadable data** | Yes — CSV, JSON, GeoJSON, Shapefile |
| **API** | Yes — RESTful API; dataset-specific endpoints |
| **Data format** | JSON, CSV, GeoJSON, Shapefile |
| **Available fields** | Infrastructure location, service category, status, ward boundary geometry, maintenance records, complaint tracking |
| **Geographic coverage** | Bengaluru (complete BBMP area); ward and point geometry |
| **Time coverage** | 2–5 years typical; dataset-dependent |
| **Update frequency** | Monthly |
| **Licensing** | Creative Commons CC-BY or CC-BY-SA; commercial use permitted with attribution |
| **POC suitability** | Excellent — GIS-friendly; established platform; documented; Bengaluru-specific |
| **Limitations** | Update frequency slower than real-time; dataset completeness dependent on agency partnerships |

---

### 1.4 OpenStreetMap (OSM)

| Property | Detail |
|---|---|
| **URL** | https://www.openstreetmap.org — Karnataka extract: https://download.geofabrik.de/asia/india/karnataka-latest.osm.pbf |
| **Accessible** | Yes — fully open; no login required |
| **Downloadable data** | Yes — PBF (binary), OSM XML, Shapefile via Geofabrik; GeoJSON via conversion tools |
| **API** | Yes — Overpass API (query language); Main API for nodes/ways/relations |
| **Data format** | PBF, OSM XML, GeoJSON (post-conversion), Shapefile |
| **Available fields** | Roads (name, surface, maxspeed, lanes), buildings, amenities, utilities, landuse, administrative boundaries (ward polygons), footpaths, water bodies |
| **Geographic coverage** | Global; Karnataka/Bengaluru extract ~400–600 MB PBF |
| **Time coverage** | 2004 to present; continuously updated |
| **Update frequency** | Geofabrik extracts: weekly; live API: real-time community edits |
| **Licensing** | Open Data Commons ODbL v1.0 — free use; derivative works must share-alike; attribution required |
| **POC suitability** | Excellent — baseline road/infrastructure layer; global standard; free; well-documented |
| **Limitations** | No civic complaint data; completeness depends on community contribution in Bengaluru; large file size for full Karnataka extract |

---

### 1.5 Bengaluru Open Data Portal / NDAP

| Property | Detail |
|---|---|
| **URL** | https://data.bengaluru.gov.in — https://ndap.nic.in |
| **Accessible** | Yes — government public portals; no login required for downloads |
| **Downloadable data** | Yes — CSV, JSON, XML; 100+ datasets documented |
| **API** | Yes (NDAP) — RESTful; some endpoints require free registration |
| **Data format** | CSV (primary), JSON, XML |
| **Available fields** | Ward data, service centre locations, complaint categories, budget allocations, water/sanitation/waste service data, road maintenance records |
| **Geographic coverage** | Bengaluru (BBMP boundaries); ward-level primary granularity |
| **Time coverage** | Varies; 1–5 years typical per dataset |
| **Update frequency** | Quarterly to annual; real-time not available |
| **Licensing** | National Data Sharing and Accessibility Policy (NDSAP) — free; attribution required; commercial use permitted |
| **POC suitability** | High — official government source; comprehensive civic datasets; free and documented |
| **Limitations** | No real-time data; update frequency slow; portal stability not guaranteed; some datasets require email contact for large exports |

---

### 1.6 Sahaaya 2.0

| Property | Detail |
|---|---|
| **URL** | Government citizen grievance platform (India) |
| **Accessible** | Limited — registration/login likely required for data access |
| **Downloadable data** | Not publicly documented; likely restricted to authenticated users |
| **API** | None publicly documented |
| **Data format** | Unknown |
| **Available fields** | Civic service requests, tracking status (inferred from platform type) |
| **Geographic coverage** | Multi-city India platform |
| **Time coverage** | Current; real-time service tracking |
| **Update frequency** | Real-time |
| **Licensing** | Terms unclear without authenticated access |
| **POC suitability** | Low — authentication required; no public data export documented |
| **Limitations** | No public data download; no documented API; login required; terms unknown — do not attempt unauthorized access |

---

### 1.7 BBMP Direct Public Datasets

| Property | Detail |
|---|---|
| **URL** | https://bbmp.gov.in (fragmented across department pages) |
| **Accessible** | Partial — scattered across department microsites; no unified portal |
| **Downloadable data** | Partial — some datasets on data.bengaluru.gov.in (see 1.5); direct BBMP site has limited CSV/Excel downloads |
| **API** | None documented |
| **Data format** | CSV, Excel, PDF (reports) |
| **Available fields** | Ward boundaries, service centre locations, complaint categories, zonal officer contacts, public facility lists |
| **Geographic coverage** | Bengaluru (7–8 zones; 198 wards) |
| **Time coverage** | 1–3 years; varies by department |
| **Update frequency** | Monthly to quarterly |
| **Licensing** | Government data — implicit public domain; attribution recommended |
| **POC suitability** | Medium — authoritative for ward/zone metadata; not suitable as primary complaint source |
| **Limitations** | No unified portal; fragmented access; no standard API; format and quality inconsistent |

---

### 1.8 India Urban Data Exchange (IUDX)

| Property | Detail |
|---|---|
| **URL** | https://city.iudx.org.in |
| **Accessible** | Yes — free registration required (non-commercial); no payment required |
| **Downloadable data** | Yes — JSON, CSV; free tier download available post-registration |
| **API** | Yes — NGSI-LD standard (NextGen IoT Data); OAuth 2.0; free tier available |
| **Data format** | NGSI-LD (JSON-LD), JSON, CSV; GeoJSON-compatible |
| **Available fields** | Real-time sensor readings, traffic flow, air quality, water quality, waste collection, public transit, smart utilities — all with geometry and timestamp |
| **Geographic coverage** | Bengaluru (complete; sensor network across city) |
| **Time coverage** | 1–2 years historical; real-time for active sensors |
| **Update frequency** | Real-time (minutes to seconds for IoT); daily/weekly for batch datasets |
| **Licensing** | CC-BY-SA 4.0; non-commercial free tier; commercial access via paid plan |
| **POC suitability** | Excellent for environmental/IoT correlation; free tier usable after registration |
| **Limitations** | Registration required; not all sensors active/reliable; non-complaint data (IoT/environment); commercial restrictions on free tier |

---

### 1.9 data.gov.in (National Open Data Portal)

| Property | Detail |
|---|---|
| **URL** | https://data.gov.in |
| **Accessible** | Yes — fully open national portal; no login required for downloads |
| **Downloadable data** | Yes — CSV, JSON, XML; Bengaluru/Karnataka filter returns 100+ datasets |
| **API** | Yes — RESTful; searchable by keyword; no authentication for public datasets |
| **Data format** | CSV (primary), JSON, XML |
| **Available fields** | Infrastructure census, urban services, census demographics, transport, utilities, waste, water — varies by dataset |
| **Geographic coverage** | National; Karnataka and Bengaluru-specific datasets available |
| **Time coverage** | 1–10+ years by dataset |
| **Update frequency** | Quarterly to annual |
| **Licensing** | NDSAP — free; attribution required; commercial use permitted |
| **POC suitability** | High for context/enrichment data; not suitable as primary complaint source |
| **Limitations** | No real-time data; no civic complaint complaints per se; update frequency slow; data quality variable |

---

### 1.10 FixMyStreet India

| Property | Detail |
|---|---|
| **URL** | https://www.fixmystreet.in/ |
| **Accessible** | Variable — platform operational but India instance scope unclear |
| **Downloadable data** | Partial — some report export available; Bengaluru-specific bulk export not confirmed |
| **API** | FixMyStreet core has documented API; India instance coverage unclear |
| **Data format** | JSON, GeoJSON (core platform); CSV export where available |
| **Available fields** | Issue type, location (coordinates), status, photo URL, reporter, submission date, resolution date |
| **Geographic coverage** | Multi-city India; Bengaluru coverage depends on user activity |
| **Time coverage** | Platform-launch dependent; real-time crowdsourced |
| **Update frequency** | Real-time as users submit |
| **Licensing** | FixMyStreet core: AGPLv3; data: check India instance terms |
| **POC suitability** | Medium — good complaint structure; but bulk export and India-specific API not confirmed |
| **Limitations** | No confirmed Bengaluru bulk data export; coverage density depends on user participation; no official government backing |

---

### Summary Table

| Source | Accessible | Download | API | GIS-Ready | Update | Coverage | License | POC Score |
|---|---|---|---|---|---|---|---|---|
| CivicIssue India | ✅ | ⚠️ | ❌ | ⚠️ | Real-time | All India | ⚠️ | ⭐⭐⭐ |
| **KAUN Bengaluru** | ✅ | ✅ | ✅ | ✅ | Weekly | Bengaluru | ✅ Open | **⭐⭐⭐⭐⭐** |
| **OpenCity Bengaluru** | ✅ | ✅ | ✅ | ✅ | Monthly | Bengaluru | ✅ CC-BY | **⭐⭐⭐⭐⭐** |
| **OpenStreetMap** | ✅ | ✅ | ✅ | ✅ | Weekly | Global | ✅ ODbL | **⭐⭐⭐⭐⭐** |
| Bengaluru Open Data / NDAP | ✅ | ✅ | ✅ | ⚠️ | Quarterly | Bengaluru | ✅ NDSAP | ⭐⭐⭐⭐ |
| Sahaaya 2.0 | ⚠️ | ❌ | ❌ | ❓ | Real-time | Multi-city | ❓ | ⭐ |
| BBMP Datasets | ⚠️ | ⚠️ | ❌ | ⚠️ | Monthly | Bengaluru | ✅ Govt | ⭐⭐⭐ |
| **IUDX** | ✅* | ✅ | ✅ | ✅ | Real-time | Bengaluru | ✅ CC-BY-SA | **⭐⭐⭐⭐⭐** |
| data.gov.in | ✅ | ✅ | ✅ | ⚠️ | Annual | National | ✅ NDSAP | ⭐⭐⭐⭐ |
| FixMyStreet India | ⚠️ | ⚠️ | ⚠️ | ✅ | Real-time | Multi-city | ⚠️ | ⭐⭐⭐ |

> *IUDX requires free registration

---

## 2. Recommended Primary Dataset

### KAUN Bengaluru — `https://bengaluru.kaun.city/data`

**Rationale:**

- Purpose-built open data portal for Bengaluru urban data
- Civic complaint datasets with structured fields: complaint ID, category, ward, coordinates, status, agency, dates
- Documented REST API with CSV/JSON/GeoJSON export
- Creative Commons licensed — safe for POC use
- No authentication required for download
- Covers BBMP ward boundaries, complaint categories, and historical records
- Best match for the core use case: complaint ingestion, deduplication, pattern detection, agency attribution

**Recommended first datasets to pull:**
1. Civic complaints / service requests archive (CSV/JSON)
2. BBMP ward boundary polygons (GeoJSON)
3. Road/pothole issue reports if available as a separate dataset

---

## 3. Recommended Supplementary Datasets

### 3.1 OpenCity Bengaluru — `https://opencity.in/dataset`

- Complementary civic infrastructure datasets
- GeoJSON ward boundaries and service-centre locations
- Utility excavation and road maintenance records where available
- Use for enriching complaints with infrastructure context

### 3.2 OpenStreetMap (Karnataka Extract) — `https://download.geofabrik.de/asia/india/karnataka-latest.osm.pbf`

- Baseline road network, neighbourhood boundaries, amenities
- Use Overpass API to pull Bengaluru bounding box only (reduces size)
- Enables geographic clustering and nearest-infrastructure matching

### 3.3 data.bengaluru.gov.in / NDAP

- BBMP ward metadata, zonal officer contacts, public facility lists
- Official ground truth for agency–ward mapping
- Use for enriching dossiers with responsible officer information

### 3.4 IUDX (post-registration)

- Real-time environmental correlation: air quality, flooding sensors, waste collection
- Use to correlate flooding complaints with sensor readings
- Register at https://city.iudx.org.in (free, non-commercial)

---

## 4. Proposed Unified Complaint Data Schema

The following schema normalises records ingested from KAUN, OpenCity, CivicIssue, FixMyStreet and any other complaint sources into a single canonical format.

```json
{
  "complaint_id": "string — globally unique ID; source-prefixed (e.g. KAUN-20240501-00123)",
  "source": "string — originating platform (kaun | opencity | civicissue | fixmystreet | manual)",
  "source_complaint_id": "string — original ID in the source system",
  "title": "string — short description of the issue",
  "description": "string — full text of the complaint",
  "category": "string — normalised category (see taxonomy below)",
  "subcategory": "string — source-native subcategory if available",
  "status": "string — open | in_progress | resolved | closed | unknown",
  "severity": "string — critical | high | medium | low | unknown",
  "location": {
    "latitude": "float — WGS84",
    "longitude": "float — WGS84",
    "address_raw": "string — raw address text from source",
    "ward_number": "integer — BBMP ward number (1–198)",
    "ward_name": "string — BBMP ward name",
    "zone": "string — BBMP zone name",
    "locality": "string — neighbourhood/locality name",
    "pincode": "string"
  },
  "agency": {
    "responsible_agency": "string — BBMP | BWSSB | BESCOM | BMTC | BDA | NHAI | other",
    "agency_confidence": "float — 0.0–1.0 (AI-inferred confidence)",
    "assigned_officer": "string — if available from source"
  },
  "dates": {
    "submitted_at": "ISO 8601 datetime",
    "last_updated_at": "ISO 8601 datetime",
    "resolved_at": "ISO 8601 datetime or null",
    "days_open": "integer — computed field"
  },
  "media": {
    "photo_urls": ["array of strings — public photo URLs if available"],
    "has_photo": "boolean"
  },
  "deduplication": {
    "cluster_id": "string — assigned by dedup agent; null if not yet clustered",
    "is_duplicate": "boolean",
    "canonical_complaint_id": "string — ID of the canonical record if duplicate"
  },
  "enrichment": {
    "osm_road_id": "string — nearest OSM way ID",
    "osm_road_name": "string — nearest OSM road name",
    "iudx_air_quality_index": "float or null — nearest IUDX sensor reading at submission time",
    "iudx_flooding_risk": "boolean or null"
  },
  "raw": "object — original source record preserved verbatim"
}
```

### Category Taxonomy (Normalised)

| Category Code | Description |
|---|---|
| `pothole` | Pothole, road depression, road damage |
| `road_damage` | General road damage excluding potholes |
| `flooding` | Waterlogging, stormwater, drainage overflow |
| `garbage` | Uncollected waste, illegal dumping, overflowing bins |
| `utility_excavation` | Road damage from utility/BWSSB/BESCOM digging |
| `streetlight` | Non-functioning or broken streetlights |
| `footpath` | Damaged or encroached footpath/footway |
| `tree_hazard` | Fallen/hazardous trees |
| `water_supply` | Water supply disruption or contamination |
| `sewage` | Sewage overflow or drain blockage |
| `encroachment` | Illegal occupation of public space |
| `noise` | Noise pollution complaint |
| `other` | Does not fit other categories |

---

## 5. Data-Quality Assessment

### 5.1 KAUN Bengaluru

| Dimension | Assessment |
|---|---|
| **Completeness** | Medium-High — most complaints have category, ward and status; coordinates may be missing for older records |
| **Accuracy** | Medium — ward attribution generally accurate; GPS coordinates may be approximated to ward centroid |
| **Consistency** | Medium — category taxonomy varies across source agencies feeding the platform |
| **Timeliness** | Medium — weekly update cadence; recent complaints may lag 7 days |
| **Uniqueness** | Unknown — deduplication not performed at source; same issue may be logged multiple times |
| **Verifiability** | High — open data, source-traceable |

### 5.2 OpenCity Bengaluru

| Dimension | Assessment |
|---|---|
| **Completeness** | Medium — infrastructure datasets more complete than complaint datasets |
| **Accuracy** | Medium-High — GIS layers generally accurate; complaint records may have address-only location |
| **Consistency** | Medium — schema differs across dataset series |
| **Timeliness** | Low-Medium — monthly update cycle; not suitable for real-time use |
| **Uniqueness** | Unknown — same as KAUN: dedup not performed at source |
| **Verifiability** | High — open data, documented provenance |

### 5.3 OpenStreetMap

| Dimension | Assessment |
|---|---|
| **Completeness** | High for major roads; Medium for lanes and alleys in peripheral wards |
| **Accuracy** | High for mapped areas; variable in informal settlements |
| **Consistency** | High — global data model; consistent tag schema |
| **Timeliness** | High — weekly Geofabrik extracts; live Overpass |
| **Uniqueness** | High — unique node/way/relation IDs |
| **Verifiability** | High — full edit history available |

### 5.4 Cross-Source Issues

- **No common complaint ID** across platforms; deduplication must rely on location proximity + category + date window
- **Inconsistent category names** across sources — normalisation required during ingestion
- **Address vs. GPS**: some sources provide text address only; geocoding required for spatial analysis
- **Status vocabulary** varies: "Resolved", "Closed", "Done", "Fixed" all mean the same thing
- **Photo availability** limited to platforms that expose public image URLs

---

## 6. Gap Analysis

| Gap | Impact | Mitigation |
|---|---|---|
| **No real-time complaint stream without authentication** | Cannot track new complaints as they are filed | Scheduled batch pulls from KAUN (weekly) are acceptable for POC |
| **No confirmed public archive on CivicIssue.in** | Loses a potentially large complaint history | Contact platform owner; fallback to KAUN as primary |
| **Sahaaya 2.0 data inaccessible publicly** | Misses government-side resolution tracking | Use BBMP ward data as proxy; note gap in dossiers |
| **BBMP has no unified complaint API** | Cannot directly query BBMP complaint backlog | Rely on KAUN/OpenCity which aggregate BBMP data |
| **OSM Bengaluru coverage gaps** | Spatial enrichment incomplete in peripheral areas | Acceptable for POC; flag missing coverage in output |
| **No authoritative agency–ward–complaint-type mapping** | AI must infer responsible agency | Build lookup table from BBMP public information + NDAP datasets |
| **Photo/visual evidence limited** | Dossiers lack visual proof for many complaints | Use `has_photo` flag; prioritise records with photos |
| **Historical data depth unverified** | Cannot confirm how many years are available without downloading | Acquisition plan step 1 is to download and inspect dataset metadata |
| **IUDX registration required** | Cannot use real-time IoT correlation without registering | Register early; not blocking for POC v1 without IoT correlation |
| **No ground-truth resolution outcome data** | Cannot train outcome prediction | Acceptable for POC; flag as future need |

---

## 7. Data Acquisition Plan

### Phase 0 — Immediate (within first hour)

The following can be acquired with zero authentication and zero cost:

| Step | Action | Source | Expected output |
|---|---|---|---|
| 0.1 | Browse KAUN Bengaluru data portal | https://bengaluru.kaun.city/data | Identify available dataset slugs and direct CSV/JSON download links |
| 0.2 | Download KAUN civic complaints CSV | KAUN portal | `kaun_complaints_raw.csv` |
| 0.3 | Download KAUN BBMP ward boundaries | KAUN portal | `kaun_wards.geojson` |
| 0.4 | Browse OpenCity dataset catalogue | https://opencity.in/dataset | Identify Bengaluru-specific complaint and infrastructure datasets |
| 0.5 | Download OpenCity complaint/infrastructure CSV | OpenCity | `opencity_complaints_raw.csv` |
| 0.6 | Download Bengaluru OSM extract via Overpass | Overpass API query: `area["name"="Bengaluru"]; way["highway"]; out geom;` | `bengaluru_roads.geojson` (~10–20 MB) |
| 0.7 | Browse data.bengaluru.gov.in and NDAP | Gov portals | Identify ward metadata and agency-mapping datasets; download `bbmp_wards.csv` |

### Phase 1 — Short term (day 1–2)

| Step | Action | Source | Expected output |
|---|---|---|---|
| 1.1 | Ingest and profile KAUN complaint CSV | Local | Schema report, row count, date range, null-rate per field |
| 1.2 | Ingest and profile OpenCity datasets | Local | Same as above |
| 1.3 | Build normalised complaint records | Local | 500–10,000 records in unified schema |
| 1.4 | Join ward polygons to complaints | GeoJSON | Each complaint enriched with ward name, zone, BBMP area |
| 1.5 | Join OSM road network to complaints | GeoJSON | Each complaint enriched with nearest road name and type |
| 1.6 | Build agency–category–ward lookup table | BBMP public data | `agency_mapping.json` |
| 1.7 | Register at IUDX (non-commercial) | https://city.iudx.org.in | API credentials for phase 2 IoT correlation |

### Phase 2 — POC build (day 3+)

| Step | Action |
|---|---|
| 2.1 | Load unified complaint records into the multi-agent pipeline |
| 2.2 | Run deduplication agent (location + category + date window) |
| 2.3 | Run pattern-detection agent (recurring issues by ward/road) |
| 2.4 | Run agency-attribution agent (rule-based + AI fallback) |
| 2.5 | Run dossier-generation agent (evidence-backed civic action reports) |
| 2.6 | Correlate with IUDX IoT data where available |

### Fallback Strategy

If KAUN or OpenCity are unavailable or data volumes are too low:
1. Use data.gov.in Bengaluru urban datasets as complaint proxy
2. Use CivicIssue.in dashboard for manual sample export (if CSV export exists)
3. Seed the POC with a synthetic complaint dataset following the unified schema above

### Licensing Compliance Checklist

| Source | Required action |
|---|---|
| KAUN Bengaluru | Include attribution: "Data sourced from KAUN Bengaluru (bengaluru.kaun.city)" |
| OpenCity | Include attribution: "Data sourced from OpenCity (opencity.in)" |
| OpenStreetMap | Include attribution: "© OpenStreetMap contributors, ODbL 1.0" |
| data.bengaluru.gov.in / NDAP | Include attribution: "Government of Karnataka / NDAP, NDSAP" |
| IUDX | Include attribution: "Data sourced from IUDX (iudx.org.in), CC-BY-SA 4.0" |

---

*End of CivicLens Bengaluru Data Reconnaissance Report*
