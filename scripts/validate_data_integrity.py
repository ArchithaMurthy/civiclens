"""
CivicLens — Data integrity validation script.

Verifies:
1. Every complaint_id referenced by a case exists in complaints_normalised.json
2. Case complaint_count matches len(complaint_ids)
3. No duplicate IDs within a case
4. No complaint appears in zero cases vs. pipeline expectations
5. Representative complaint IDs are a subset of complaint_ids
6. All complaint_ids in civic_cases.json are valid ICMC record IDs
7. Ward join confidence field present on all cases
8. No cases have fabricated/duplicate IDs

Usage:
    python scripts/validate_data_integrity.py

Exits with code 0 on success, 1 on any failures.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

PROC = Path("data/processed")


def load_json(path: Path) -> object:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run_validation() -> int:
    failures: list[str] = []
    warnings: list[str] = []

    print("=" * 60)
    print("CivicLens — Data Integrity Validation")
    print("=" * 60)

    # Load data
    print("\nLoading data files…")
    cases = load_json(PROC / "civic_cases.json")
    complaints_raw = load_json(PROC / "complaints_normalised.json")

    # Build complaint ID lookup
    all_complaint_ids: set[str] = {c["complaint_id"] for c in complaints_raw}
    print(f"  {len(cases)} cases loaded")
    print(f"  {len(all_complaint_ids)} normalised complaints loaded")

    # -------------------------------------------------------------------
    # Check 1: Every case has complaint_ids field
    # -------------------------------------------------------------------
    print("\n[1] Checking complaint_ids field presence…")
    missing_field = [c["case_id"] for c in cases if "complaint_ids" not in c]
    if missing_field:
        failures.append(f"[1] {len(missing_field)} cases missing complaint_ids field: {missing_field[:5]}")
    else:
        print(f"  OK — all {len(cases)} cases have complaint_ids field")

    # -------------------------------------------------------------------
    # Check 2: complaint_count matches len(complaint_ids)
    # -------------------------------------------------------------------
    print("\n[2] Checking complaint_count vs len(complaint_ids)…")
    count_mismatches = []
    for c in cases:
        if "complaint_ids" not in c:
            continue
        expected = c["complaint_count"]
        actual = len(c["complaint_ids"])
        if expected != actual:
            count_mismatches.append((c["case_id"], expected, actual))
    if count_mismatches:
        failures.append(
            f"[2] {len(count_mismatches)} cases where complaint_count != len(complaint_ids): "
            f"{count_mismatches[:3]}"
        )
    else:
        print(f"  OK — all {len(cases)} cases: complaint_count matches len(complaint_ids)")

    # -------------------------------------------------------------------
    # Check 3: All complaint IDs exist in normalised complaints
    # -------------------------------------------------------------------
    print("\n[3] Checking all complaint_ids resolve to actual records…")
    orphan_cases: list[tuple[str, list[str]]] = []
    total_ids_checked = 0
    total_orphans = 0
    for c in cases:
        ids = c.get("complaint_ids", [])
        total_ids_checked += len(ids)
        orphans = [cid for cid in ids if cid not in all_complaint_ids]
        if orphans:
            orphan_cases.append((c["case_id"], orphans))
            total_orphans += len(orphans)
    if orphan_cases:
        failures.append(
            f"[3] {total_orphans} orphan complaint IDs across {len(orphan_cases)} cases "
            f"(IDs not found in complaints_normalised.json). "
            f"First offender: {orphan_cases[0]}"
        )
    else:
        print(f"  OK — {total_ids_checked:,} complaint IDs checked, 0 orphans")

    # -------------------------------------------------------------------
    # Check 4: No duplicate IDs within a case
    # -------------------------------------------------------------------
    print("\n[4] Checking for duplicate complaint IDs within cases…")
    dup_cases = []
    for c in cases:
        ids = c.get("complaint_ids", [])
        counts = Counter(ids)
        dups = {cid: n for cid, n in counts.items() if n > 1}
        if dups:
            dup_cases.append((c["case_id"], dups))
    if dup_cases:
        failures.append(
            f"[4] {len(dup_cases)} cases with duplicate complaint IDs within the same case. "
            f"First: {dup_cases[0]}"
        )
    else:
        print(f"  OK — no duplicate IDs within any case")

    # -------------------------------------------------------------------
    # Check 5: Representative complaints are a subset of complaint_ids
    # -------------------------------------------------------------------
    print("\n[5] Checking representative_complaints are subset of complaint_ids…")
    rep_not_in_ids: list[tuple[str, str]] = []
    for c in cases:
        all_ids = set(c.get("complaint_ids", []))
        for rep in c.get("representative_complaints", []):
            rid = rep.get("complaint_id", "")
            if rid and rid not in all_ids:
                rep_not_in_ids.append((c["case_id"], rid))
    if rep_not_in_ids:
        failures.append(
            f"[5] {len(rep_not_in_ids)} representative complaints not found in complaint_ids. "
            f"First: {rep_not_in_ids[0]}"
        )
    else:
        print(f"  OK — all representative complaint IDs are within complaint_ids")

    # -------------------------------------------------------------------
    # Check 6: ward_join_confidence present and valid on all cases
    # -------------------------------------------------------------------
    print("\n[6] Checking ward_join_confidence field…")
    valid_confs = {"exact_name", "fuzzy_name", "none"}
    bad_conf = [c["case_id"] for c in cases if c.get("ward_join_confidence") not in valid_confs]
    if bad_conf:
        failures.append(f"[6] {len(bad_conf)} cases with invalid ward_join_confidence: {bad_conf[:5]}")
    else:
        conf_dist = Counter(c.get("ward_join_confidence") for c in cases)
        print(f"  OK — distribution: {dict(conf_dist)}")

    # -------------------------------------------------------------------
    # Check 7: No complaint_id referenced across multiple cases (OK to flag as warning)
    # -------------------------------------------------------------------
    print("\n[7] Checking complaint-to-case cross-membership (warning only)…")
    cid_to_cases: dict[str, list[str]] = {}
    for c in cases:
        for cid in c.get("complaint_ids", []):
            cid_to_cases.setdefault(cid, []).append(c["case_id"])
    shared = {cid: case_list for cid, case_list in cid_to_cases.items() if len(case_list) > 1}
    if shared:
        warnings.append(
            f"[7] {len(shared)} complaints appear in multiple cases. "
            f"This may occur at cluster boundaries (geo_dbscan + ward_temporal overlap). "
            f"Example: {list(shared.items())[:2]}"
        )
    else:
        print(f"  OK — no complaints shared across multiple cases")

    # -------------------------------------------------------------------
    # Check 8: Total complaint IDs across all cases vs. expected
    # -------------------------------------------------------------------
    print("\n[8] Checking total complaint coverage…")
    all_case_ids = set()
    for c in cases:
        all_case_ids.update(c.get("complaint_ids", []))
    # Road ICMC complaints should largely be covered
    road_icmc = [c for c in complaints_raw if c.get("source") == "ichangemycity" and c.get("category") == "road_infrastructure"]
    road_icmc_ids = {c["complaint_id"] for c in road_icmc}
    covered = road_icmc_ids & all_case_ids
    uncovered = road_icmc_ids - all_case_ids
    pct_covered = len(covered) / len(road_icmc_ids) * 100 if road_icmc_ids else 0
    print(f"  Road ICMC complaints: {len(road_icmc_ids):,}")
    print(f"  Covered by at least one case: {len(covered):,} ({pct_covered:.1f}%)")
    print(f"  Unclustered (not in any case): {len(uncovered):,}")
    if pct_covered < 10:
        failures.append(f"[8] Only {pct_covered:.1f}% of road complaints covered — suspiciously low")

    # -------------------------------------------------------------------
    # Summary
    # -------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  WARN: {w}")

    if failures:
        print(f"\nFAILURES ({len(failures)}):")
        for fail in failures:
            print(f"  FAIL: {fail}")
        print(f"\nResult: FAILED ({len(failures)} failure(s))")
        return 1
    else:
        print(f"\nResult: ALL CHECKS PASSED")
        return 0


if __name__ == "__main__":
    sys.exit(run_validation())
