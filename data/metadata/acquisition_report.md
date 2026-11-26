# CivicLens Bengaluru — Sprint 1 Acquisition Report

> **Date:** 2026-11-23  
> **Sprint goal:** Acquire and profile real Bengaluru civic datasets to determine whether sufficient real data exists for the CivicLens POC.  
> **Decision gate:** GO / NARROW SCOPE / NO-GO

---

## 1. What Was Attempted vs. What Was Acquired

| Source | Attempted | Acquired | Outcome |
|---|---|---|---|
| KAUN Bengaluru | Yes | Yes | 6 datasets (ward metrics, work orders, ward crosswalk, contractors, MLAs) |
| I Change My City (via OpenCity mirrors) | Yes | Yes | **16,071 real complaints, 2019–2021** |
| GovWatch / CivicIssue.in | Yes | Yes | **1,012 + 4,989 real complaints, May–Jul 2026** |
| OpenCity (direct) | Yes | No | 403 Forbidden — all access blocked |
| data.bengaluru.gov.in | Yes | No | DNS failure — domain down |
| NDAP | Yes | No | DNS failure |
| BBMP official | Yes | No | SSL certificate failure |
| Overpass API (OSM) | Yes | No | 502/406/timeout — all endpoints unreachable |
| Geofabrik OSM extract | Yes | No (deferred) | Accessible but requires osmium tooling not yet available |
| data.gov.in | Yes | No | JavaScript SPA — no programmatic API |
| Sahaaya 2.0 | No (design) | No | Requires authentication; excluded by policy |
| FixMyStreet India | Yes | No | No bulk export available |

**Net result:** 12 real datasets acquired across 3 source families. 8 sources failed or were deferred.

---

## 2. Dataset Profile Highlights

### Best dataset: `ichangemycity_complaints.csv`

| Metric | Value |
|---|---|
| Records | 16,071 |
| Date range | Jan 2019 – Sep 2021 (2 years 9 months) |
| GPS coverage | 100% (every record has lat/lon) |
| Ward coverage | 198 distinct wards |
| Complaint text | 100% populated (avg 224 chars) |
| Civic agency | 95.9% populated |
| Category | 99.8% populated |
| Complaint status | 100% populated (Open / Resolved / On-the-Job / Re-opened / Rejected / Closed) |
| Top categories | Mobility – Roads (31.6%), Garbage (24.6%), Traffic (6.0%), Yellow Spot (5.9%) |
| Top agency | BBMP (79.8%), BTP (5.9%), BWSSB (4.1%) |
| Duplicates | 2,057 near-duplicates (same ward + category + date) — real deduplication signal |
| Resolution rate | 30.7% resolved (4,937 / 16,071) |
| Encoding issue | cp1252 (Windows-1252) — requires explicit encoding handling |

**Assessment:** Excellent quality. All key fields for the CivicLens pipeline are present and populated. This dataset alone is sufficient to build a credible POC demonstrating deduplication, pattern detection, agency attribution, and dossier generation.

---

### Second dataset: `kaun_work_orders_all_wards.json`

| Metric | Value |
|---|---|
| Records | 11,072 work orders |
| Wards covered | 243 (all BBMP wards) |
| Key fields | description, contractor, sanctioned amount, net paid, deduction, FY |
| Fiscal year | Primarily 2024–25 |
| Descriptions | Road/drain/infrastructure work descriptions (readable text) |
| GPS | None — ward-level only |
| Start/end dates | Missing for most records |

**Assessment:** Strong secondary dataset. Descriptions contain exact road names and construction types (white-topping, SWD drain construction, streetlight installation). Enables work-order vs. complaint correlation: *"Pothole complaints in ward X despite ₹2.3Cr road contract in 2024-25."*

---

### Third dataset: `kaun_ward_metrics.csv`

| Metric | Value |
|---|---|
| Records | 254 wards |
| Pothole complaints | 243 wards with 2022 data; total 16,364 complaints |
| Road crashes | 58 wards with 2024–2025 data |
| Spending | All 254 wards; 2018–2023 period |
| Zone field | Empty — missing for all wards |

**Assessment:** Good enrichment layer. Ward-level aggregate complaint counts (potholes), spending, infrastructure stats. Zone field being empty is a gap.

---

### Fourth dataset: `civicissue_issues.json` (GovWatch)

| Metric | Value |
|---|---|
| Records | 1,012 (filtered); 4,989 (unfiltered) |
| Date range | May–Jul 2026 (very recent) |
| GPS | None — area text only |
| Ward coverage | 114 / 1,012 have ward_no (11.3%) |
| Text | Full tweet text (avg 236 chars) |
| Primary categories | Electricity (40.7%), Waste (33.8%), Water (7.8%), Roads (6.7%) |
| Severity | Mostly "low" (98.9%) — severity scoring is not calibrated |

**Assessment:** Valuable for recent (2026) complaint signal and social media complaint text. Poor ward coverage limits geospatial analysis. Useful as an NLP/classification training supplement.

---

## 3. Data Quality Summary

| Dimension | I Change My City | KAUN Work Orders | KAUN Ward Metrics | GovWatch |
|---|---|---|---|---|
| **Completeness** | High | Medium | Medium-High | Medium |
| **GPS accuracy** | High | None | None | None |
| **Text richness** | High | Medium | Low | High |
| **Recency** | Low (2021) | High (2025) | Medium | Very High (2026) |
| **Ward attribution** | High (198 wards) | High (all wards) | High | Low (11.3%) |
| **Category taxonomy** | Inconsistent names | Work description | Aggregate only | 8 broad categories |
| **Duplicates** | Present (2,057) | Low | N/A | Low |
| **Usability for POC** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## 4. Field Mapping to Unified Schema

The following maps the primary dataset (`ichangemycity_complaints.csv`) fields to the unified schema defined in `DATA_RECONNAISSANCE.md §4`:

| Unified Schema Field | Source Field | Notes |
|---|---|---|
| `complaint_id` | Derived: `"ICMC-" + row_index` | No explicit ID in source |
| `source` | Hardcoded: `"ichangemycity"` | |
| `source_complaint_id` | None in source | Missing — assign row index |
| `title` | `title` | Direct map |
| `description` | `description` | Direct map |
| `category` | Normalised from `category_title` | Requires taxonomy mapping |
| `subcategory` | `sub_category_title` | Direct map |
| `status` | `complaint_status_title` | Normalise: "On-the-Job" → `in_progress` |
| `location.latitude` | `latitude` | Direct map (float) |
| `location.longitude` | `longitude` | Direct map (float) |
| `location.address_raw` | `location` | Full address string |
| `location.ward_number` | `ward_id` | Direct map (integer) |
| `location.ward_name` | `ward_title` | Direct map |
| `agency.responsible_agency` | `civic_agency_title` | Normalise agency names (duplicates: BBMP and "Bruhat Bengaluru Mahanagara Palike") |
| `dates.submitted_at` | `created_at` | Requires date parsing (mixed formats: `1-1-2019`, `1/13/2019`, `9-9-2021`) |
| `dates.days_open` | Computed | `today - created_at` if status != Resolved |
| `media.has_photo` | Not in source | Default `false` |

**Two normalisation tasks required before pipeline use:**
1. **Date parsing:** `created_at` field has at least 3 date formats (`D-M-YYYY`, `M/D/YYYY HH:MM`, `M-D-YYYY HH:MM`) and mixed AM/PM conventions.
2. **Agency deduplication:** "BBMP" and "Bruhat Bengaluru Mahanagara Palike" are the same entity; "BCP" and "Bangalore Traffic Police" overlap.

---

## 5. Unresolved Data Gaps

| Gap | Severity | Notes |
|---|---|---|
| **No GPS in work orders or ward metrics** | Medium | Cannot spatially join complaints to work orders at record level; must use ward-level join |
| **I Change My City data ends Sep 2021** | Medium | 5-year data gap to present; GovWatch covers May–Jul 2026 only |
| **No BBMP ward boundary GeoJSON** | Medium | Cannot draw ward polygons for maps; Overpass deferred; must source separately |
| **Ward numbering inconsistency** | Medium | I Change My City uses 1–199 ward IDs; KAUN uses datameet-243 scheme; crosswalk CSV bridges them but requires careful join |
| **Zone field empty in KAUN** | Low | Cannot group wards by zone (Bommanahalli, Dasarahalli, etc.) without a separate lookup |
| **No complaint IDs in I Change My City** | Low | Deduplication must rely on content fingerprint, not ID |
| **I Change My City date format inconsistency** | Low | 3+ date formats in `created_at` column; must parse defensively |
| **GovWatch low ward coverage (11.3%)** | High for GovWatch | Most GovWatch complaints cannot be assigned to a ward without geocoding |
| **OSM road network unavailable** | Low for POC | Nearest-road enrichment not possible in Sprint 2 without additional tools |

---

## 6. Decision: GO / NARROW SCOPE / NO-GO

## **Decision: GO ✅**

### Evidence

The **I Change My City dataset** alone provides:

- **16,071 real Bengaluru civic complaints** with full text, GPS coordinates, ward attribution, complaint status, and civic agency — across 2 years 9 months
- **100% GPS coverage** enabling spatial clustering and density analysis
- **198 distinct wards** — full BBMP coverage
- **Pothole/road complaints: 5,072 records** (31.6%), **garbage: 3,946** (24.6%), **flooding/waterlogging: 226** (1.4%)
- **~2,057 near-duplicate records** providing a real deduplication challenge for the agent to solve
- **4,937 resolved complaints** providing ground-truth resolution outcomes
- **Civic agency attribution** for 95.9% of records across BBMP, BTP, BWSSB, BESCOM

Supplemented by:
- **11,072 KAUN work orders** (2024–25) mapping contractor road/drain work per ward — enables the "spent ₹X Cr on roads yet 505 pothole complaints" dossier narrative
- **1,012 GovWatch tweets** (May–Jul 2026) providing recent civic complaint signal for temporal trend analysis
- **243-ward metrics** including pothole complaints per ward for 2022 and road crash statistics

Together, this data fully supports all five envisioned CivicLens agent capabilities:

| Agent | Data Available |
|---|---|
| **Complaint Ingestion Agent** | I Change My City CSV; GovWatch JSON |
| **Deduplication Agent** | 2,057 near-duplicates to work with |
| **Pattern Detection Agent** | 198 wards × 2.75 years; top-ward and top-category analysis |
| **Agency Attribution Agent** | 95.9% of records have `civic_agency_title` |
| **Dossier Generation Agent** | Complaints + work orders + ward spending = evidence-backed narrative |

---

## 7. Recommendation for Sprint 2

### Primary dataset for pipeline
`data/raw/ichangemycity_complaints.csv` — 16,071 records, all core fields present

### Supplementary datasets
1. `data/raw/kaun_work_orders_all_wards.json` — ward-level road/drain work orders (accountability layer)
2. `data/raw/kaun_ward_metrics.csv` — ward enrichment (pothole counts, spending, infrastructure)
3. `data/raw/civicissue_issues.json` — recent 2026 complaints (NLP/text signal)
4. `data/raw/kaun_ward_crosswalk.csv` — ward ID reconciliation

### Sprint 2 tasks

1. **Normalise I Change My City dates** — handle 3+ date formats in `created_at`
2. **Normalise category taxonomy** — map 43 raw categories to the 13-category unified taxonomy
3. **Normalise agency names** — deduplicate BBMP/BTP/BWSSB variants
4. **Build ward join** — use `kaun_ward_crosswalk.csv` to reconcile ward IDs between I Change My City (1–199 scheme) and KAUN (datameet-243 scheme)
5. **Build deduplication agent** — cluster complaints within 500m radius + same category + 7-day window
6. **Build pattern detection agent** — rank wards by complaint density; identify chronic unresolved clusters
7. **Build agency attribution agent** — start with rule-based (use `civic_agency_title`) + AI fallback for NULL agency records (619 records)
8. **Build dossier generation agent** — combine complaint cluster + work order history + spending vs. complaint ratio
9. **Acquire OSM ward boundaries** — install `osmium-tool` or use alternative GeoJSON source for ward polygons (needed for maps)

### One risk to address before Sprint 2 begins
The I Change My City data ends in September 2021. The GovWatch data starts May 2026. There is a **~4.5-year gap** in complaint data. The POC dossiers will reflect historical patterns from 2019–2021, not current conditions. This should be noted explicitly in any POC outputs.

**To close this gap:** Manually download the full I Change My City dataset from OpenCity via browser (the UUID URL is known: `https://data.opencity.in/dataset/i-change-my-city-data/resource/a60abf5c-...`) and check if there are more recent exports.

---

*Sprint 1 complete.*
