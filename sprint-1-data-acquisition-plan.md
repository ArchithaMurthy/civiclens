# CivicLens Sprint 1 — Data Acquisition Plan

> **Goal:** Acquire, verify and profile real Bengaluru civic complaint datasets. No application code. No synthetic data mixed with real data.
> **Prerequisite:** `DATA_RECONNAISSANCE.md` completed — sources identified and prioritised.

---

## Environment Constraints (Confirmed)

| Constraint | Detail |
|---|---|
| **Shell access** | Available in Agent mode only via `execute_command` (PowerShell on Windows) |
| **Network access** | Unknown until tested; must probe before assuming downloads will succeed |
| **Python** | Assumed available on host; must verify with `python --version` before use |
| **curl / wget** | PowerShell `Invoke-WebRequest` is the guaranteed fallback on Windows |
| **Plan mode** | No `execute_command` — plan only; switch to Agent mode for all execution steps |
| **No browser** | Cannot interactively browse portals; must use direct URL probing |

---

## Sub-Task 1 — Create Workspace Directory Structure

**Intent:** Establish the folder layout required by the sprint spec before any downloads begin.

**Expected Outcomes:**
- `data/raw/` exists
- `data/processed/` exists
- `data/metadata/` exists
- `data/synthetic/` exists (for future synthetic data, kept separate from real data per spec)
- `.gitkeep` placeholder in each empty directory

**Todo List:**
- [ ] Create `data/raw/` directory
- [ ] Create `data/processed/` directory
- [ ] Create `data/metadata/` directory
- [ ] Create `data/synthetic/` directory
- [ ] Write a `data/metadata/source_manifest.md` stub with headers (to be filled in Sub-Task 4)

**Relevant Context:** None — greenfield workspace.

**Status:** `[ ] pending`

---

## Sub-Task 2 — Probe Environment and Network Availability

**Intent:** Before any download is attempted, verify that the execution environment has network access and the required tools. Record the result honestly. If network is unavailable, the plan branches to the synthetic fallback path.

**Expected Outcomes:**
- Confirmed: Python version and availability
- Confirmed: `pip` availability
- Confirmed: Whether `Invoke-WebRequest` can reach the public internet (google.com HEAD probe)
- Confirmed: HTTP status code for each target URL:
  - `https://bengaluru.kaun.city/data`
  - `https://opencity.in/dataset`
  - `https://overpass-api.de/api/status`
  - `https://data.gov.in`
- All results written to `data/metadata/environment_probe.md`
- Decision recorded: "network available" or "network unavailable — activate fallback"

**Todo List:**
- [ ] Run `python --version` and record output
- [ ] Run `pip --version` and record output
- [ ] Run `Invoke-WebRequest -Uri "https://www.google.com" -Method HEAD -TimeoutSec 5` — record status code
- [ ] Run HEAD probe against `https://bengaluru.kaun.city/data` — record status code and Content-Type header
- [ ] Run HEAD probe against `https://opencity.in/dataset` — record status code
- [ ] Run HEAD probe against `https://overpass-api.de/api/status` — record status code
- [ ] Run HEAD probe against `https://data.gov.in` — record status code
- [ ] Write all results to `data/metadata/environment_probe.md`
- [ ] Set `NETWORK_AVAILABLE` flag based on probe results (used in Sub-Tasks 3–5)

**Relevant Context:** None — no existing code.

**Status:** `[ ] pending`

---

## Sub-Task 3A — Acquire KAUN Bengaluru Data (Network Available Path)

> **Precondition:** Sub-Task 2 confirmed `NETWORK_AVAILABLE = true` and KAUN returned HTTP 200.

**Intent:** Discover what datasets KAUN actually exposes, download the most relevant ones, and preserve originals untouched in `data/raw/`.

**Expected Outcomes:**
- Raw HTML of `https://bengaluru.kaun.city/data` fetched and scanned for dataset links
- At least one of the following downloaded to `data/raw/`:
  - `kaun_complaints_raw.csv` — civic complaint records
  - `kaun_wards.geojson` — BBMP ward boundaries
  - `kaun_roads_raw.csv` or `kaun_roads_raw.geojson` — road/pothole issues if separate
- If no direct CSV/GeoJSON link is found: record the failure, document what was actually available
- Download metadata written to `data/metadata/source_manifest.md`

**Todo List:**
- [ ] Fetch `https://bengaluru.kaun.city/data` page content (not scraping — single page fetch, respecting ToS)
- [ ] Parse page output for `href` links containing `.csv`, `.json`, `.geojson`, `/download/`, `/api/` patterns
- [ ] For each relevant link found: download with `Invoke-WebRequest` to `data/raw/<filename>`
- [ ] Record each download: source URL, filename, download datetime, file size, HTTP status
- [ ] If KAUN exposes an API (documented): probe `/api/` endpoint, record response schema
- [ ] If no downloadable files found: write `data/metadata/kaun_access_failure.md` with exact error

**Relevant Context:** See `DATA_RECONNAISSANCE.md` §1.2 for expected fields and formats.

**Status:** `[ ] pending`

---

## Sub-Task 3B — Acquire OpenCity Bengaluru Data (Network Available Path)

> **Precondition:** Sub-Task 2 confirmed `NETWORK_AVAILABLE = true` and OpenCity returned HTTP 200.

**Intent:** Download Bengaluru-specific datasets from OpenCity catalogue.

**Expected Outcomes:**
- OpenCity dataset catalogue page fetched and scanned
- At least one dataset downloaded to `data/raw/`:
  - `opencity_complaints_raw.csv` or equivalent
  - `opencity_wards.geojson` if separate from KAUN
- Download metadata written to `data/metadata/source_manifest.md`

**Todo List:**
- [ ] Fetch `https://opencity.in/dataset` page content
- [ ] Filter for Bengaluru-tagged datasets
- [ ] Download up to 3 most relevant datasets to `data/raw/`
- [ ] Record download metadata
- [ ] If no downloadable files: write `data/metadata/opencity_access_failure.md`

**Relevant Context:** See `DATA_RECONNAISSANCE.md` §1.3.

**Status:** `[ ] pending`

---

## Sub-Task 3C — Acquire OpenStreetMap Road Network (Network Available Path)

> **Precondition:** Sub-Task 2 confirmed Overpass API is reachable.

**Intent:** Fetch the Bengaluru road network from OpenStreetMap via Overpass API. Use a bounding-box query (not the full Karnataka PBF) to keep the file small enough for POC use.

**Expected Outcomes:**
- Overpass query returns GeoJSON road network for Bengaluru bounding box
- File saved to `data/raw/osm_bengaluru_roads.geojson`
- File size < 30 MB
- Download metadata written to `data/metadata/source_manifest.md`

**Overpass query to use:**
```
[out:json][timeout:60];
(
  way["highway"](12.834,77.461,13.143,77.784);
);
out geom;
```
> Bounding box: SW `12.834, 77.461` → NE `13.143, 77.784` (BBMP city limits)

**Todo List:**
- [ ] POST the Overpass query to `https://overpass-api.de/api/interpreter`
- [ ] Save response to `data/raw/osm_bengaluru_roads.geojson`
- [ ] Record file size, row count (number of ways), download datetime
- [ ] If response > 50 MB or times out: reduce bounding box and retry with central Bengaluru only (`12.907,77.544,13.013,77.660`)
- [ ] Record attribution: "© OpenStreetMap contributors, ODbL 1.0"

**Relevant Context:** See `DATA_RECONNAISSANCE.md` §1.4.

**Status:** `[ ] pending`

---

## Sub-Task 3D — Acquire Supplementary Government Data (Network Available Path)

> **Precondition:** Sub-Task 2 confirmed data.gov.in or data.bengaluru.gov.in returned HTTP 200.

**Intent:** Download BBMP ward metadata and agency-mapping data from official government sources. This enriches complaint records with authoritative ward names, zone assignments, and responsible agency contacts.

**Expected Outcomes:**
- At least one of the following downloaded to `data/raw/`:
  - `bbmp_wards.csv` — ward number, name, zone, area
  - `bbmp_service_centres.csv` — service centre locations with ward mapping
- Download metadata written to `data/metadata/source_manifest.md`

**Todo List:**
- [ ] Search `https://data.bengaluru.gov.in` for "ward" datasets — use API if documented, otherwise fetch catalogue page
- [ ] Search `https://ndap.nic.in` for Bengaluru/BBMP ward datasets
- [ ] Download up to 2 relevant datasets to `data/raw/`
- [ ] Record download metadata
- [ ] If no downloadable files: record failure and note that ward metadata must be manually sourced

**Relevant Context:** See `DATA_RECONNAISSANCE.md` §1.5.

**Status:** `[ ] pending`

---

## Sub-Task 3E — Fallback: Generate Synthetic Seed Dataset (Network Unavailable Path)

> **Precondition:** Sub-Task 2 confirmed `NETWORK_AVAILABLE = false` OR all download attempts in 3A–3D failed.

**Intent:** When real data cannot be acquired, generate a minimal synthetic dataset that faithfully follows the unified schema defined in `DATA_RECONNAISSANCE.md` §4. This dataset must be clearly labeled synthetic, stored separately from real data, and must not be presented as real data.

**Expected Outcomes:**
- `data/synthetic/synthetic_complaints_v1.csv` with 200–500 records
- Records cover all 13 category types, all 8 BBMP zones, and a 2-year date range
- File includes a `is_synthetic: true` column
- `data/synthetic/SYNTHETIC_DATA_NOTICE.md` explains generation methodology
- Primary deliverable shifts to schema validation and pipeline readiness

**Todo List:**
- [ ] Write Python script `scripts/generate_synthetic_data.py` that:
  - Uses only Python stdlib + random + datetime (no external dependencies)
  - Generates 500 records following the unified schema
  - Distributes complaints across 198 wards, 13 categories, and 2-year date range
  - Intentionally seeds ~15% duplicates (same location + category within 7 days) for dedup testing
  - Outputs `data/synthetic/synthetic_complaints_v1.csv`
- [ ] Run the script and verify output
- [ ] Write `data/synthetic/SYNTHETIC_DATA_NOTICE.md`
- [ ] Update `data/metadata/source_manifest.md` to reflect synthetic dataset

**Relevant Context:** Unified schema in `DATA_RECONNAISSANCE.md` §4; category taxonomy §4.

**Status:** `[ ] pending`

---

## Sub-Task 4 — Profile All Acquired Datasets

**Intent:** For every file in `data/raw/` (and `data/synthetic/` if activated), produce a structured data profile. This is the foundation for the multi-agent pipeline design — the pipeline must be designed around what the data actually contains.

**Expected Outcomes:**
- For each dataset, the following are known and documented:
  - Row count
  - Column count and names
  - Data types per column
  - Null/missing value rate per column
  - Date range (min/max of date fields)
  - Category distribution (top 10 values for category columns)
  - Geographic coverage (lat/lon range, number of distinct wards)
  - Duplicate record count (exact ID duplicates)
  - Near-duplicate estimate (same ward + category within 7 days)
  - Whether complaint text/description field is populated
- All profiles written to `data/metadata/dataset_profiles.md`

**Todo List:**
- [ ] Write Python script `scripts/profile_datasets.py` that:
  - Reads each CSV in `data/raw/` (and `data/synthetic/` if present)
  - Outputs a Markdown report section per file
  - Handles both CSV and GeoJSON inputs
  - Uses only `csv`, `json`, `collections`, `datetime` stdlib modules (no pandas dependency)
- [ ] Run the script
- [ ] Write output to `data/metadata/dataset_profiles.md`
- [ ] Manually review profiles for any anomalies not caught by script

**Relevant Context:** Unified schema §4 of `DATA_RECONNAISSANCE.md` defines expected fields to look for.

**Status:** `[ ] pending`

---

## Sub-Task 5 — Write Source Manifest

**Intent:** Create a single authoritative record of every dataset acquired, its provenance, license, and suitability. This becomes the reference document for the pipeline build sprint.

**Expected Outcomes:**
- `data/metadata/source_manifest.md` is complete with one entry per dataset
- Each entry includes: source name, URL, download date, file path, format, row count, license, attribution string, POC suitability rating, and known limitations
- `data/metadata/data_access_issues.md` documents every source that was attempted but failed

**Todo List:**
- [ ] Collate all download records from Sub-Tasks 3A–3D (or 3E)
- [ ] Write `data/metadata/source_manifest.md` with one entry per dataset
- [ ] Write `data/metadata/data_access_issues.md` with one entry per failed access attempt
- [ ] Cross-check that every file in `data/raw/` has a manifest entry
- [ ] Cross-check that every manifest entry has a corresponding file in `data/raw/`

**Relevant Context:** `DATA_RECONNAISSANCE.md` §7 (Acquisition Plan) contains the expected manifest structure.

**Status:** `[ ] pending`

---

## Sub-Task 6 — Write Acquisition Report and Recommendation

**Intent:** Produce the final deliverable of Sprint 1: a clear, evidence-grounded recommendation for which dataset(s) should power the CivicLens POC pipeline, based on what was actually downloaded and profiled.

**Expected Outcomes:**
- `data/metadata/acquisition_report.md` written, containing:
  1. Summary of what was acquired vs. what was attempted
  2. Dataset profile highlights (best and worst quality datasets)
  3. Final recommendation: primary dataset for POC
  4. Final recommendation: supplementary datasets
  5. Data gaps that must be addressed before the pipeline can run
  6. Specific field-mapping notes (how source fields map to unified schema)
  7. Next steps for Sprint 2 (pipeline build)

**Todo List:**
- [ ] Read `data/metadata/dataset_profiles.md`
- [ ] Read `data/metadata/data_access_issues.md`
- [ ] Write `data/metadata/acquisition_report.md`
- [ ] Update `DATA_RECONNAISSANCE.md` with any findings that supersede the reconnaissance report

**Relevant Context:** `DATA_RECONNAISSANCE.md` §2 (Primary Dataset recommendation) is the baseline to validate or revise.

**Status:** `[ ] pending`

---

## Execution Order

```
Sub-Task 1 (Workspace)
    ↓
Sub-Task 2 (Probe)
    ↓
    ├── NETWORK_AVAILABLE = true
    │       ↓
    │   Sub-Tasks 3A, 3B, 3C, 3D (run sequentially — Overpass has rate limits)
    │
    └── NETWORK_AVAILABLE = false (or all downloads failed)
            ↓
        Sub-Task 3E (Synthetic fallback)
    ↓
Sub-Task 4 (Profile)
    ↓
Sub-Task 5 (Manifest)
    ↓
Sub-Task 6 (Report)
```

> **Note on Overpass rate limits:** Space Overpass requests at least 10 seconds apart. The free Overpass API allows 1 request per 10 seconds per IP. Do not issue parallel requests.

---

## Files This Sprint Will Create

| File | Sub-Task | Description |
|---|---|---|
| `data/raw/kaun_complaints_raw.csv` | 3A | KAUN complaint records (if available) |
| `data/raw/kaun_wards.geojson` | 3A | BBMP ward boundaries from KAUN (if available) |
| `data/raw/opencity_*.csv` | 3B | OpenCity Bengaluru datasets (if available) |
| `data/raw/osm_bengaluru_roads.geojson` | 3C | OSM road network for Bengaluru bounding box |
| `data/raw/bbmp_wards.csv` | 3D | BBMP ward metadata from gov portal (if available) |
| `data/synthetic/synthetic_complaints_v1.csv` | 3E | Synthetic fallback dataset (only if network fails) |
| `data/synthetic/SYNTHETIC_DATA_NOTICE.md` | 3E | Disclaimer and generation methodology |
| `scripts/generate_synthetic_data.py` | 3E | Synthetic data generation script |
| `scripts/profile_datasets.py` | 4 | Dataset profiling script |
| `data/metadata/environment_probe.md` | 2 | Network and tool availability results |
| `data/metadata/source_manifest.md` | 5 | Authoritative dataset registry |
| `data/metadata/dataset_profiles.md` | 4 | Per-dataset profiling report |
| `data/metadata/data_access_issues.md` | 5 | Failed access attempts log |
| `data/metadata/acquisition_report.md` | 6 | Final Sprint 1 deliverable |

---

## What This Sprint Does NOT Do

- Does not build any agents, dashboards, or application code
- Does not mix synthetic data with real data
- Does not scrape websites (single-page fetches of public data portals are not scraping)
- Does not attempt authenticated access to Sahaaya 2.0 or any gated endpoint
- Does not normalise data into the unified schema (that is Sprint 2)
- Does not store data outside the `data/` directory

---

*Sprint 1 Data Acquisition Plan — CivicLens Bengaluru*
