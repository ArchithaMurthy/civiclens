# CivicLens Bengaluru — Source Manifest

> Sprint 1 Data Acquisition  
> Download date: 2026-11-23  
> All files preserved in `data/raw/` without modification.

---

## Successfully Acquired Datasets

### 1. I Change My City — Bengaluru Civic Complaints (2019–2021)

| Field | Detail |
|---|---|
| **Source name** | I Change My City (ichangemycity.com) by Janaagraha |
| **Origin platform** | OpenCity (data.opencity.in) |
| **Acquisition path** | GitHub mirror: `pr4navvvv/blr-civic-complaints-analysis` |
| **Direct URL** | https://raw.githubusercontent.com/pr4navvvv/blr-civic-complaints-analysis/main/5f99b09a-64b5-45f0-ab18-4cf0a0cabf6d.csv |
| **OpenCity canonical URL** | https://data.opencity.in/dataset/i-change-my-city-data/resource/a60abf5c-3a15-4967-af32-c3074248580f |
| **Local path** | `data/raw/ichangemycity_complaints.csv` |
| **Download date** | 2026-11-23 |
| **Format** | CSV, cp1252 encoding |
| **File size** | 8,377,752 bytes (8.0 MB) |
| **Row count** | 16,071 |
| **Columns** | 17 |
| **Date range** | January 2019 – September 2021 |
| **Geographic coverage** | 198 wards, full BBMP area (lat 12.71–13.18, lon 77.43–77.81) |
| **GPS completeness** | 100% (16,071 / 16,071 records have lat/lon) |
| **License** | Creative Commons — data sourced via OpenCity (open data platform) |
| **Attribution** | "Data sourced from I Change My City (ichangemycity.com) via OpenCity (opencity.in)" |
| **POC suitability** | ⭐⭐⭐⭐⭐ — primary complaint dataset |
| **Notes** | 44.8% missing `address` field; 4.1% missing `civic_agency_title`; date format inconsistent across rows |

---

### 2. KAUN Bengaluru — Ward Metrics (2022–2025)

| Field | Detail |
|---|---|
| **Source name** | KAUN Bengaluru (bengaluru.kaun.city) |
| **URL** | https://bengaluru.kaun.city/api/export?type=all |
| **Local path** | `data/raw/kaun_ward_metrics.csv` |
| **Download date** | 2026-11-23 |
| **Format** | CSV, UTF-8 |
| **File size** | 62,363 bytes (60.9 KB) |
| **Row count** | 254 (243 BBMP wards + 11 extended/citywide) |
| **Columns** | 44 |
| **Key fields** | `pothole_complaints` (2022 data), `road_crashes_2024/2025`, `fatal_crashes_2024/2025`, `spend_*` (2018–2023), `ac_road_length_km`, `ac_streetlights`, `total_work_orders` |
| **Date range** | Spending: 2018–2023; Potholes: 2022; Crashes: 2024–2025 |
| **Geographic coverage** | 243 Bengaluru wards |
| **License** | MIT licensed platform; public government data |
| **Attribution** | "Data sourced from KAUN Bengaluru (bengaluru.kaun.city)" |
| **POC suitability** | ⭐⭐⭐⭐ — excellent enrichment dataset; ward-level aggregates |
| **Notes** | `zone` field is empty for all 243 wards (not populated at time of download); road crash data covers only 58 wards |

---

### 3. KAUN Bengaluru — Work Orders (All Wards, 2024–2025)

| Field | Detail |
|---|---|
| **Source name** | KAUN Bengaluru — BBMP work orders via opencity.in |
| **URL** | https://kaun.city/api/data/spending?ward=N&type=work-orders (fetched for all 243 wards) |
| **Local path** | `data/raw/kaun_work_orders_all_wards.json` |
| **Download date** | 2026-11-23 |
| **Format** | JSON |
| **File size** | 10,750,704 bytes (10.3 MB) |
| **Record count** | 11,072 work orders |
| **Key fields** | `work_order_id`, `ward_no`, `ward_class`, `description`, `contractor_name`, `contractor_phone`, `sanctioned_amount`, `net_paid`, `deduction`, `fy`, `data_source` |
| **Date range** | FY 2024–25 (primary) |
| **Geographic coverage** | 243 wards (50 work orders per ward max per API call) |
| **License** | MIT licensed platform; public government data |
| **Attribution** | "Data sourced from KAUN Bengaluru (kaun.city) via BBMP/opencity.in" |
| **POC suitability** | ⭐⭐⭐⭐ — road/drain/infrastructure work orders with contractor accountability |
| **Notes** | API caps at 50 records per ward; `start_date`/`end_date` missing for most records; `ward_class = "citywide"` for 304+ ward class entries |

---

### 4. KAUN Bengaluru — Ward List JSON

| Field | Detail |
|---|---|
| **Source name** | KAUN Bengaluru — ward name reference |
| **URL** | https://kaun.city/api/data/wards |
| **Local path** | `data/raw/kaun_wards.json` |
| **Download date** | 2026-11-23 |
| **Format** | JSON |
| **File size** | 23,219 bytes |
| **Record count** | 243 wards |
| **Key fields** | `ward_no`, `ward_name`, `assembly_constituency`, `zone` |
| **License** | MIT licensed platform |
| **Attribution** | "Data sourced from KAUN Bengaluru (kaun.city)" |
| **POC suitability** | ⭐⭐⭐⭐ — ward name lookup / join key |
| **Notes** | `zone` is null for all records |

---

### 5. KAUN Bengaluru — Ward Crosswalk CSV

| Field | Detail |
|---|---|
| **Source name** | KAUN Bengaluru — BBMP 2023 (225 wards) to Datameet (243 wards) crosswalk |
| **URL** | https://data.kaun.city/bengaluru/ward-crosswalk/bbmp2023_225_to_datameet_243.csv |
| **Local path** | `data/raw/kaun_ward_crosswalk.csv` |
| **Download date** | 2026-11-23 |
| **Format** | CSV, UTF-8 |
| **File size** | 38,621 bytes |
| **Row count** | 225 |
| **Key fields** | `bbmp225_no`, `bbmp225_name_en`, `bbmp225_name_ka`, `assembly_constituency`, `population`, `datameet243_no`, `datameet243_name`, `overlap_confidence` |
| **License** | Open data, MIT licensed platform |
| **Attribution** | "Data sourced from KAUN Bengaluru (data.kaun.city)" |
| **POC suitability** | ⭐⭐⭐ — essential for ward ID reconciliation across datasets |
| **Notes** | Maps between different BBMP ward numbering systems (pre/post 2020 delimitation) |

---

### 6. KAUN Bengaluru — Ward Crosswalk JSON (Full)

| Field | Detail |
|---|---|
| **Source name** | KAUN Bengaluru — ward crosswalk with Kannada names and geometry metadata |
| **URL** | https://data.kaun.city/bengaluru/ward-crosswalk/bbmp2023_225_to_datameet_243.json |
| **Local path** | `data/raw/kaun_ward_crosswalk.json` |
| **Format** | JSON |
| **File size** | 158,417 bytes |
| **License** | Open data, MIT licensed platform |
| **POC suitability** | ⭐⭐⭐ — richer version of crosswalk CSV |

---

### 7. KAUN Bengaluru — Contractors

| Field | Detail |
|---|---|
| **Source name** | KAUN Bengaluru — BBMP contractor registry |
| **URL** | https://kaun.city/api/data/contractors?limit=1000 |
| **Local path** | `data/raw/kaun_contractors.json` |
| **Format** | JSON |
| **File size** | 186,066 bytes |
| **Record count** | ~350 contractors |
| **Key fields** | `entity_id`, `canonical_name`, `phone`, `total_contracts`, `total_value_lakh`, `avg_deduction_pct`, `ward_count`, `wards`, `blacklist_flags` |
| **License** | MIT licensed platform; public government data |
| **Attribution** | "Data sourced from KAUN Bengaluru (kaun.city)" |
| **POC suitability** | ⭐⭐⭐ — useful for agency accountability investigations |

---

### 8. KAUN Bengaluru — Elected Representatives (MLA)

| Field | Detail |
|---|---|
| **Source name** | KAUN Bengaluru — MLA data with report cards |
| **URL** | https://kaun.city/api/data/reps?role=MLA |
| **Local path** | `data/raw/kaun_reps_mla.json` |
| **Format** | JSON |
| **File size** | 18,376 bytes |
| **Key fields** | `role`, `constituency`, `name`, `party`, `phone`, `report_card.attendance_pct`, `report_card.questions_asked` |
| **License** | MIT licensed platform |
| **POC suitability** | ⭐⭐ — useful for dossier escalation pathway |

---

### 9. CivicIssue / GovWatch — Issues JSON (Filtered)

| Field | Detail |
|---|---|
| **Source name** | GovWatch by ishanfso — Bengaluru civic issues from Twitter/X (2026) |
| **URL** | https://raw.githubusercontent.com/ishanfso/GovWatch/main/data/issues.json |
| **Local path** | `data/raw/civicissue_issues.json` |
| **Format** | JSON |
| **File size** | 677,496 bytes |
| **Record count** | 1,012 |
| **Date range** | May 2026 – July 2026 |
| **Key fields** | `id`, `text`, `author`, `date`, `category`, `area`, `ward_name`, `ward_no`, `severity`, `likes`, `retweets`, `source_url`, `status` |
| **License** | AGPLv3 (platform code); data sourced from public Twitter posts |
| **Attribution** | "Data sourced from GovWatch (civicissue.in / github.com/ishanfso/GovWatch)" |
| **POC suitability** | ⭐⭐⭐⭐ — recent (2026) real complaints with text; complements 2019–2021 historical data |
| **Notes** | Only 114/1012 records have ward_no; all records are from Twitter/X; primary category is Electricity (40.7%) then Waste (33.8%) |

---

### 10. CivicIssue / GovWatch — Issues JSON (Unfiltered)

| Field | Detail |
|---|---|
| **Source name** | GovWatch — unfiltered/all collected tweets |
| **URL** | https://raw.githubusercontent.com/ishanfso/GovWatch/main/data/issues_unfiltered.json |
| **Local path** | `data/raw/civicissue_issues_unfiltered.json` |
| **Format** | JSON |
| **File size** | 3,349,647 bytes (3.2 MB) |
| **Record count** | 4,989 |
| **Date range** | May 2026 – July 2026 |
| **POC suitability** | ⭐⭐⭐ — larger corpus but includes non-complaint content |

---

### 11. CivicIssue / GovWatch — Tweet Analysis CSV

| Field | Detail |
|---|---|
| **Source name** | GovWatch — human-labelled tweet verdicts with LLM accuracy scores |
| **URL** | https://raw.githubusercontent.com/ishanfso/GovWatch/main/govwatch_tweet_analysis.csv |
| **Local path** | `data/raw/civicissue_tweet_analysis.csv` |
| **Format** | CSV |
| **File size** | 156,275 bytes |
| **Row count** | 338 |
| **Key fields** | `tweet_id`, `category`, `area`, `likes`, `retweets`, `llm_verdict`, `my_verdict`, `tweet_type`, `theme`, `llm_accuracy`, `notes`, `text`, `author` |
| **POC suitability** | ⭐⭐⭐ — LLM-labelled ground truth; useful for classifier evaluation |

---

### 12. KAUN Bengaluru — Budget Work Orders (Citywide Sample)

| Field | Detail |
|---|---|
| **Source name** | KAUN Bengaluru — citywide work order sample |
| **URL** | https://kaun.city/api/data/spending?type=work-orders |
| **Local path** | `data/raw/kaun_work_orders.json` |
| **Format** | JSON |
| **File size** | 147,209 bytes |
| **Record count** | 200 (citywide sample only) |
| **POC suitability** | ⭐⭐ — superseded by `kaun_work_orders_all_wards.json` |

---

## Total Acquired

| Metric | Value |
|---|---|
| **Files in data/raw/** | 12 datasets |
| **Total download size** | ~24 MB |
| **Real complaint records** | 16,071 (I Change My City) + 1,012 (GovWatch) = **17,083** |
| **Work order records** | 11,072 |
| **Ward reference records** | 243 wards (KAUN) + 225 ward crosswalk |
| **Date coverage** | Jan 2019 – Jul 2026 (complaint data) |
| **Geographic coverage** | 198–243 Bengaluru wards; full BBMP jurisdiction |
