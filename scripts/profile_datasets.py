"""
CivicLens Sprint 1 — Dataset Profiling Script
Profiles all CSV and JSON files in data/raw/.
Uses stdlib only: csv, json, collections, datetime, os.
Output: stdout (redirect to data/metadata/dataset_profiles.md)
"""
import csv
import json
import os
import collections
from datetime import datetime

RAW_DIR = "data/raw"
ENCODING_FALLBACKS = ["utf-8", "cp1252", "latin-1"]


def try_read_csv(path):
    for enc in ENCODING_FALLBACKS:
        try:
            with open(path, encoding=enc, errors="replace") as f:
                rows = list(csv.DictReader(f))
            return rows, enc
        except Exception:
            continue
    return None, None


def try_read_json(path):
    for enc in ENCODING_FALLBACKS:
        try:
            with open(path, encoding=enc, errors="replace") as f:
                data = json.load(f)
            return data, enc
        except Exception:
            continue
    return None, None


def null_rate(values, total):
    nulls = sum(1 for v in values if v is None or str(v).strip() in ("", "NULL", "null", "None"))
    return nulls, round(nulls * 100 / total, 1) if total else 0


def profile_csv(path):
    fname = os.path.basename(path)
    size = os.path.getsize(path)
    rows, enc = try_read_csv(path)
    if rows is None:
        return f"\n### {fname}\n\n> **ERROR:** Could not read file.\n"

    total = len(rows)
    if total == 0:
        return f"\n### {fname}\n\n> **Empty file.**\n"

    cols = list(rows[0].keys())
    lines = [
        f"\n### {fname}",
        f"",
        f"| Property | Value |",
        f"|---|---|",
        f"| **File** | `{fname}` |",
        f"| **Size** | {size:,} bytes ({round(size/1024, 1)} KB) |",
        f"| **Encoding** | {enc} |",
        f"| **Rows** | {total:,} |",
        f"| **Columns** | {len(cols)} |",
        f"",
        f"**Columns:**",
        f"",
    ]
    for c in cols:
        vals = [r.get(c, "") for r in rows]
        n_null, pct_null = null_rate(vals, total)
        n_distinct = len(set(str(v) for v in vals if str(v).strip() not in ("", "NULL", "null")))
        lines.append(f"- `{c}` — {total - n_null:,} populated ({pct_null}% missing) | {n_distinct:,} distinct values")

    # Date range detection
    date_cols = [c for c in cols if any(x in c.lower() for x in ("date", "created", "updated", "at", "time", "year"))]
    if date_cols:
        lines.append(f"\n**Date fields detected:** {', '.join(date_cols)}")
        dc = date_cols[0]
        date_vals = [r.get(dc, "") for r in rows if r.get(dc) and str(r.get(dc, "")).strip()]
        if date_vals:
            date_vals_sorted = sorted(date_vals)
            lines.append(f"- `{dc}` range: `{date_vals_sorted[0]}` to `{date_vals_sorted[-1]}`")

    # Category distribution
    cat_cols = [c for c in cols if any(x in c.lower() for x in ("category", "type", "status", "agency", "zone", "ward"))]
    for cc in cat_cols[:3]:
        dist = collections.Counter(r.get(cc, "") for r in rows if r.get(cc) and str(r.get(cc, "")).strip())
        if dist:
            lines.append(f"\n**`{cc}` distribution (top 10):**")
            lines.append(f"")
            lines.append(f"| Value | Count |")
            lines.append(f"|---|---|")
            for val, cnt in dist.most_common(10):
                lines.append(f"| {val} | {cnt:,} |")

    # Geographic coverage
    lat_col = next((c for c in cols if "lat" in c.lower()), None)
    lon_col = next((c for c in cols if "lon" in c.lower()), None)
    if lat_col and lon_col:
        lats = []
        lons = []
        for r in rows:
            try:
                lats.append(float(r.get(lat_col, "")))
                lons.append(float(r.get(lon_col, "")))
            except (ValueError, TypeError):
                pass
        if lats:
            lines.append(f"\n**Geographic coverage:**")
            lines.append(f"- Latitude: {min(lats):.4f} to {max(lats):.4f}")
            lines.append(f"- Longitude: {min(lons):.4f} to {max(lons):.4f}")
            lines.append(f"- Records with valid GPS: {len(lats):,} / {total:,}")

    # Duplicate check
    id_col = next((c for c in cols if c.lower() in ("id", "complaint_id", "work_order_id", "tweet_id")), None)
    if id_col:
        ids = [r.get(id_col, "") for r in rows if r.get(id_col, "").strip()]
        dup_ids = len(ids) - len(set(ids))
        lines.append(f"\n**Duplicate IDs (`{id_col}`):** {dup_ids}")

    return "\n".join(lines)


def profile_json_array(path, data):
    fname = os.path.basename(path)
    size = os.path.getsize(path)
    total = len(data) if isinstance(data, list) else 0
    if total == 0:
        # Try to find array within object
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, list) and len(v) > 0:
                    data = v
                    total = len(data)
                    break
    if total == 0:
        return f"\n### {fname}\n\n> **Empty or non-array JSON.**\n"

    sample = data[0] if isinstance(data[0], dict) else {}
    cols = list(sample.keys())

    lines = [
        f"\n### {fname}",
        f"",
        f"| Property | Value |",
        f"|---|---|",
        f"| **File** | `{fname}` |",
        f"| **Size** | {size:,} bytes ({round(size/1024/1024, 2)} MB) |",
        f"| **Records** | {total:,} |",
        f"| **Fields (sample)** | {len(cols)} |",
        f"",
        f"**Fields in first record:** {', '.join(f'`{c}`' for c in cols)}",
        f"",
    ]

    # Category/status distributions
    for cc in cols:
        vals = [str(r.get(cc, "")) for r in data if isinstance(r, dict)]
        non_null = [v for v in vals if v not in ("", "None", "null", "NULL")]
        if 1 < len(set(non_null)) <= 30:  # only show categorical columns
            dist = collections.Counter(non_null)
            if len(dist) <= 20:
                lines.append(f"**`{cc}` distribution:**")
                lines.append(f"")
                lines.append(f"| Value | Count |")
                lines.append(f"|---|---|")
                for val, cnt in dist.most_common(10):
                    lines.append(f"| {val} | {cnt:,} |")
                lines.append(f"")

    # Date range
    date_cols = [c for c in cols if any(x in c.lower() for x in ("date", "created", "at", "time"))]
    for dc in date_cols[:1]:
        date_vals = sorted([str(r.get(dc, "")) for r in data if isinstance(r, dict) and r.get(dc)])
        if date_vals:
            lines.append(f"**`{dc}` range:** `{date_vals[0]}` to `{date_vals[-1]}`")
            lines.append(f"")

    # Null check on key fields
    lines.append(f"**Null/missing rates:**")
    lines.append(f"")
    for c in cols:
        vals = [r.get(c) for r in data if isinstance(r, dict)]
        n_null, pct = null_rate(vals, total)
        if pct > 5:
            lines.append(f"- `{c}`: {pct}% missing")

    return "\n".join(lines)


def profile_json_work_orders(path, data):
    """Special profiler for the KAUN work orders nested JSON."""
    fname = os.path.basename(path)
    size = os.path.getsize(path)
    meta = data.get("metadata", {})
    work_orders = data.get("work_orders", [])
    total = len(work_orders)

    if total == 0:
        return f"\n### {fname}\n\n> **Empty work_orders array.**\n"

    sample = work_orders[0] if work_orders else {}
    cols = list(sample.keys())

    lines = [
        f"\n### {fname}",
        f"",
        f"| Property | Value |",
        f"|---|---|",
        f"| **File** | `{fname}` |",
        f"| **Size** | {size:,} bytes ({round(size/1024/1024, 2)} MB) |",
        f"| **Work Orders** | {total:,} |",
        f"| **Wards Fetched** | {meta.get('wards_fetched', 'unknown')} |",
        f"| **Source** | {meta.get('source', 'unknown')} |",
        f"| **License** | {meta.get('license', 'unknown')} |",
        f"| **Attribution** | {meta.get('attribution', 'unknown')} |",
        f"",
        f"**Fields:** {', '.join(f'`{c}`' for c in cols)}",
        f"",
    ]

    # Fiscal year distribution
    fy_dist = collections.Counter(r.get("fy", "") for r in work_orders if r.get("fy"))
    lines.append("**Fiscal year distribution:**")
    lines.append("")
    lines.append("| FY | Count |")
    lines.append("|---|---|")
    for k, v in sorted(fy_dist.items()):
        lines.append(f"| {k} | {v:,} |")
    lines.append("")

    # Ward class distribution
    wc_dist = collections.Counter(r.get("ward_class", "") for r in work_orders)
    lines.append("**Ward class distribution:**")
    lines.append("")
    lines.append("| Ward Class | Count |")
    lines.append("|---|---|")
    for k, v in wc_dist.most_common():
        lines.append(f"| {k or '(ward-specific)'} | {v:,} |")
    lines.append("")

    # Amount stats
    amounts = [r.get("sanctioned_amount") for r in work_orders if r.get("sanctioned_amount")]
    amounts = [a for a in amounts if isinstance(a, (int, float)) and a > 0]
    if amounts:
        total_amt = sum(amounts)
        lines.append(f"**Sanctioned amounts:**")
        lines.append(f"- Total: ₹{total_amt/10000000:,.2f} crore")
        lines.append(f"- Average: ₹{(total_amt/len(amounts))/100000:,.1f} lakh")
        lines.append(f"- Records with amount: {len(amounts):,} / {total:,}")
        lines.append(f"")

    # Missing rates
    lines.append("**Null/missing rates:**")
    lines.append("")
    for c in cols:
        vals = [r.get(c) for r in work_orders]
        n_null, pct = null_rate(vals, total)
        if pct > 5:
            lines.append(f"- `{c}`: {pct}% missing")

    return "\n".join(lines)


def main():
    print("# CivicLens Sprint 1 — Dataset Profiles")
    print("")
    print(f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"> Source directory: `{RAW_DIR}/`")
    print("")
    print("---")

    files = sorted(os.listdir(RAW_DIR))
    csv_files = [f for f in files if f.endswith(".csv")]
    json_files = [f for f in files if f.endswith(".json")]

    print("\n## CSV Datasets\n")
    for fname in csv_files:
        if fname == ".gitkeep":
            continue
        path = os.path.join(RAW_DIR, fname)
        print(profile_csv(path))

    print("\n---\n")
    print("## JSON Datasets\n")
    for fname in json_files:
        if fname == ".gitkeep":
            continue
        path = os.path.join(RAW_DIR, fname)
        data, enc = try_read_json(path)
        if data is None:
            print(f"\n### {fname}\n\n> **ERROR reading file.**\n")
            continue

        # Dispatch to appropriate profiler
        if isinstance(data, dict) and "work_orders" in data:
            print(profile_json_work_orders(path, data))
        elif isinstance(data, dict) and "data" in data:
            print(profile_json_array(path, data["data"]))
        elif isinstance(data, list):
            print(profile_json_array(path, data))
        else:
            keys = list(data.keys())[:5]
            print(f"\n### {fname}\n\n| Property | Value |\n|---|---|\n| **Top-level keys** | {', '.join(keys)} |\n")


if __name__ == "__main__":
    main()
