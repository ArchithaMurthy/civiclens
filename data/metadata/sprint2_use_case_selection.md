# Sprint 2 — Use Case Selection

> **Date:** 2026-11-23  
> **Purpose:** Determine which civic complaint category provides the strongest demonstrable use case for the CivicLens POC pipeline.  
> **Method:** Direct analysis of acquired datasets. All findings are derived from actual data.

---

## 1. Category Landscape (ichangemycity_complaints.csv — 16,071 records)

| Category | Count | % of total |
|---|---|---|
| Mobility – Roads, Footpaths and Infrastructure | 5,072 | 31.6% |
| Garbage and Unsanitary Practices | 3,946 | 24.6% |
| Traffic and Road Safety | 967 | 6.0% |
| Yellow Spot | 948 | 5.9% |
| Animal Husbandry | 859 | 5.3% |
| Street lighting / Streetlights (combined) | 1,500 | 9.3% |
| Pollution | 437 | 2.7% |
| Water Supply and Services | 320 | 2.0% |
| Sewerage Systems | 301 | 1.9% |
| Storm Water Drains | 138 | 0.9% |

**Finding:** "Mobility – Roads, Footpaths and Infrastructure" is by far the largest category (31.6% of all complaints, 5,072 records). It is 28% larger than the second category (Garbage).

---

## 2. Road Complaint Subcategory Breakdown

| Subcategory | Count |
|---|---|
| Fixing/Repairing Potholes | 2,247 |
| Tarring Or Asphalting Of Existing Road | 1,623 |
| Tarring Or Asphalting Of Mud/Kutcha/Unpaved Road | 260 |
| Flooding/Waterlogging Of Roads And Footpaths | 226 |
| Construction Of Roadside Drains | 117 |
| Construction of new footpaths | 116 |
| Removal Of Roadside Debris | 90 |
| Repair Of Existing Footpaths | 83 |

**Finding:** The two dominant road subcategories together (Potholes + Tarring = 3,870 records) account for 76.3% of all road complaints. These are the same underlying infrastructure failure — a road that needs resurfacing generates both pothole reports and tarring requests. This makes them ideal for deduplication and clustering.

---

## 3. Geographic Concentration

Top wards for road complaints:

| Ward | Road Complaints |
|---|---|
| Bellanduru | 378 |
| Begur | 279 |
| Horamavu | 231 |
| Thanisandra | 194 |
| Varthur | 165 |
| Dodda Nekkundi | 137 |
| Singasandra | 125 |

**"Other" (ward_id=199, unlocated) accounts for 281 records** — these cannot be spatially clustered and will be noted but excluded from geo-clustering.

**Finding:** Bellanduru, Begur, Horamavu, Thanisandra, and Varthur are persistent hotspot wards. Each has hundreds of complaints over 2.75 years.

---

## 4. Temporal Recurrence

Road complaints appearing in **every year of the dataset** (2019, 2020, 2021, 2022):

- Begur: Potholes AND Tarring (both subcategories, every year)
- Ramamurthy Nagar: Potholes (every year)
- Bellanduru: Tarring (every year)
- Shettihalli: Tarring (every year)
- Arekere: Potholes (every year)
- HBR Layout: Potholes (every year)

**375 ward × subcategory pairs** appear in more than one year. This is the strongest recurrence signal in the dataset.

**Finding:** Road complaints recur in the same wards year after year — this is exactly the "recurring civic problem" pattern CivicLens is designed to detect.

---

## 5. Resolution Analysis

| Status | Count | % |
|---|---|---|
| Open | 2,173 | 42.8% |
| Resolved | 1,580 | 31.2% |
| On-the-Job | 1,188 | 23.4% |
| Re-opened | 129 | 2.5% |
| Rejected | 2 | 0.0% |

**Finding:** 42.8% of road complaints remain Open. 2.5% were Re-opened (resolved and broken again). This is a strong indicator of systemic non-resolution — a key CivicLens narrative.

---

## 6. Work Order Alignment

Work order categories from `kaun_work_orders_all_wards.json` (11,072 records, FY 2023–26):

| Work Order Category | Count |
|---|---|
| Road construction/resurfacing | 6,384 (57.7%) |
| Drain construction/desilting | 691 (6.2%) |
| Streetlight installation | 676 (6.1%) |
| Water/BWSSB works | 470 (4.2%) |
| Footpath works | 257 (2.3%) |
| Other | 2,594 (23.4%) |

**Finding:** 57.7% of BBMP work orders are road-related. This is the largest overlap between complaint categories and work order categories. The key intelligence narrative is: **road complaints exist in ward X → work order exists in ward X → complaint persists anyway** (or: work was done but complaints pre-date it, or complaints re-emerged).

**Ward join:** ICMC uses ward_ids 1–198 (pre-2020 198-ward scheme). KAUN uses datameet243 numbering. The crosswalk CSV maps 225 of the BBMP wards — 198 ICMC ward IDs directly overlap with the datameet243 range (1–198), enabling an approximate direct join for wards 1–198. Ward 199 ("Other") cannot be joined and is excluded.

---

## 7. Complaint Description Quality

- Average description length: 224 characters
- 100% of records have a description field populated
- Descriptions are predominantly English
- Quality ranges from one-liners ("Begur road full of potholes") to detailed multi-paragraph accounts
- Road complaints specifically tend to include street names, landmark references, and history of prior repair attempts — making them rich for NLP

**Finding:** Description quality is high enough for text-similarity-based deduplication and semantic clustering without requiring LLM processing for every record.

---

## 8. Garbage Category Assessment (Second Candidate)

Garbage complaints (3,946 records, 24.6%) were considered as an alternative. However:

- Garbage complaints are diffuse — spread across pickup failures, dumping sites, and hygiene — making clustering harder
- Work order data has very limited garbage/solid waste entries compared to road works
- The ward × category recurrence signal is weaker (most garbage complaints are one-off events, not structural failures)

**Conclusion:** Garbage is a viable second use case for Sprint 3 but is weaker than roads for the initial POC.

---

## 9. Decision

### **Selected use case: Road Infrastructure Failure (Pothole + Road Resurfacing complaints)**

**Justification:**

1. **Volume:** 5,072 records (31.6% of dataset) — the largest single category
2. **Recurrence:** 375 ward × subcategory pairs appear in multiple years; most hotspot wards show complaints every single year 2019–2022
3. **Non-resolution:** 42.8% remain Open; 2.5% Re-opened — systemic failure signal
4. **GPS coverage:** 100% of records have GPS — enables spatial deduplication and cluster maps
5. **Work order crossover:** 57.7% of KAUN work orders are road-related — enabling the accountability narrative
6. **Description quality:** Rich text descriptions suitable for NLP-based clustering
7. **Ward join feasibility:** 198 ICMC wards directly mappable to KAUN datameet243 for enrichment
8. **Demo value:** A cluster showing "184 pothole reports in Bellanduru over 3 years, with ₹X Cr road contract in 2024-25, yet 42% unresolved" is immediately compelling to any citizen or journalist

### **Scope for Sprint 2 pipeline:**

The pipeline will process **all 16,071 ICMC complaints** (not just road complaints) through ingestion and normalization, but will focus the clustering, enrichment, and case generation specifically on the **road infrastructure** subset:

- Primary: `Fixing/Repairing Potholes` (2,247 records)
- Secondary: `Tarring Or Asphalting Of Existing Road` (1,623 records)
- Tertiary: `Flooding/Waterlogging Of Roads And Footpaths` (226 records) — included because flooding complaints are frequently caused by road-level drainage failures

**Total focused dataset: 4,096 complaints** across 198 wards spanning 2019–2022.

---

## 10. Ward Numbering Note (Important for all joining)

ICMC uses a 1–199 ward numbering scheme where:
- IDs 1–198 correspond to BBMP's pre-2020 198-ward delimitation
- ID 199 = "Other" (unlocated, 637 records = 4.0% of total) — excluded from geo-joins

KAUN uses the datameet243 numbering (1–243). The ward crosswalk CSV (`kaun_ward_crosswalk.csv`) shows that for the 1–198 range, ICMC ward_id and datameet243_no align closely but are **not identical** — the crosswalk should be used for confident joins, with `overlap_confidence` retained as a join quality indicator.

For Sprint 2: direct ward_id join will be used as a first approximation; crosswalk-based joins will be used where high confidence is needed (enrichment and dossier generation).
