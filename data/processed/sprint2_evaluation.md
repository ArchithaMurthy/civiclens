# CivicLens Sprint 2 — Pipeline Evaluation Report

> **Methodology:** Quantitative checks on structure and coverage. No accuracy claims are made without manual verification. Human-review samples are exported for independent inspection.

---

## 1. Pipeline Summary

| Metric | Value |
|---|---|
| Total civic cases generated | 298 |
| HIGH priority | 15 |
| MEDIUM priority | 172 |
| LOW priority | 111 |
| Total complaints in cases | 3,895 |
| Total dedup candidate pairs | 16,513 |
| Exact duplicate pairs | 163 |
| Near-duplicate pairs | 689 |

## 2. Duplicate Detection Quality

### Methodology
Duplicates are detected using a rule-based approach combining: text fingerprint identity, geographic proximity (≤200m), temporal proximity (≤7 days), and subcategory match. No LLM used. Confidence scores are based on signal combinations.

### Confidence score distribution (all candidate pairs)

| Confidence range | Count |
|---|---|
| 0.80–1.00 | 605 |
| 0.60–0.79 | 822 |
| 0.40–0.59 | 2,775 |
| 0.00–0.39 | 12,311 |

### Signal distribution (exact duplicates)

| Signal | Count in exact dups |
|---|---|
| `same_category` | 163 |
| `identical_description` | 163 |
| `same_source` | 163 |
| `within_3_days` | 159 |
| `same_subcategory` | 155 |
| `gps_within_50m` | 100 |
| `gps_within_200m` | 20 |
| `within_7_days` | 4 |

> **Limitation:** No ground-truth label set exists. The 163 'exact duplicate' pairs all share identical descriptions + same ward + within 7 days — these are very likely true duplicates but cannot be confirmed without manual review. See `dedup_sample_review.csv` for 20 randomly selected pairs.

## 3. Cluster Coherence

| Cluster type | Count | Avg complaints | Avg confidence |
|---|---|---|---|
| geo_dbscan | 189 | 13.6 | 0.75 |
| ward_temporal | 109 | 12.2 | 0.54 |

### Geographic extent (geo_dbscan clusters)
- Min extent: 0.091 km
- Max extent: 1.999 km
- Mean extent: 0.745 km
- Clusters with extent < 0.5km: 59 (31%)
- Clusters with extent 0.5–1.0km: 89
- Clusters with extent 1.0–2.0km: 41

> **Known limitation:** Geo clusters with large extents (>1km) may contain complaints about different road segments within the same neighbourhood. These are marked as lower confidence and require field verification.

## 4. Geographic Validity

- ICMC complaints with GPS within BBMP bounding box: 16,071 / 16,071 (100%)
- BBMP bounding box used: Lat 12.70–13.20, Lon 77.40–77.85
- GovWatch complaints with GPS: 0 (source has no GPS data)

- Cases with centroid GPS: 298
- Cases with centroid outside BBMP bounds: 0 (expected: 0)

## 5. Ward Mapping Confidence

| Join type | Count |
|---|---|
| Crosswalk (bbmp225 → datameet243) | 298 |
| Approximate (direct ID match) | 0 |
| No ward ID available | 0 |

> **Important:** ICMC ward_id (1–198) ≈ datameet243 ward no for the same range but is not guaranteed identical. All work order and ward metric joins are approximate unless the crosswalk CSV confirms the mapping. Evidence items explicitly record join quality.

## 6. Case Quality Indicators

### Evidence traceability
- Total evidence items across all cases: 1554
- Average evidence items per case: 5.2
- Cases with ward metrics evidence: 298
- Cases with work order evidence: 298
- Cases with road crash evidence: 64

### Agency attribution confidence
- Direct (≥80% complaints name agency): 298
- Inferred (majority, <80%): 0
- Unknown: 0

### Case completeness checklist

| Check | Cases passing | % |
|---|---|---|
| Has problem_title | 298 | 100% |
| Has problem_summary | 298 | 100% |
| Has date_first_complaint | 298 | 100% |
| Has primary_ward_name | 298 | 100% |
| Has responsible_agency | 298 | 100% |
| Has >=1 evidence items | 298 | 100% |
| Has >=1 next steps | 298 | 100% |
| Has representative complaints | 298 | 100% |
| Has complaint_chronology | 298 | 100% |

## 7. Sample Cases (Top 5 HIGH Priority)

### CASE-GEO-0044
**Recurring Fixing/Reparing Potholes — Begur (2019–2022)**
- Complaints: 56 | Unresolved: 50.0%
- Years active: [2019, 2020, 2021, 2022]
- Priority score: 0.624
- Agency: BBMP (direct attribution)
- Summary: 56 citizen complaints about 'Fixing/Reparing Potholes' were recorded in Begur between January 2019 and April 2022, spanning 4 calendar year(s). 50% of these complaints remain unresolved (status: Open or Re-opened). 4 complaint(s) were re-opened after initially being resolved. 

**Evidence:**
- [complaint_volume] 56 complaints recorded in source dataset.
- [complaint_status] Status distribution: Open=28, Resolved=13, Re-opened=4.
- [ward_pothole_data] KAUN 2022 data: ward recorded 58 pothole complaints.
- [ward_road_spending] Ward road/infrastructure spending: ₹12.8 crore (2018-2023).
- [work_orders_in_ward] 42 road/drain work order(s) sanctioned in ward (₹94.6 crore, FY 2023-24, 2024-25, 2025-26). Note: work order ward mapping uses datameet243 numbering (crosswalk join).
- [road_crash_data] Ward recorded 110 road crashes in 2024, of which 20 were fatal.

**Hypotheses (explicitly labelled as unverified):**
- HYPOTHESIS (unverified): Road work contracts exist in this ward, yet 50% of complaints remain unresolved. This may indicate that repairs were incomplete, inadequate, or that the work was performed in different road segments. Independent verification required.
- HYPOTHESIS (unverified): 4 complaint(s) were re-opened after being marked resolved. This may indicate short-term or superficial repairs that did not address the underlying problem.

### CASE-GEO-0034
**Recurring Fixing/Reparing Potholes — Varthur (2019–2022)**
- Complaints: 103 | Unresolved: 50.5%
- Years active: [2019, 2020, 2021, 2022]
- Priority score: 0.610
- Agency: BBMP (direct attribution)
- Summary: 103 citizen complaints about 'Fixing/Reparing Potholes' were recorded in Varthur between January 2019 and August 2022, spanning 4 calendar year(s). 50% of these complaints remain unresolved (status: Open or Re-opened). 

**Evidence:**
- [complaint_volume] 103 complaints recorded in source dataset.
- [complaint_status] Status distribution: Open=52, Resolved=25, Re-opened=0.
- [ward_pothole_data] KAUN 2022 data: ward recorded 44 pothole complaints.
- [ward_road_spending] Ward road/infrastructure spending: ₹20.4 crore (2018-2023).
- [work_orders_in_ward] 39 road/drain work order(s) sanctioned in ward (₹56.9 crore, FY 2023-24, 2024-25, 2025-26). Note: work order ward mapping uses datameet243 numbering (crosswalk join).

**Hypotheses (explicitly labelled as unverified):**
- HYPOTHESIS (unverified): Road work contracts exist in this ward, yet 50% of complaints remain unresolved. This may indicate that repairs were incomplete, inadequate, or that the work was performed in different road segments. Independent verification required.

### CASE-WARD-150-FIXINGR
**Recurring Fixing/Reparing Potholes — Bellanduru (2019–2022)**
- Complaints: 100 | Unresolved: 27.0%
- Years active: [2019, 2020, 2021, 2022]
- Priority score: 0.574
- Agency: BBMP (direct attribution)
- Summary: 100 citizen complaints about 'Fixing/Reparing Potholes' were recorded in Bellanduru between January 2019 and May 2022, spanning 4 calendar year(s). 27% of these complaints remain unresolved (status: Open or Re-opened). 2 complaint(s) were re-opened after initially being resolved. 

**Evidence:**
- [complaint_volume] 100 complaints recorded in source dataset.
- [complaint_status] Status distribution: Open=27, Resolved=60, Re-opened=2.
- [ward_pothole_data] KAUN 2022 data: ward recorded 53 pothole complaints.
- [ward_road_spending] Ward road/infrastructure spending: ₹10.9 crore (2018-2023).
- [work_orders_in_ward] 40 road/drain work order(s) sanctioned in ward (₹87.6 crore, FY 2024-25, 2025-26). Note: work order ward mapping uses datameet243 numbering (crosswalk join).

**Hypotheses (explicitly labelled as unverified):**
- HYPOTHESIS (unverified): 2 complaint(s) were re-opened after being marked resolved. This may indicate short-term or superficial repairs that did not address the underlying problem.

### CASE-WARD-192-FIXINGR
**Recurring Fixing/Reparing Potholes — Begur (2019–2022)**
- Complaints: 38 | Unresolved: 31.6%
- Years active: [2019, 2020, 2021, 2022]
- Priority score: 0.568
- Agency: BBMP (direct attribution)
- Summary: 38 citizen complaints about 'Fixing/Reparing Potholes' were recorded in Begur between January 2019 and March 2022, spanning 4 calendar year(s). 32% of these complaints remain unresolved (status: Open or Re-opened). 2 complaint(s) were re-opened after initially being resolved. 

**Evidence:**
- [complaint_volume] 38 complaints recorded in source dataset.
- [complaint_status] Status distribution: Open=12, Resolved=13, Re-opened=2.
- [ward_pothole_data] KAUN 2022 data: ward recorded 58 pothole complaints.
- [ward_road_spending] Ward road/infrastructure spending: ₹12.8 crore (2018-2023).
- [work_orders_in_ward] 42 road/drain work order(s) sanctioned in ward (₹94.6 crore, FY 2023-24, 2024-25, 2025-26). Note: work order ward mapping uses datameet243 numbering (crosswalk join).
- [road_crash_data] Ward recorded 110 road crashes in 2024, of which 20 were fatal.

**Hypotheses (explicitly labelled as unverified):**
- HYPOTHESIS (unverified): 2 complaint(s) were re-opened after being marked resolved. This may indicate short-term or superficial repairs that did not address the underlying problem.

### CASE-GEO-0090
**Recurring Fixing/Reparing Potholes — Begur (2019–2022)**
- Complaints: 38 | Unresolved: 55.3%
- Years active: [2019, 2020, 2021, 2022]
- Priority score: 0.567
- Agency: BBMP (direct attribution)
- Summary: 38 citizen complaints about 'Fixing/Reparing Potholes' were recorded in Begur between January 2019 and January 2022, spanning 4 calendar year(s). 55% of these complaints remain unresolved (status: Open or Re-opened). 1 complaint(s) were re-opened after initially being resolved. 

**Evidence:**
- [complaint_volume] 38 complaints recorded in source dataset.
- [complaint_status] Status distribution: Open=21, Resolved=11, Re-opened=1.
- [ward_pothole_data] KAUN 2022 data: ward recorded 58 pothole complaints.
- [ward_road_spending] Ward road/infrastructure spending: ₹12.8 crore (2018-2023).
- [work_orders_in_ward] 42 road/drain work order(s) sanctioned in ward (₹94.6 crore, FY 2023-24, 2024-25, 2025-26). Note: work order ward mapping uses datameet243 numbering (crosswalk join).
- [road_crash_data] Ward recorded 110 road crashes in 2024, of which 20 were fatal.

**Hypotheses (explicitly labelled as unverified):**
- HYPOTHESIS (unverified): Road work contracts exist in this ward, yet 55% of complaints remain unresolved. This may indicate that repairs were incomplete, inadequate, or that the work was performed in different road segments. Independent verification required.
- HYPOTHESIS (unverified): 1 complaint(s) were re-opened after being marked resolved. This may indicate short-term or superficial repairs that did not address the underlying problem.

## 8. Known Limitations and Risks

| Risk | Description | Mitigation |
|---|---|---|
| **Data staleness** | ICMC data ends Sep 2021. Pipeline cannot reflect current road conditions. | Noted in all case summaries; requires newer data for operational use. |
| **Ward numbering mismatch** | ICMC ward_ids (1–198) ≈ datameet243 but not identical. | Crosswalk used; join confidence documented per case. |
| **False merges (geo clusters)** | DBSCAN with 300m radius may merge adjacent-road complaints. | Cases with bbox > 1km flagged as lower confidence. |
| **False splits (ward clusters)** | Same physical pothole cluster may appear in two adjacent wards. | Geo clusters run first; ward clustering only on geo-unclustered records. |
| **No complaint IDs in ICMC source** | Cannot definitively deduplicate without stable IDs. | Pipeline IDs assigned; exact dedup uses text fingerprint + GPS + time. |
| **Work order ≠ repair** | A work order being sanctioned does not confirm that repairs occurred or were adequate. | All work order evidence items explicitly note this limitation. |
| **Agency attribution** | 100% of road complaints name BBMP — this reflects source data, not independent verification. | Agency confidence level documented per case. |
