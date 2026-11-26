# CivicLens Bengaluru — Data Access Issues Log

> Sprint 1 Data Acquisition  
> Date: 2026-11-23  
> Records all sources that were attempted but could not be acquired.

---

## Access Failures

### 1. OpenCity (opencity.in/dataset)

| Property | Detail |
|---|---|
| **URL attempted** | https://opencity.in/dataset |
| **HTTP result** | 403 Forbidden |
| **Methods tried** | HEAD, GET, GET with browser User-Agent |
| **Sub-paths tried** | https://data.opencity.in (403), https://opencity.in/api/3/action/package_list (403) |
| **Root cause** | Server actively blocks all non-browser programmatic access; likely CDN/WAF policy |
| **Impact** | Cannot directly download datasets from OpenCity. The I Change My City dataset was recovered via GitHub mirrors that pre-downloaded from OpenCity. |
| **Mitigation** | Use the GitHub mirror (UUID CSV) which contains the same underlying dataset. For future sprints, manual download via browser is feasible. |
| **Status** | Blocked — not retrying programmatically |

---

### 2. data.bengaluru.gov.in

| Property | Detail |
|---|---|
| **URL attempted** | https://data.bengaluru.gov.in |
| **HTTP result** | DNS resolution failed: 'data.bengaluru.gov.in' |
| **Root cause** | Domain does not resolve — portal is offline, decommissioned, or renamed |
| **Impact** | Cannot access official Bengaluru open data portal |
| **Mitigation** | KAUN Bengaluru serves as an aggregator of BBMP data; use KAUN as proxy |
| **Status** | DNS failure — portal appears to be down or domain changed |

---

### 3. NDAP (ndap.nic.in)

| Property | Detail |
|---|---|
| **URL attempted** | https://ndap.nic.in |
| **HTTP result** | DNS resolution failed: 'ndap.nic.in' |
| **Root cause** | Domain does not resolve — portal may have been reorganised under a different NIC subdomain |
| **Impact** | Cannot access the National Data and Analytics Platform |
| **Mitigation** | data.gov.in is accessible (HTTP 200) and covers equivalent national/state datasets |
| **Status** | DNS failure — verify correct current URL manually if needed |

---

### 4. BBMP Official Website (bbmp.gov.in)

| Property | Detail |
|---|---|
| **URL attempted** | https://bbmp.gov.in |
| **HTTP result** | SSL/TLS error — "Could not establish trust relationship for the SSL/TLS secure channel" |
| **Root cause** | SSL certificate is expired, self-signed, or issued by an untrusted CA |
| **Impact** | Cannot access BBMP official website |
| **Mitigation** | KAUN Bengaluru aggregates BBMP data with higher reliability |
| **Status** | SSL failure — not attempted further (would require bypassing certificate validation which is against policy) |

---

### 5. Overpass API (OpenStreetMap)

| Property | Detail |
|---|---|
| **URLs attempted** | https://overpass-api.de/api/status (502), https://overpass-api.de/api/interpreter GET (timeout), POST (406), https://overpass.kumi.systems (timeout) |
| **HTTP result** | Multiple failures: 502 Bad Gateway, 406 Not Acceptable, repeated timeouts |
| **Root cause** | Overpass API is under heavy load or geographically blocked; all test queries across multiple endpoints and methods failed |
| **Impact** | Cannot fetch Bengaluru road network via Overpass API |
| **Mitigation** | Geofabrik extracts are accessible (India page returns 200) but require OSM tooling (osmium/osmconvert) to extract Bengaluru subregion from full PBF. This is deferred to Sprint 2 when tooling can be installed. |
| **Status** | Deferred — Overpass unreachable; Geofabrik PBF requires additional tools |

---

### 6. data.gov.in (Programmatic API Access)

| Property | Detail |
|---|---|
| **URL attempted** | https://data.gov.in (HTTP 200), API paths like /api/1/metastore/schemas/dataset/items |
| **HTTP result** | HTTP 200 on all paths, but returns full HTML SPA regardless of path |
| **Root cause** | data.gov.in is a Next.js SPA; all API-style paths return the same HTML frontend — no server-side API rendering |
| **Impact** | Cannot programmatically search or download datasets from data.gov.in |
| **Mitigation** | Manual dataset discovery and download via browser is feasible. No Bengaluru-specific complaint datasets were identified in prior research on this portal. |
| **Status** | SPA — no programmatic API available without a headless browser |

---

### 7. Sahaaya 2.0

| Property | Detail |
|---|---|
| **Status** | Not attempted (by design) |
| **Reason** | Reconnaissance confirmed: requires authentication; no public data export documented. Attempting to access would require login — explicitly out of scope per sprint rules. |
| **Impact** | Government-side resolution tracking unavailable |
| **Mitigation** | Use complaint status from I Change My City dataset as proxy for resolution tracking |

---

### 8. FixMyStreet India

| Property | Detail |
|---|---|
| **URL attempted** | https://www.fixmystreet.in/ (HTTP 200) |
| **Data found** | Site is live but no bulk data download links or API endpoints visible on the public-facing pages |
| **Root cause** | India instance may not expose the same open data features as UK FixMyStreet |
| **Impact** | No Bengaluru-specific bulk complaint export available from this source |
| **Mitigation** | I Change My City dataset provides superior coverage |
| **Status** | No accessible data — skipped |

---

## Summary

| Source | Outcome | Workaround Used |
|---|---|---|
| OpenCity | 403 Blocked | GitHub mirror (same dataset) |
| data.bengaluru.gov.in | DNS fail | KAUN as aggregator |
| NDAP | DNS fail | Not needed (data.gov.in accessible) |
| BBMP official | SSL fail | KAUN as aggregator |
| Overpass API | 502/406/Timeout | Deferred to Sprint 2 |
| data.gov.in API | SPA — no API | Manual browse if needed |
| Sahaaya 2.0 | Out of scope | Not attempted |
| FixMyStreet India | No export available | Not needed |
