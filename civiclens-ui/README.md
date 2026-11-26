# CivicLens UI

React + Vite + TypeScript dashboard for the CivicLens Bengaluru civic intelligence system.

## Quick start

```bash
cd CivicBOB/civiclens-ui
npm run dev
```

Open **http://localhost:5173**

## Stack

| Layer | Library |
|---|---|
| Framework | React 19 + TypeScript |
| Build | Vite 8 |
| Routing | React Router v7 |
| Table | TanStack Table v8 (sortable, filterable, paginated) |
| Charts | Recharts |
| Map | Leaflet + OpenStreetMap (no API key required) |
| Styling | Tailwind CSS v4 |

## Data

Data is served as static JSON from `public/data/`:

| File | Contents |
|---|---|
| `cases_index.json` | Compact 298-row index for table/overview (216 KB) |
| `cases/CASE-*.json` | Full case detail per case, fetched on demand (includes `all_complaints`) |
| `ward_metrics.json` | 243-ward enrichment data |
| `ward_boundaries.geojson` | _(optional)_ Ward boundary polygons — enables choropleth on Ward Explorer |

Regenerate data after a pipeline re-run:

```bash
cd CivicBOB
python scripts/prepare_ui_data.py
```

### Ward boundary GeoJSON (optional)

To enable the choropleth view in Ward Explorer, download the BBMP ward boundaries and save as
`civiclens-ui/public/data/ward_boundaries.geojson`.

Sources to try:
- [datameet/municipal-data](https://github.com/datameet/municipal-data) — look under `Ward Boundary/`
- [geohacker/bengaluru](https://github.com/geohacker/bengaluru) — `ward/bengaluru_ward.geojson`
- BBMP Open Data portal — search for "ward boundary GeoJSON"

The GeoJSON must have a `ward_name` or `NAME` property on each feature matching
the ward names used in `cases_index.json`. Without this file, the Ward Explorer
falls back to point markers automatically.

## Pages

| Route | Page |
|---|---|
| `/` | City Overview — KPIs, charts, top priority cases |
| `/wards` | Ward Explorer — Leaflet map, ward selector, case list |
| `/cases` | Case Registry — sortable/filterable/paginated table |
| `/cases/:id` | Investigation — full evidence dossier per case |

## Production build

```bash
npm run build
# Output in dist/ — serve with any static host (Nginx, Vercel, etc.)
npx serve dist
```
