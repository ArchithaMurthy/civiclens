# CivicLens Dashboard — Design Specification

**Sprint:** 3 Phase 4  
**Date:** 2026-11-24  
**Grounded in:** `data/processed/civic_cases.json` (298 cases, post-fix)  
**Purpose:** Define what a decision-support dashboard for CivicLens should show,  
to whom, in what layout, and with what data bindings — before any implementation.

---

## 0. Design Principles

1. **Evidence first, inference second.** Every number on screen must be traceable to a source
   record. Hypotheses must be visually distinguished from facts.
2. **Show what the data actually contains.** The dashboard is built for 298 road-infrastructure
   cases across Bengaluru wards (2019–2022 ICMC data). Do not design for aspirational
   features not yet backed by real data.
3. **Actionable, not decorative.** Each panel must drive one decision: *Which case to
   investigate? Which ward to prioritise? Which work order to scrutinise?*
4. **Honest about uncertainty.** Ward join confidence (`exact_name` / `fuzzy_name` / `none`),
   ward-level vs GPS-matched crash data, and temporal mismatch (complaints 2019–2022 vs
   work orders 2023–2026) must be surfaced, not hidden.
5. **Static POC first.** The first dashboard implementation is a static single-page HTML
   generated from `civic_cases.json`. No live database, no real-time update.

---

## 1. Users and Use Cases

| User | Goal | Key questions |
|---|---|---|
| **Civic journalist / researcher** | Find the worst unresolved road problems in a ward or locality | Which wards have the most HIGH cases? Which complaints have been open for 4 years? |
| **BBMP ward official** | See the case load for their ward and prioritise resources | How many unresolved clusters are in my ward? What is the work order spend vs complaint count? |
| **NGO / RWA member** | Build a complaint dossier for a specific road/area | Download all evidence for a specific case; view GPS cluster on map |
| **Civic data engineer** | Validate pipeline outputs and inspect edge cases | Inspect ward join confidence; check fuzzy-match cases; review large bounding-box clusters |

---

## 2. Dashboard Structure

The dashboard has **4 views** arranged as a single-page application with tab navigation.

```
[ Overview ] [ Ward Explorer ] [ Case List ] [ Case Detail ]
```

---

## 3. View 1 — Overview

**Purpose:** City-wide summary at a glance. Entry point for all users.

### Panel 3.1 — Summary Metrics Bar (top of page)

Horizontal row of 6 KPI cards. All numbers are static, derived from `civic_cases.json`.

| Card | Value (actual) | Label |
|---|---|---|
| Total Cases | 298 | Civic cases detected |
| HIGH Priority | 14 | Need urgent attention |
| MEDIUM Priority | 175 | Require monitoring |
| Total Complaints | sum of `complaint_count` across all cases | Source complaints |
| Avg Unresolved | 46.3% | Complaints unresolved |
| Wards Affected | count distinct `primary_ward_name` | Wards with active issues |

**Data binding:** Computed once from `civic_cases.json` at page load.

### Panel 3.2 — Priority Score Distribution (bar chart)

Histogram of `priority_score` values bucketed into 10 bins (0.1 width, range 0.1–0.7).
Each bar coloured by tier: HIGH (red ≥ 0.5), MEDIUM (amber ≥ 0.3), LOW (grey < 0.3).

**Purpose:** Shows the analyst that most cases cluster in MEDIUM tier (0.3–0.5) and that
HIGH cases are genuinely rare (14 of 298 = 4.7%).

**Data binding:** `priority_score` from each case.

### Panel 3.3 — Top 10 Wards Heatmap (bar chart)

Horizontal bar chart of the 10 wards with the most cases. Bars segmented by priority tier.

Actual top 10 (from data):

| Ward | Cases | HIGH |
|---|---|---|
| Begur | 16 | 1 |
| Bellanduru | 15 | 2 |
| Horamavu | 12 | 2 |
| Thanisandra | 9 | 1 |
| Ramamurthy Nagar | 8 | 0 |
| Hagadur | 8 | 0 |
| Singasandra | 7 | 2 |
| Varthur | 6 | 1 |
| Vasanthapura | 6 | 0 |
| Bilekahalli | 5 | 0 |

**Data binding:** `primary_ward_name`, `priority_tier` per case.

### Panel 3.4 — Subcategory Breakdown (donut chart)

Shows distribution of `representative_subcategory` across all 298 cases.

Actual distribution:
- Fixing/Repairing Potholes: 169 (56.7%)
- Tarring/Asphalting of Existing Road: 100 (33.6%)
- Flooding/Waterlogging: 6 (2.0%)
- Other: 23 (7.7%)

**Data binding:** `representative_subcategory` per case.

### Panel 3.5 — Years Active Distribution (bar chart)

Simple bar chart: X = number of years active (2, 3, 4), Y = count of cases.

Actual: 2 years = 105 cases, 3 years = 123 cases, 4 years = 70 cases (all ICMC years).

**Data binding:** `len(years_active)` per case.

### Panel 3.6 — Data Provenance Note

Small text block at bottom of Overview:

> **Data sources:** I Change My City complaints (16,071 records, 2019–2022), KAUN work orders
> (11,072 records, FY 2023–2026), KAUN ward metrics (243 wards).  
> **Ward enrichment:** 206 exact name matches, 66 fuzzy matches, 26 unmatched.  
> **Temporal note:** Complaint data is 2019–2022; work order data is 2023–2026. Comparison
> across sources must account for this gap.

---

## 4. View 2 — Ward Explorer

**Purpose:** Let a user select a ward and see all cases, enrichment data, and work orders
for that ward.

### Layout

- Left sidebar: alphabetical ward list (all distinct `primary_ward_name` values) with case count badge
- Right: ward detail panel

### Ward Detail Panel

When a ward is selected, show:

**Sub-panel 4.1 — Ward Summary Cards**
- Total cases in ward
- HIGH / MEDIUM / LOW counts
- Total complaints across all ward cases
- Ward join confidence (show `exact_name`, `fuzzy_name`, or `none` badge)
- Ward pothole complaints 2022 (from first case's ward evidence)
- Road/infrastructure spend (from first case's ward evidence, in crore INR)

**Sub-panel 4.2 — Ward Case Table**

Sortable table of all cases in the ward. Columns:
`Case ID | Priority Tier | Score | Subcategory | Complaints | Unresolved % | Years Active | Cluster Method`

Clicking a row navigates to Case Detail view.

**Sub-panel 4.3 — Work Order Summary**

If `road_work_order_count > 0` for cases in this ward, show:
- Total work orders found in ward (sum across cases, deduplicated by ward)
- Total sanctioned amount (₹ crore)
- Financial years covered

Include disclaimer: *"Work orders listed are for the ward as a whole. The pipeline does not
establish a direct causal link between any specific work order and any specific complaint cluster."*

**Sub-panel 4.4 — Ward Join Quality Note**

If any case in the ward has `ward_join_confidence=fuzzy_name`, show:
> ⚠️ Ward enrichment for this ward used fuzzy name matching. Verify independently before citing
> in formal documents.

If `ward_join_confidence=none`, show:
> ⚠️ No ward enrichment data could be matched for this ward. Work order and crash data are
> not shown.

---

## 5. View 3 — Case List

**Purpose:** Sortable, filterable table of all 298 cases. The analyst's main working surface.

### Filter Controls

| Filter | Type | Options |
|---|---|---|
| Priority Tier | Multi-select chips | HIGH, MEDIUM, LOW |
| Ward | Searchable dropdown | All 60+ distinct ward names |
| Subcategory | Multi-select | Top 10 subcategories |
| Unresolved % | Range slider | 0–100 |
| Complaints | Range slider | 3–103 |
| Years Active | Checkbox | 2, 3, 4 |
| Cluster Method | Toggle | geo_dbscan / ward_temporal |
| Ward Join | Multi-select | exact_name / fuzzy_name / none |

### Table Columns

| Column | Source field | Sortable |
|---|---|---|
| Priority | `priority_tier` + `priority_score` | ✅ |
| Case ID | `case_id` | ✅ |
| Problem | `problem_title` (truncated to 50 chars) | — |
| Ward | `primary_ward_name` | ✅ |
| Complaints | `complaint_count` | ✅ |
| Unresolved | `unresolved_rate_pct` | ✅ |
| Re-opened | `reopened_count` | ✅ |
| Years | `years_active` (badges) | ✅ |
| Cluster | `cluster_method` icon | — |
| Join | `ward_join_confidence` badge | ✅ |

**Default sort:** `priority_score` descending.

**Row click:** Opens Case Detail view.

**Export:** "Download CSV" button exports currently filtered cases as CSV.

---

## 6. View 4 — Case Detail

**Purpose:** Full civic intelligence dossier for a single case. Designed for deep investigation.

### Layout: Two-column (60% / 40%)

#### Left column — Case Content

**Section 6.1 — Header**
- Large: `problem_title`
- Sub: `ward_name` | `date_first_complaint` – `date_last_complaint`
- Priority badge (HIGH / MEDIUM / LOW) with score number
- Cluster method badge (Geo Cluster / Ward Temporal)

**Section 6.2 — Problem Summary**
Full text of `problem_summary`. No truncation.

**Section 6.3 — Complaint Timeline**
Small bar chart: X = year, Y = complaint count (from `complaint_chronology`).
Example for CASE-GEO-0044 (Begur): 2019=28, 2020=14, 2021=10, 2022=4.

**Section 6.4 — Evidence Items**
Numbered list. For each item in `evidence_items`:
- Type badge (complaint_volume / ward_data / work_orders / crash_data)
- Description text
- Source: `traceable_to` shown as a small chip

If type is `ward_data` or `work_orders` and `ward_join_confidence=fuzzy_name`, show
⚠️ fuzzy join indicator next to the evidence item.

**Section 6.5 — Hypotheses**
If `hypotheses` list is non-empty, render in a visually distinct amber/yellow callout box:
> 🔬 HYPOTHESIS (unverified) — [text]

Never show hypotheses without this callout styling.

**Section 6.6 — Recommended Next Steps**
Numbered list from `recommended_next_steps`.

**Section 6.7 — Representative Complaints**
Table with columns: `complaint_id | date | subcategory | status | description_excerpt`.
Show up to 5 rows (the stored representative complaints).
Below the table: note stating *"Showing 5 representative complaints. Full complaint list
requires pipeline re-run with complaint_ids export (see Gap G1 in sprint3_audit_report.md)."*

#### Right column — Sidebar

**Section 6.8 — Key Numbers**
Compact grid of KPI cards:
- Complaints: `complaint_count`
- Open: `open_count`
- Resolved: `resolved_count`
- Re-opened: `reopened_count`
- Unresolved: `unresolved_rate_pct`%
- Years active: `years_active` as badges

**Section 6.9 — Priority Factors**
Horizontal bar chart of `priority_factors`:
- complaint_volume
- recurrence_years
- unresolved_rate
- reopened_rate
- crash_risk
- description_severity

Each bar coloured by weight (darker = higher weight). Exact factor scores shown.

**Section 6.10 — Map (GPS cases only)**
If `centroid_lat` / `centroid_lon` available and `cluster_method=geo_dbscan`:
- Static OpenStreetMap tile (Leaflet.js or static image) centred on centroid
- Single marker at centroid
- Note: *"Map shows cluster centroid. The cluster has {geographic_extent_km:.1f} km bounding box."*

If `cluster_method=ward_temporal`:
- Show ward name text instead of map; note that GPS coordinates are ward-averaged

**Section 6.11 — Ward Enrichment Panel**

Labelled section: *"Ward: {primary_ward_name} (datameet243 join confidence: {ward_join_confidence})"*

| Metric | Value | Source |
|---|---|---|
| Pothole complaints (2022) | `ward_pothole_count_2022` or N/A | KAUN ward metrics |
| Road/infra spend | `ward_road_spending_inr` ÷ 1e7 crore or N/A | KAUN ward metrics |
| Work orders (road/drain) | `road_work_order_count` | KAUN work orders |
| Work order total | ₹X crore | KAUN work orders |
| Financial years | list | KAUN work orders |
| Road crashes (2024) | `ward_road_crashes_2024` or N/A | KAUN ward metrics |
| Fatal crashes (2024) | `ward_fatal_crashes_2024` or N/A | KAUN ward metrics |

If `ward_join_confidence=none`: show *"No ward enrichment data available for this case."*
If `ward_join_confidence=fuzzy_name`: show ⚠️ above the table.

**Section 6.12 — Responsible Agency**
- Agency: `responsible_agency`
- Confidence: `agency_confidence` badge
- Note: `agency_attribution_note`

---

## 7. Data Contract — What the Dashboard Reads

The dashboard reads **only** from `data/processed/civic_cases.json`. It does not read raw
data files, work order JSON, or ward metrics CSV directly.

All fields that the dashboard depends on, with their actual types from the pipeline:

| Field | Type | Notes |
|---|---|---|
| `case_id` | string | e.g. "CASE-GEO-0044" |
| `cluster_id` | string | e.g. "GEO-0044" |
| `cluster_method` | string | "geo_dbscan" or "ward_temporal" |
| `problem_title` | string | ≤ 80 chars |
| `problem_summary` | string | 2–4 sentences |
| `problem_category` | string | "road_infrastructure" for all 298 cases |
| `representative_subcategory` | string | e.g. "Fixing/Reparing Potholes" |
| `complaint_count` | int | 3–103 |
| `unique_ward_count` | int | usually 1 |
| `date_first_complaint` | ISO date string | YYYY-MM-DD |
| `date_last_complaint` | ISO date string | YYYY-MM-DD |
| `years_active` | list[int] | e.g. [2019, 2020, 2021, 2022] |
| `complaint_chronology` | list[{year, count}] | for timeline chart |
| `primary_ward_name` | string or null | null for 11 ward_id=199 cases |
| `primary_ward_id` | int or null | ICMC ward_id |
| `all_ward_names` | list[string] | |
| `centroid_lat` | float or null | WGS84 |
| `centroid_lon` | float or null | WGS84 |
| `geographic_extent_km` | float or null | bounding box diagonal; some ward-temporal cases have inflated values |
| `open_count` | int | |
| `resolved_count` | int | |
| `reopened_count` | int | |
| `unresolved_rate_pct` | float | 0–100 |
| `evidence_items` | list[{type, description, source, traceable_to}] | 2–6 items |
| `hypotheses` | list[string] | 0–2 items; explicitly labelled in text |
| `responsible_agency` | string | "BBMP" for all 298 |
| `agency_confidence` | string | "direct" for all 298 |
| `agency_attribution_note` | string | |
| `priority_tier` | string | "HIGH", "MEDIUM", "LOW" |
| `priority_score` | float | 0.147–0.610 |
| `priority_factors` | dict[str, float] | 6 factor scores |
| `priority_rationale` | string | |
| `cluster_confidence` | float | |
| `clustering_reasons` | list[string] | |
| `ward_join_confidence` | string | "exact_name", "fuzzy_name", "none" |
| `ward_join_note` | string | Full join explanation |
| `recommended_next_steps` | list[string] | 1–4 items |
| `representative_complaints` | list[{complaint_id, created_at, ward_name, subcategory, status, description_excerpt, latitude, longitude}] | up to 5 |
| `generated_at` | ISO datetime string | |

---

## 8. Missing Fields (Sprint 4 work items)

| Missing Field | Needed For | Sprint 4 Action |
|---|---|---|
| `complaint_ids` | Evidence traceability in Case Detail | Add to `CivicCase`; expose in JSON |
| GPS points of all cluster members | Accurate cluster map | Store `complaint_gps_points` list |
| `ward_road_crashes_2024` on case (not just in evidence_items) | Priority factors sidebar | Expose as top-level field |
| `work_order_ids` list per case | Work order deep-dive | Store in case JSON |

---

## 9. Implementation Notes

### Technology
The POC dashboard is a **single-file static HTML** (no build toolchain) generated by a
Python script from `civic_cases.json`. Libraries loaded from CDN:

- **Chart.js 4.x** — bar charts, donut, histogram
- **Leaflet.js 1.9.x** — map tiles for Case Detail GPS view  
- **OpenStreetMap tiles** — free, no API key
- **Tabulator.js 6.x** (or simple HTML table) — sortable filterable case list

### Generation
Script: `scripts/generate_dashboard.py`  
Output: `dashboard/index.html`  

The script embeds the full `civic_cases.json` as a JavaScript variable inside the HTML file,
so the dashboard is fully self-contained and openable from the filesystem without a web server.

### No LLM
The dashboard does not call any LLM. All text (titles, summaries, evidence, hypotheses) was
generated deterministically by the pipeline at case generation time.

---

## 10. What the Dashboard Does NOT Show

The following are explicitly out of scope for the POC dashboard:

- Real-time complaint feeds (data is static 2019–2022)
- Individual citizen identities or contact details
- Contractor names or blacklist flags (available in work order data but excluded from pipeline
  outputs per design constraint)
- Deduction percentages from work orders (available in source data, excluded per design constraint)
- Any inferences not explicitly derived from pipeline outputs
- OpenCity road network layer (not yet integrated into pipeline)
- Photo or media attachments (not in source data)

---

*Dashboard specification grounded in `civic_cases.json` (298 cases, 2026-11-24 post-fix run).*  
*All numbers are actual pipeline outputs, not estimates or hypothetical values.*
