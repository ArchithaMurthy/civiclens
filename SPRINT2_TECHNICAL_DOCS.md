# CivicLens Bengaluru — Sprint 2 Technical Documentation

> **Sprint goal:** Build the core civic intelligence pipeline. Transform raw complaints into evidence-backed civic cases.  
> **Completed:** 2026-11-23  
> **Data:** Real datasets only (no synthetic data used in production pipeline)

---

## Repository Structure

```
CivicBOB/
├── DATA_RECONNAISSANCE.md          # Sprint 0: data source investigation
├── sprint-1-data-acquisition-plan.md
├── run_pipeline.py                 # Main pipeline runner (run this first)
│
├── pipeline/
│   ├── __init__.py
│   ├── schema.py                   # Pydantic data models (Complaint, WorkOrder, WardMetrics)
│   ├── normalise.py                # Category, agency, status normalisation maps
│   ├── ingest.py                   # Data loading + normalisation
│   ├── dedup.py                    # Duplicate detection
│   ├── cluster.py                  # Problem clustering (DBSCAN + ward-temporal)
│   ├── enrich.py                   # Evidence enrichment from KAUN datasets
│   ├── cases.py                    # Civic intelligence case generation
│   ├── prioritise.py               # Priority scoring
│   └── evaluate.py                 # Pipeline evaluation
│
├── scripts/
│   ├── fetch_kaun_work_orders.py   # Sprint 1: download KAUN work orders
│   ├── profile_datasets.py         # Sprint 1: data profiling
│   ├── inspect_road_data.py        # Sprint 2 recon: road complaint analysis
│   └── inspect_work_orders.py      # Sprint 2 recon: work order analysis
│
├── data/
│   ├── raw/                        # Original downloaded datasets (read-only)
│   │   ├── ichangemycity_complaints.csv      # PRIMARY: 16,071 complaints 2019-2021
│   │   ├── kaun_work_orders_all_wards.json   # 11,072 BBMP work orders FY2023-26
│   │   ├── kaun_ward_metrics.csv             # 243-ward enrichment data
│   │   ├── kaun_ward_crosswalk.csv           # Ward numbering crosswalk
│   │   ├── kaun_wards.json                   # Ward name reference
│   │   ├── kaun_contractors.json             # BBMP contractor registry
│   │   ├── kaun_reps_mla.json               # MLA data
│   │   ├── civicissue_issues.json            # 1,012 GovWatch complaints 2026
│   │   ├── civicissue_issues_unfiltered.json # 4,989 unfiltered GovWatch
│   │   └── civicissue_tweet_analysis.csv     # 338 labelled tweet verdicts
│   │
│   ├── processed/                  # Pipeline outputs (generated, safe to delete and re-run)
│   │   ├── complaints_normalised.json        # 17,083 normalised complaints
│   │   ├── work_orders_normalised.json       # 11,072 normalised work orders
│   │   ├── ward_metrics_normalised.json      # 243 ward enrichment records
│   │   ├── dedup_candidates.json             # 16,513 duplicate candidate pairs
│   │   ├── civic_cases.json                  # 298 civic intelligence cases
│   │   ├── civic_cases_summary.csv           # Summary CSV of all cases
│   │   ├── sprint2_evaluation.md             # Evaluation report
│   │   ├── eval_dedup_sample.csv             # 20 dedup pairs for human review
│   │   └── eval_cases_sample.csv             # 15 HIGH-priority cases for review
│   │
│   ├── metadata/                   # Sprint 1 and 2 metadata
│   │   ├── source_manifest.md
│   │   ├── dataset_profiles.md
│   │   ├── data_access_issues.md
│   │   ├── acquisition_report.md
│   │   ├── environment_probe.md
│   │   └── sprint2_use_case_selection.md
│   │
│   └── synthetic/                  # Empty — synthetic data not activated
```

---

## Pipeline Architecture

```
data/raw/
  ichangemycity_complaints.csv    (16,071 records)
  kaun_work_orders_all_wards.json (11,072 records)
  kaun_ward_metrics.csv           (243 records)
       ↓
pipeline/ingest.py                → Normalise → complaints_normalised.json
       ↓
pipeline/dedup.py                 → 163 exact dups + 689 near-dups
       ↓
pipeline/cluster.py               → 298 clusters (189 geo + 109 ward)
       ↓
pipeline/enrich.py                → Attach ward metrics + work orders
       ↓
pipeline/cases.py + prioritise.py → 298 civic cases (15 HIGH, 172 MED, 111 LOW)
       ↓
data/processed/civic_cases.json
data/processed/civic_cases_summary.csv
```

---

## How to Run

```bash
# Run the full pipeline (5–7 seconds)
python run_pipeline.py

# Run evaluation and generate review samples
python -m pipeline.evaluate
```

**Requirements:** Python 3.14+, pandas, pydantic, scikit-learn, geopy

```bash
pip install pandas pydantic scikit-learn geopy
```

---

## Pipeline Stage Descriptions

### Stage 1: Ingest (`pipeline/ingest.py`)

Loads three datasets:
- **I Change My City** (ICMC): `ichangemycity_complaints.csv` — 16,071 records, cp1252 encoding, mixed date formats
- **GovWatch**: `civicissue_issues.json` — 1,012 records, ISO dates, no GPS
- **KAUN work orders**: `kaun_work_orders_all_wards.json` — 11,072 records
- **KAUN ward metrics**: `kaun_ward_metrics.csv` — 243 records

All records are normalised to Pydantic models. Original values are preserved in `*_original` fields. Date parsing handles 3 mixed formats in ICMC. GPS coordinates are validated against the BBMP bounding box.

**Date parsing success rate: 100% (17,083 / 17,083)**

### Stage 2: Duplicate Detection (`pipeline/dedup.py`)

Rule-based detection on the ICMC road infrastructure subset (5,072 complaints):
- Groups by ward to avoid O(n²) global comparison
- Compares within 60-day window (sorted by date for efficiency)
- Signals: text fingerprint, GPS proximity (50m/200m), temporal proximity (3/7 days), subcategory match

| Type | Count | Confidence threshold |
|---|---|---|
| Exact duplicate | 163 | text fingerprint + same ward + ≤7 days |
| Near-duplicate | 689 | ≥0.65 confidence |
| Related | 15,661 | 0.35–0.65, flagged for clustering |

No complaints are deleted. Flags only.

### Stage 3: Problem Clustering (`pipeline/cluster.py`)

Two-pass clustering:

**Pass 1 — DBSCAN geographic clustering:**
- Input: 5,072 road complaints with valid GPS
- Algorithm: sklearn DBSCAN with haversine metric, eps=300m, min_samples=5
- Acceptance filter: must span ≥2 distinct years AND bbox ≤2km
- Result: 189 geo clusters

**Pass 2 — Ward-temporal clustering:**
- Input: complaints not assigned in Pass 1
- Groups by ward_id × subcategory
- Acceptance filter: ≥5 complaints, ≥2 distinct years
- Result: 109 ward clusters

**Total: 298 clusters covering 4,176 of 5,072 road complaints. 896 unclustered.**

### Stage 4: Evidence Enrichment (`pipeline/enrich.py`)

For each cluster, attaches:
1. **Ward metrics** (KAUN): pothole complaint count 2022, road spending 2018–23, road crashes 2024
2. **Work orders** (KAUN): road/drain work orders in matching ward, FY 2023–26

Ward join: ICMC ward_id (1–198) → datameet243_no via crosswalk CSV. Join confidence documented per case.

**All inferences are labelled "HYPOTHESIS". Work orders are contextual evidence only — not proof of repair.**

### Stage 5: Case Generation (`pipeline/cases.py`)

Produces one `CivicCase` per cluster containing:
- Problem title and summary (data-derived, no LLM)
- Complaint chronology by year
- Evidence items with source traceability
- Responsible agency (derived from source data, confidence labelled)
- Recommended next steps (RTI, inspection, field survey)
- Hypotheses (explicitly labelled as unverified)

### Stage 6: Prioritisation (`pipeline/prioritise.py`)

Weighted factor scoring (all weights configurable via `SCORING_WEIGHTS`):

| Factor | Weight | Normalisation ceiling |
|---|---|---|
| Complaint volume | 25% | 100 complaints → 1.0 |
| Recurrence years | 25% | 4 years → 1.0 |
| Unresolved rate | 20% | raw fraction |
| Re-opened rate | 10% | raw fraction |
| Road crash risk (ward) | 10% | 100 crashes/yr → 1.0 |
| Severity keyword hits | 10% | loose normalisation |

Tier thresholds (calibrated to data): HIGH ≥ 0.50, MEDIUM ≥ 0.30, LOW < 0.30

---

## Key Results

| Metric | Value |
|---|---|
| Total complaints processed | 17,083 |
| Road infrastructure complaints | 5,072 |
| Exact duplicate pairs detected | 163 |
| Near-duplicate pairs detected | 689 |
| Problem clusters generated | 298 |
| Civic cases produced | 298 |
| HIGH priority cases | 15 |
| MEDIUM priority cases | 172 |
| LOW priority cases | 111 |
| Pipeline execution time | ~6 seconds |

### Top 3 cases by priority score

1. **GEO-0044 / Begur** — 56 pothole complaints, 50% unresolved, all 4 years, BBMP. Score: 0.624
2. **GEO-0034 / Varthur** — 103 pothole complaints, 50.5% unresolved, all 4 years, BBMP. Score: 0.610
3. **WARD-150 / Bellanduru** — 100 pothole complaints, 27% unresolved, all 4 years, BBMP. Score: 0.574

---

## Design Decisions and Constraints

### What the pipeline does NOT do
- Does not use an LLM anywhere in the core pipeline
- Does not modify or overwrite raw data files
- Does not claim a work order fixed a specific complaint
- Does not infer contractor misconduct from deductions or blacklist flags
- Does not use synthetic data

### What requires manual verification before operational use
- Duplicate detection: 163 exact pairs reviewed by algorithm only; human spot-check needed
- Cluster coherence: geo clusters with large extents (>1km) need field verification
- Ward joins: approximate joins have documented uncertainty; crosswalk joins are higher confidence
- Case narratives: descriptions are data-derived; claims about current road condition need field verification

---

## Sprint 3 Roadmap

### Priority 1 — Data freshness
- Acquire updated I Change My City data beyond Sep 2021 (manual download from OpenCity)
- Register at IUDX for real-time IoT/environmental data
- Investigate whether BBMP has a newer complaint dump

### Priority 2 — Spatial enrichment
- Acquire BBMP ward boundary GeoJSON (via osmium on Geofabrik extract, or manual source)
- Add nearest-road name from OSM (once Overpass becomes reachable or osmium is available)
- Assign GPS coordinates to ward-only GovWatch complaints via ward centroid lookup

### Priority 3 — NLP improvement
- Use sentence-transformers for semantic similarity in dedup (complement text fingerprint)
- Apply topic modelling on complaint descriptions to generate cluster titles automatically
- Build LLM-assisted narrative summarisation for case generation (optional enrichment layer)

### Priority 4 — Pipeline hardening
- Add a stable complaint ID scheme to avoid ID drift between runs
- Build incremental update mode (don't re-process records already in civic_cases.json)
- Add a validation step for ward crosswalk joins
- Create regression tests for the ingest and dedup stages

### Priority 5 — Output layer
- Build a minimal Streamlit dashboard displaying the top 20 HIGH-priority cases
- Add a CSV export formatted for journalist/advocacy use
- Add a simple REST API endpoint (FastAPI) for cases by ward or priority tier

---

*Sprint 2 complete — CivicLens Bengaluru*
