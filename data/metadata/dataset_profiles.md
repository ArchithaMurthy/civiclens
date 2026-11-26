# CivicLens Sprint 1 ΓÇö Dataset Profiles

> Generated: 2026-11-23 15:43:33
> Source directory: `data/raw/`

---

## CSV Datasets


### civicissue_tweet_analysis.csv

| Property | Value |
|---|---|
| **File** | `civicissue_tweet_analysis.csv` |
| **Size** | 156,275 bytes (152.6 KB) |
| **Encoding** | utf-8 |
| **Rows** | 338 |
| **Columns** | 16 |

**Columns:**

- `num` ΓÇö 338 populated (0.0% missing) | 338 distinct values
- `tweet_id` ΓÇö 338 populated (0.0% missing) | 338 distinct values
- `date` ΓÇö 338 populated (0.0% missing) | 8 distinct values
- `category` ΓÇö 338 populated (0.0% missing) | 8 distinct values
- `area` ΓÇö 338 populated (0.0% missing) | 22 distinct values
- `likes` ΓÇö 338 populated (0.0% missing) | 33 distinct values
- `retweets` ΓÇö 338 populated (0.0% missing) | 17 distinct values
- `llm_verdict` ΓÇö 338 populated (0.0% missing) | 2 distinct values
- `my_verdict` ΓÇö 338 populated (0.0% missing) | 3 distinct values
- `tweet_type` ΓÇö 338 populated (0.0% missing) | 14 distinct values
- `theme` ΓÇö 338 populated (0.0% missing) | 16 distinct values
- `llm_accuracy` ΓÇö 338 populated (0.0% missing) | 5 distinct values
- `notes` ΓÇö 338 populated (0.0% missing) | 338 distinct values
- `text` ΓÇö 338 populated (0.0% missing) | 334 distinct values
- `author` ΓÇö 338 populated (0.0% missing) | 275 distinct values
- `source_url` ΓÇö 338 populated (0.0% missing) | 338 distinct values

**Date fields detected:** date, category
- `date` range: `2026-05-10` to `2026-05-17`

**`category` distribution (top 10):**

| Value | Count |
|---|---|
| Waste | 94 |
| Electricity | 61 |
| Traffic | 58 |
| Parks | 46 |
| Water | 42 |
| Roads | 21 |
| Flooding | 15 |
| Other | 1 |

**`tweet_type` distribution (top 10):**

| Value | Count |
|---|---|
| citizen_complaint | 88 |
| civic_commentary | 53 |
| general_discussion | 48 |
| news_media | 38 |
| unrelated | 33 |
| political_content | 25 |
| govt_announcement | 16 |
| civic_watchdog | 11 |
| service_promo | 9 |
| corporate_news | 6 |

**Duplicate IDs (`tweet_id`):** 0

### ichangemycity_complaints.csv

| Property | Value |
|---|---|
| **File** | `ichangemycity_complaints.csv` |
| **Size** | 8,377,752 bytes (8181.4 KB) |
| **Encoding** | utf-8 |
| **Rows** | 16,071 |
| **Columns** | 17 |

**Columns:**

- `created_at` ΓÇö 16,071 populated (0.0% missing) | 15,844 distinct values
- `ward_id` ΓÇö 16,071 populated (0.0% missing) | 198 distinct values
- `title` ΓÇö 16,071 populated (0.0% missing) | 13,582 distinct values
- `description` ΓÇö 16,071 populated (0.0% missing) | 15,377 distinct values
- `sub_category_id` ΓÇö 16,071 populated (0.0% missing) | 211 distinct values
- `civic_agency_id` ΓÇö 15,452 populated (3.9% missing) | 10 distinct values
- `location` ΓÇö 16,071 populated (0.0% missing) | 12,096 distinct values
- `address` ΓÇö 8,878 populated (44.8% missing) | 8,068 distinct values
- `latitude` ΓÇö 16,071 populated (0.0% missing) | 12,936 distinct values
- `longitude` ΓÇö 16,071 populated (0.0% missing) | 12,747 distinct values
- `ward_title` ΓÇö 16,039 populated (0.2% missing) | 198 distinct values
- `category_id` ΓÇö 16,039 populated (0.2% missing) | 43 distinct values
- `category_title` ΓÇö 16,039 populated (0.2% missing) | 43 distinct values
- `sub_category_title` ΓÇö 16,053 populated (0.1% missing) | 220 distinct values
- `civic_agency_title` ΓÇö 15,416 populated (4.1% missing) | 15 distinct values
- `complaint_status_title` ΓÇö 16,071 populated (0.0% missing) | 6 distinct values
- `comment_count` ΓÇö 16,071 populated (0.0% missing) | 45 distinct values

**Date fields detected:** created_at, sub_category_id, location, latitude, category_id, category_title, sub_category_title, complaint_status_title
- `created_at` range: `1-1-2019 06:33` to `9/30/2021 8:40`

**`ward_id` distribution (top 10):**

| Value | Count |
|---|---|
| 150 | 727 |
| 199 | 637 |
| 192 | 535 |
| 25 | 507 |
| 6 | 365 |
| 85 | 350 |
| 149 | 324 |
| 174 | 292 |
| 191 | 280 |
| 26 | 255 |

**`sub_category_id` distribution (top 10):**

| Value | Count |
|---|---|
| 155 | 3,110 |
| 66 | 2,247 |
| 67 | 1,623 |
| 62 | 1,294 |
| 77 | 770 |
| 442 | 361 |
| 42 | 346 |
| 709 | 265 |
| 352 | 260 |
| 46 | 253 |

**`civic_agency_id` distribution (top 10):**

| Value | Count |
|---|---|
| 10 | 12,944 |
| 5 | 970 |
| 2 | 659 |
| NULL | 619 |
| 7 | 437 |
| 1 | 241 |
| 4 | 146 |
| 8 | 37 |
| 11 | 10 |
| 15 | 4 |

**Geographic coverage:**
- Latitude: 12.7123 to 13.1828
- Longitude: 77.4309 to 77.8094
- Records with valid GPS: 16,071 / 16,071

### kaun_ward_crosswalk.csv

| Property | Value |
|---|---|
| **File** | `kaun_ward_crosswalk.csv` |
| **Size** | 38,621 bytes (37.7 KB) |
| **Encoding** | utf-8 |
| **Rows** | 225 |
| **Columns** | 16 |

**Columns:**

- `bbmp225_no` ΓÇö 225 populated (0.0% missing) | 225 distinct values
- `bbmp225_name_en` ΓÇö 225 populated (0.0% missing) | 225 distinct values
- `bbmp225_name_ka` ΓÇö 225 populated (0.0% missing) | 225 distinct values
- `assembly_constituency` ΓÇö 225 populated (0.0% missing) | 28 distinct values
- `population` ΓÇö 225 populated (0.0% missing) | 223 distinct values
- `datameet243_no` ΓÇö 225 populated (0.0% missing) | 206 distinct values
- `datameet243_name` ΓÇö 225 populated (0.0% missing) | 206 distinct values
- `lgd_ward_code` ΓÇö 186 populated (17.3% missing) | 169 distinct values
- `overlap_confidence` ΓÇö 225 populated (0.0% missing) | 182 distinct values
- `tier` ΓÇö 225 populated (0.0% missing) | 3 distinct values
- `runner_up_243_no` ΓÇö 211 populated (6.2% missing) | 148 distinct values
- `runner_up_share` ΓÇö 225 populated (0.0% missing) | 204 distinct values
- `outside_share` ΓÇö 225 populated (0.0% missing) | 7 distinct values
- `split` ΓÇö 225 populated (0.0% missing) | 225 distinct values
- `samples` ΓÇö 225 populated (0.0% missing) | 99 distinct values
- `method` ΓÇö 225 populated (0.0% missing) | 1 distinct values

**Date fields detected:** population, datameet243_no, datameet243_name
- `population` range: `16757` to `43243`

**`lgd_ward_code` distribution (top 10):**

| Value | Count |
|---|---|
| 1303146 | 2 |
| 1303155 | 2 |
| 1302706 | 2 |
| 1302710 | 2 |
| 1302733 | 2 |
| 1302771 | 2 |
| 1302758 | 2 |
| 1302782 | 2 |
| 1302796 | 2 |
| 1302801 | 2 |

### kaun_ward_metrics.csv

| Property | Value |
|---|---|
| **File** | `kaun_ward_metrics.csv` |
| **Size** | 62,363 bytes (60.9 KB) |
| **Encoding** | utf-8 |
| **Rows** | 254 |
| **Columns** | 44 |

**Columns:**

- `ward_no` ΓÇö 254 populated (0.0% missing) | 254 distinct values
- `ward_name` ΓÇö 243 populated (4.3% missing) | 244 distinct values
- `assembly_constituency` ΓÇö 242 populated (4.7% missing) | 28 distinct values
- `zone` ΓÇö 0 populated (100.0% missing) | 1 distinct values
- `ac_total_population` ΓÇö 228 populated (10.2% missing) | 27 distinct values
- `ac_total_households` ΓÇö 228 populated (10.2% missing) | 27 distinct values
- `ac_area_sqkm` ΓÇö 228 populated (10.2% missing) | 25 distinct values
- `ac_population_density` ΓÇö 228 populated (10.2% missing) | 27 distinct values
- `ac_road_length_km` ΓÇö 228 populated (10.2% missing) | 27 distinct values
- `ac_lakes` ΓÇö 228 populated (10.2% missing) | 12 distinct values
- `ac_parks` ΓÇö 228 populated (10.2% missing) | 26 distinct values
- `ac_playgrounds` ΓÇö 228 populated (10.2% missing) | 15 distinct values
- `ac_govt_schools` ΓÇö 228 populated (10.2% missing) | 19 distinct values
- `ac_police_stations` ΓÇö 228 populated (10.2% missing) | 9 distinct values
- `ac_fire_stations` ΓÇö 228 populated (10.2% missing) | 4 distinct values
- `ac_streetlights` ΓÇö 228 populated (10.2% missing) | 27 distinct values
- `ac_trees` ΓÇö 228 populated (10.2% missing) | 27 distinct values
- `ac_namma_clinics` ΓÇö 223 populated (12.2% missing) | 5 distinct values
- `ac_dwcc` ΓÇö 228 populated (10.2% missing) | 13 distinct values
- `ac_ward_count` ΓÇö 242 populated (4.7% missing) | 8 distinct values
- `demographics_source` ΓÇö 242 populated (4.7% missing) | 2 distinct values
- `demographics_year` ΓÇö 242 populated (4.7% missing) | 2 distinct values
- `traffic_signals` ΓÇö 243 populated (4.3% missing) | 31 distinct values
- `bus_stops` ΓÇö 243 populated (4.3% missing) | 26 distinct values
- `daily_bus_trips` ΓÇö 243 populated (4.3% missing) | 233 distinct values
- `spend_buildings_facilities` ΓÇö 243 populated (4.3% missing) | 244 distinct values
- `spend_drainage` ΓÇö 243 populated (4.3% missing) | 244 distinct values
- `spend_roads_and_drains` ΓÇö 243 populated (4.3% missing) | 243 distinct values
- `spend_roads_and_infrastructure` ΓÇö 243 populated (4.3% missing) | 244 distinct values
- `spend_streetlighting` ΓÇö 243 populated (4.3% missing) | 244 distinct values
- `spend_waste_management` ΓÇö 243 populated (4.3% missing) | 232 distinct values
- `spend_water_and_sanitation` ΓÇö 243 populated (4.3% missing) | 244 distinct values
- `spend_grand_total` ΓÇö 243 populated (4.3% missing) | 244 distinct values
- `spend_period` ΓÇö 243 populated (4.3% missing) | 2 distinct values
- `pothole_complaints` ΓÇö 243 populated (4.3% missing) | 119 distinct values
- `pothole_data_year` ΓÇö 243 populated (4.3% missing) | 2 distinct values
- `road_crashes_2024` ΓÇö 47 populated (81.5% missing) | 44 distinct values
- `fatal_crashes_2024` ΓÇö 47 populated (81.5% missing) | 30 distinct values
- `road_crashes_2025` ΓÇö 47 populated (81.5% missing) | 43 distinct values
- `fatal_crashes_2025` ΓÇö 47 populated (81.5% missing) | 30 distinct values
- `air_quality_station` ΓÇö 11 populated (95.7% missing) | 12 distinct values
- `avg_pm25` ΓÇö 9 populated (96.5% missing) | 10 distinct values
- `avg_pm10` ΓÇö 11 populated (95.7% missing) | 12 distinct values
- `total_work_orders` ΓÇö 10 populated (96.1% missing) | 11 distinct values

**Date fields detected:** ac_total_population, ac_population_density, ac_police_stations, ac_fire_stations, demographics_year, spend_water_and_sanitation, pothole_data_year, fatal_crashes_2024, fatal_crashes_2025, air_quality_station
- `ac_total_population` range: `171500` to `507806`

**`ward_no` distribution (top 10):**

| Value | Count |
|---|---|
| 1 | 1 |
| 2 | 1 |
| 3 | 1 |
| 4 | 1 |
| 5 | 1 |
| 6 | 1 |
| 7 | 1 |
| 8 | 1 |
| 9 | 1 |
| 10 | 1 |

**`ward_name` distribution (top 10):**

| Value | Count |
|---|---|
| Kempegowda Ward | 1 |
| Chowdeswari Ward | 1 |
| Someshwara Ward | 1 |
| Atturu Layout | 1 |
| Yelahanka Satellite Town | 1 |
| Kogilu | 1 |
| Thanisandra | 1 |
| Jakkuru | 1 |
| Amrutahalli | 1 |
| Kempapura | 1 |

---

## JSON Datasets


### civicissue_issues.json

| Property | Value |
|---|---|
| **File** | `civicissue_issues.json` |
| **Size** | 677,496 bytes (0.65 MB) |
| **Records** | 1,012 |
| **Fields (sample)** | 14 |

**Fields in first record:** `id`, `text`, `author`, `date`, `category`, `area`, `ward_name`, `ward_no`, `severity`, `likes`, `retweets`, `source_url`, `keywords`, `status`

**`category` distribution:**

| Value | Count |
|---|---|
| Electricity | 412 |
| Waste | 342 |
| Water | 79 |
| Roads | 68 |
| Traffic | 46 |
| Flooding | 33 |
| Parks | 18 |
| Other | 14 |

**`severity` distribution:**

| Value | Count |
|---|---|
| low | 1,001 |
| medium | 8 |
| high | 3 |

**`likes` distribution:**

| Value | Count |
|---|---|
| 0 | 858 |
| 1 | 97 |
| 2 | 25 |
| 3 | 8 |
| 4 | 4 |
| 7 | 4 |
| 6 | 3 |
| 11 | 2 |
| 8 | 2 |
| 154 | 1 |

**`retweets` distribution:**

| Value | Count |
|---|---|
| 0 | 948 |
| 1 | 43 |
| 2 | 8 |
| 3 | 3 |
| 6 | 2 |
| 10 | 2 |
| 4 | 2 |
| 54 | 1 |
| 21 | 1 |
| 8 | 1 |

**`date` range:** `2026-05-10T10:07:23+00:00` to `2026-07-04T15:01:38+00:00`

**Null/missing rates:**

- `ward_name`: 88.7% missing
- `ward_no`: 88.7% missing

### civicissue_issues_unfiltered.json

| Property | Value |
|---|---|
| **File** | `civicissue_issues_unfiltered.json` |
| **Size** | 3,349,647 bytes (3.19 MB) |
| **Records** | 4,989 |
| **Fields (sample)** | 14 |

**Fields in first record:** `id`, `text`, `author`, `date`, `category`, `area`, `ward_name`, `ward_no`, `severity`, `likes`, `retweets`, `source_url`, `keywords`, `status`

**`category` distribution:**

| Value | Count |
|---|---|
| Waste | 1,488 |
| Water | 692 |
| Electricity | 673 |
| Traffic | 599 |
| Roads | 462 |
| Parks | 458 |
| Flooding | 392 |
| Other | 225 |

**`ward_name` distribution:**

| Value | Count |
|---|---|
| Whitefield | 49 |
| Indiranagar | 22 |
| Koramangala East | 21 |
| HSR Layout | 17 |
| Kalyanagar | 17 |
| Marathahalli | 16 |
| Hebbal | 9 |
| J.P Nagar | 9 |
| K R Pura | 8 |
| Vinayakanagar | 8 |

**`ward_no` distribution:**

| Value | Count |
|---|---|
| 38 | 49 |
| 15 | 22 |
| 28 | 21 |
| 72 | 17 |
| 31 | 17 |
| 14 | 17 |
| 45 | 16 |
| 56 | 9 |
| 30 | 8 |
| 47 | 8 |

**`severity` distribution:**

| Value | Count |
|---|---|
| low | 4,656 |
| medium | 245 |
| high | 88 |

**`date` range:** `2026-05-10T06:47:07+00:00` to `2026-07-04T15:01:38+00:00`

**Null/missing rates:**

- `ward_name`: 95.8% missing
- `ward_no`: 95.8% missing

### civicissue_sample_issues.json

| Property | Value |
|---|---|
| **File** | `civicissue_sample_issues.json` |
| **Size** | 10,177 bytes (0.01 MB) |
| **Records** | 20 |
| **Fields (sample)** | 12 |

**Fields in first record:** `id`, `text`, `author`, `date`, `category`, `area`, `severity`, `likes`, `retweets`, `source_url`, `keywords`, `status`

**`id` distribution:**

| Value | Count |
|---|---|
| s001 | 1 |
| s002 | 1 |
| s003 | 1 |
| s004 | 1 |
| s005 | 1 |
| s006 | 1 |
| s007 | 1 |
| s008 | 1 |
| s009 | 1 |
| s010 | 1 |

**`text` distribution:**

| Value | Count |
|---|---|
| Massive pothole on 80 feet road Koramangala near Sony World signal. Two-wheelers falling daily. @BBMP_MAYOR please fix! #BangaloreRoads | 1 |
| No water supply in Indiranagar 12th main for 3 days now. BWSSB tanker hasn't come either. Families struggling. #BangaloreWater | 1 |
| Garbage dump overflowing outside Jayanagar 4th block shopping complex for 5 days. BBMP SWM completely failed. @BBMP_MAYOR | 1 |
| Power cut in Whitefield for 8 hours today. BESCOM gave no prior notice. WFH professionals badly affected. @BESCOMofficial | 1 |
| Entire stretch of Sarjapur Road waterlogged after last night's rain. Office traffic completely stuck since morning. @BBMP_MAYOR | 1 |
| Street light not working on HSR Layout 5th sector main road for 2 weeks. Very unsafe at night. Please fix @BBMP | 1 |
| Road digging by BWSSB on Bannerghatta road half-done for 3 months. No barricades. Pedestrians in danger. @CMofKarnataka | 1 |
| Cubbon Park benches broken, pathways cracked, no maintenance visible. Such a shame for Bangalore's lungs. @BBMP_MAYOR | 1 |
| Traffic signal at KR Puram junction not working from morning. Peak hour chaos. Cops nowhere to be seen. #Bangalore | 1 |
| Water pipe burst on MG Road near Trinity metro. Water wasting for 2 days. BWSSB not responding to calls. @BWSSB_official | 1 |

**`author` distribution:**

| Value | Count |
|---|---|
| @koramangala_resident | 1 |
| @indiranagar_voices | 1 |
| @jayanagar_cares | 1 |
| @whitefield_hub | 1 |
| @sarjapur_daily | 1 |
| @hsr_resident | 1 |
| @bannerghatta_citizen | 1 |
| @cubbon_park_walker | 1 |
| @krpuram_commuter | 1 |
| @mg_road_watch | 1 |

**`date` distribution:**

| Value | Count |
|---|---|
| 2026-05-16T08:30:00Z | 1 |
| 2026-05-15T14:00:00Z | 1 |
| 2026-05-16T09:15:00Z | 1 |
| 2026-05-16T11:30:00Z | 1 |
| 2026-05-17T07:45:00Z | 1 |
| 2026-05-14T20:00:00Z | 1 |
| 2026-05-13T10:00:00Z | 1 |
| 2026-05-15T07:00:00Z | 1 |
| 2026-05-17T09:00:00Z | 1 |
| 2026-05-15T16:30:00Z | 1 |

**`category` distribution:**

| Value | Count |
|---|---|
| Roads | 4 |
| Water | 3 |
| Waste | 3 |
| Electricity | 3 |
| Flooding | 3 |
| Parks | 2 |
| Traffic | 2 |

**`area` distribution:**

| Value | Count |
|---|---|
| Koramangala | 1 |
| Indiranagar | 1 |
| Jayanagar | 1 |
| Whitefield | 1 |
| Sarjapur | 1 |
| HSR Layout | 1 |
| Bannerghatta | 1 |
| Cubbon Park | 1 |
| KR Puram | 1 |
| MG Road | 1 |

**`severity` distribution:**

| Value | Count |
|---|---|
| high | 12 |
| medium | 8 |

**`likes` distribution:**

| Value | Count |
|---|---|
| 87 | 1 |
| 112 | 1 |
| 67 | 1 |
| 203 | 1 |
| 445 | 1 |
| 23 | 1 |
| 156 | 1 |
| 34 | 1 |
| 89 | 1 |
| 78 | 1 |

**`retweets` distribution:**

| Value | Count |
|---|---|
| 34 | 1 |
| 56 | 1 |
| 28 | 1 |
| 89 | 1 |
| 178 | 1 |
| 8 | 1 |
| 67 | 1 |
| 12 | 1 |
| 41 | 1 |
| 33 | 1 |

**`source_url` distribution:**

| Value | Count |
|---|---|
| https://twitter.com/koramangala_resident/status/s001 | 1 |
| https://twitter.com/indiranagar_voices/status/s002 | 1 |
| https://twitter.com/jayanagar_cares/status/s003 | 1 |
| https://twitter.com/whitefield_hub/status/s004 | 1 |
| https://twitter.com/sarjapur_daily/status/s005 | 1 |
| https://twitter.com/hsr_resident/status/s006 | 1 |
| https://twitter.com/bannerghatta_citizen/status/s007 | 1 |
| https://twitter.com/cubbon_park_walker/status/s008 | 1 |
| https://twitter.com/krpuram_commuter/status/s009 | 1 |
| https://twitter.com/mg_road_watch/status/s010 | 1 |

**`keywords` distribution:**

| Value | Count |
|---|---|
| ['pothole', 'road', 'accident', 'BBMP'] | 1 |
| ['water', 'supply', 'BWSSB', 'tanker'] | 1 |
| ['garbage', 'dump', 'BBMP', 'SWM', 'overflowing'] | 1 |
| ['power cut', 'BESCOM', 'electricity', 'outage'] | 1 |
| ['waterlogged', 'flooding', 'rain', 'road', 'traffic'] | 1 |
| ['street light', 'electricity', 'unsafe', 'BBMP'] | 1 |
| ['digging', 'BWSSB', 'road', 'barricade', 'pedestrian'] | 1 |
| ['park', 'maintenance', 'broken', 'Cubbon'] | 1 |
| ['traffic signal', 'junction', 'chaos', 'commute'] | 1 |
| ['water pipe', 'burst', 'BWSSB', 'leakage'] | 1 |

**`date` range:** `2026-05-12T08:00:00Z` to `2026-05-17T09:00:00Z`

**Null/missing rates:**


### kaun_contractors.json

| Property | Value |
|---|---|
| **File** | `kaun_contractors.json` |
| **Size** | 186,066 bytes (0.18 MB) |
| **Records** | 500 |
| **Fields (sample)** | 15 |

**Fields in first record:** `entity_id`, `canonical_name`, `aliases`, `phone`, `total_contracts`, `total_value_lakh`, `total_paid_lakh`, `total_deduction_lakh`, `avg_deduction_pct`, `ward_count`, `wards`, `first_seen`, `last_seen`, `is_govt_entity`, `blacklist_flags`

**`ward_count` distribution:**

| Value | Count |
|---|---|
| 1 | 139 |
| 3 | 93 |
| 2 | 92 |
| 4 | 45 |
| 5 | 37 |
| 6 | 27 |
| 7 | 19 |
| 8 | 14 |
| 9 | 10 |
| 10 | 6 |

**`is_govt_entity` distribution:**

| Value | Count |
|---|---|
| False | 498 |
| True | 2 |

**`blacklist_flags` distribution:**

| Value | Count |
|---|---|
| [] | 498 |
| ['Blacklisted by BBMP in 2010 (Deccan Herald, 24 Jun 2020)', "Blacklisted by Karnataka's Social Welfare Department in Oct 2018 (Deccan Herald, 24 Jun 2020)", 'Γé╣4,721 Cr of BBMP projects in 2015ΓÇô20 given without tender under KTPP Act Section 4(g), per a Bengaluru NavaNirmana Party analysis (Deccan Herald, 23 Sep 2020)'] | 2 |

**Null/missing rates:**


### kaun_reps_mla.json

| Property | Value |
|---|---|
| **File** | `kaun_reps_mla.json` |
| **Size** | 18,376 bytes (0.02 MB) |
| **Records** | 48 |
| **Fields (sample)** | 12 |

**Fields in first record:** `role`, `constituency`, `name`, `party`, `elected_since`, `phone`, `criminal_cases`, `age`, `profession`, `education`, `data_source`, `report_card`

**`party` distribution:**

| Value | Count |
|---|---|
| BJP | 16 |
| INC | 14 |
| BRS | 10 |
| AIMIM | 7 |
| IND | 1 |

**`elected_since` distribution:**

| Value | Count |
|---|---|
| May 2023 | 28 |
| 2023-12-03 | 18 |
| 2025-11-11 | 1 |
| 2024-05-13 | 1 |

**`criminal_cases` distribution:**

| Value | Count |
|---|---|
| 1 | 3 |
| 2 | 3 |
| 4 | 1 |
| 5 | 1 |
| 6 | 1 |
| 8 | 1 |

**`age` distribution:**

| Value | Count |
|---|---|
| 59 | 4 |
| 70 | 3 |
| 53 | 2 |
| 63 | 2 |
| 32 | 1 |
| 71 | 1 |
| 34 | 1 |
| 47 | 1 |
| 55 | 1 |
| 44 | 1 |

**`data_source` distribution:**

| Value | Count |
|---|---|
| eci-2023 | 18 |
| eci-bypoll-2025 | 1 |
| eci-bypoll-2024 | 1 |

**Null/missing rates:**

- `phone`: 43.8% missing
- `criminal_cases`: 79.2% missing
- `age`: 50.0% missing
- `profession`: 50.0% missing
- `education`: 100.0% missing
- `data_source`: 58.3% missing
- `report_card`: 41.7% missing

### kaun_ward_crosswalk.json

| Property | Value |
|---|---|
| **Top-level keys** | crosswalk, version, generated_at, method, sources |


### kaun_wards.json

| Property | Value |
|---|---|
| **File** | `kaun_wards.json` |
| **Size** | 23,219 bytes (0.02 MB) |
| **Records** | 243 |
| **Fields (sample)** | 4 |

**Fields in first record:** `ward_no`, `ward_name`, `assembly_constituency`, `zone`

**Null/missing rates:**

- `zone`: 100.0% missing

### kaun_work_orders.json

| Property | Value |
|---|---|
| **File** | `kaun_work_orders.json` |
| **Size** | 147,209 bytes (0.14 MB) |
| **Work Orders** | 200 |
| **Wards Fetched** | unknown |
| **Source** | unknown |
| **License** | unknown |
| **Attribution** | unknown |

**Fields:** `work_order_id`, `ward_no`, `bbmp_ward_no`, `ward_class`, `description`, `contractor_name`, `contractor_phone`, `sanctioned_amount`, `net_paid`, `deduction`, `fy`, `contractor_code`, `division`, `budget_head`, `start_date`, `end_date`, `order_ref`, `sbr_ref`, `bill_ref`, `payment_status`, `data_source`, `ifms_wbid`

**Fiscal year distribution:**

| FY | Count |
|---|---|
| 2014-15 | 1 |
| 2016-17 | 5 |
| 2017-18 | 1 |
| 2019-20 | 6 |
| 2021-22 | 3 |
| 2022-23 | 6 |
| 2023-24 | 16 |
| 2024-25 | 149 |
| 2025-26 | 13 |

**Ward class distribution:**

| Ward Class | Count |
|---|---|
| ward | 120 |
| citywide | 80 |

**Sanctioned amounts:**
- Total: Γé╣2,111.37 crore
- Average: Γé╣1,055.7 lakh
- Records with amount: 200 / 200

**Null/missing rates:**

- `bbmp_ward_no`: 40.0% missing
- `contractor_name`: 9.5% missing
- `contractor_phone`: 39.5% missing
- `net_paid`: 30.0% missing
- `deduction`: 30.0% missing
- `contractor_code`: 83.5% missing
- `division`: 70.0% missing
- `budget_head`: 70.0% missing
- `start_date`: 70.0% missing
- `end_date`: 70.0% missing
- `order_ref`: 70.0% missing
- `sbr_ref`: 75.0% missing
- `bill_ref`: 75.0% missing
- `payment_status`: 70.0% missing
- `ifms_wbid`: 70.0% missing

### kaun_work_orders_all_wards.json

| Property | Value |
|---|---|
| **File** | `kaun_work_orders_all_wards.json` |
| **Size** | 10,750,704 bytes (10.25 MB) |
| **Work Orders** | 11,072 |
| **Wards Fetched** | 243 |
| **Source** | kaun.city API |
| **License** | Public data, MIT licensed platform |
| **Attribution** | Data sourced from KAUN Bengaluru (kaun.city) via BBMP/opencity.in |

**Fields:** `work_order_id`, `ward_no`, `source_ward_name`, `datameet243_no`, `overlap_share`, `is_primary`, `description`, `contractor_name`, `contractor_phone`, `sanctioned_amount`, `net_paid`, `deduction`, `fy`, `contractor_code`, `division`, `budget_head`, `start_date`, `end_date`, `order_ref`, `sbr_ref`, `bill_ref`, `payment_status`, `data_source`, `ifms_wbid`

**Fiscal year distribution:**

| FY | Count |
|---|---|
| 2022-23 | 12 |
| 2023-24 | 1,511 |
| 2024-25 | 8,446 |
| 2025-26 | 1,101 |
| 2026-27 | 2 |

**Ward class distribution:**

| Ward Class | Count |
|---|---|
| (ward-specific) | 11,072 |

**Sanctioned amounts:**
- Total: Γé╣12,039.29 crore
- Average: Γé╣108.7 lakh
- Records with amount: 11,072 / 11,072

**Null/missing rates:**

- `source_ward_name`: 57.4% missing
- `contractor_phone`: 46.7% missing
- `net_paid`: 42.6% missing
- `deduction`: 42.6% missing
- `contractor_code`: 66.3% missing
- `division`: 57.4% missing
- `budget_head`: 57.4% missing
- `start_date`: 57.4% missing
- `end_date`: 57.4% missing
- `order_ref`: 57.4% missing
- `sbr_ref`: 58.8% missing
- `bill_ref`: 59.1% missing
- `payment_status`: 57.4% missing
- `ifms_wbid`: 57.4% missing
