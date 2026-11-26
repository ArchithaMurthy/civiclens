# Environment Probe Results

> Sprint 1 Sub-Task 2 — executed during data acquisition run
> Date: 2026-11-23

---

## Tool Availability

| Tool | Version | Status |
|---|---|---|
| Python | 3.14.5 (C:\Python314) | ✅ Available |
| pip | 26.1.1 | ✅ Available |
| PowerShell Invoke-WebRequest | Built-in | ✅ Available |
| python3 alias | — | ❌ Not mapped (use `python`) |

---

## Network Probe Results

### General Internet Access

| Target | Method | Result |
|---|---|---|
| google.com | HEAD | ✅ HTTP 200 — internet is accessible |

### Civic Data Sources

| Source | URL | Method | Result | Notes |
|---|---|---|---|---|
| **KAUN Bengaluru** | https://bengaluru.kaun.city/data | HEAD | ✅ HTTP 200 | HTML page; accessible |
| **CivicIssue India** | https://civicissue.in/ | HEAD | ✅ HTTP 200 | HTML page; accessible |
| **data.gov.in** | https://data.gov.in | HEAD | ✅ HTTP 200 | HTML page; accessible |
| **Geofabrik India** | https://download.geofabrik.de/asia/india.html | HEAD | ✅ HTTP 200 | Download index accessible |
| OpenCity | https://opencity.in/dataset | HEAD | ❌ HTTP 403 Forbidden | Server blocks programmatic HEAD requests |
| data.bengaluru.gov.in | https://data.bengaluru.gov.in | HEAD | ❌ DNS resolution failed | Domain not resolving — portal may be down or renamed |
| NDAP | https://ndap.nic.in | HEAD | ❌ DNS resolution failed | Domain not resolving |
| BBMP | https://bbmp.gov.in | HEAD | ❌ SSL/TLS error | Certificate trust failure; site unreachable |

### Overpass API (OpenStreetMap)

| Endpoint | Method | Result |
|---|---|---|
| https://overpass-api.de/api/status | HEAD | ❌ HTTP 502 Bad Gateway |
| https://overpass-api.de/api/interpreter | POST | ❌ HTTP 406 Not Acceptable |
| https://overpass-api.de/api/interpreter | GET | ❌ Timeout (20s) |
| https://overpass.kumi.systems/api/interpreter | HEAD | ❌ Timeout (10s) |

> **Conclusion:** Overpass API is unreachable from this environment via all tested methods. OSM data must be acquired via Geofabrik direct download or deferred.

---

## Decision

```
NETWORK_AVAILABLE = true   (general internet access confirmed)

Accessible sources:
  ✅ KAUN Bengaluru      → proceed with Sub-Task 3A
  ✅ CivicIssue India    → attempt page scan for download links
  ✅ data.gov.in         → attempt dataset search
  ✅ Geofabrik           → attempt Karnataka OSM download (large file warning)

Inaccessible sources:
  ❌ OpenCity            → 403; skip Sub-Task 3B (record failure)
  ❌ data.bengaluru.gov.in → DNS fail; skip
  ❌ NDAP                → DNS fail; skip
  ❌ BBMP                → SSL fail; skip
  ❌ Overpass API        → all endpoints unreachable; OSM via Overpass deferred

Synthetic fallback: NOT activated — real data sources still available.
```
