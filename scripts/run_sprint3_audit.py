"""
Sprint 3 Phase 2+3: Deep audit of dedup, clusters, cases, priority, and the Begur case.
Writes findings to data/processed/sprint3_audit_data.json
"""
import json, csv, collections, math
from pathlib import Path

RAW = Path('data/raw')
PROC = Path('data/processed')

# ---------------------------------------------------------------------------
# Load all data
# ---------------------------------------------------------------------------
with open(PROC / 'complaints_normalised.json', encoding='utf-8') as f:
    complaints = json.load(f)
complaints_by_id = {c['complaint_id']: c for c in complaints}

with open(PROC / 'civic_cases.json', encoding='utf-8') as f:
    cases = json.load(f)
cases_by_id = {c['case_id']: c for c in cases}

with open(PROC / 'dedup_candidates.json', encoding='utf-8') as f:
    dedup = json.load(f)

with open(RAW / 'ichangemycity_complaints.csv', encoding='cp1252', errors='replace') as f:
    raw_icmc = list(csv.DictReader(f))
raw_by_title_ward = collections.defaultdict(list)
for r in raw_icmc:
    raw_by_title_ward[(r.get('ward_title',''), r.get('sub_category_title',''))].append(r)

with open(RAW / 'kaun_ward_metrics.csv', encoding='utf-8') as f:
    ward_metrics = list(csv.DictReader(f))
ward_metrics_by_no = {int(r['ward_no']): r for r in ward_metrics if r.get('ward_no','').isdigit()}

with open(RAW / 'kaun_ward_crosswalk.csv', encoding='utf-8') as f:
    crosswalk = list(csv.DictReader(f))
crosswalk_by_bbmp225 = {int(r['bbmp225_no']): r for r in crosswalk if r.get('bbmp225_no','').isdigit()}

audit = {}

# ---------------------------------------------------------------------------
# 2.1 Dedup audit
# ---------------------------------------------------------------------------
exact = [d for d in dedup if d['duplicate_type'] == 'duplicate']
near = [d for d in dedup if d['duplicate_type'] == 'near_duplicate']

# Inspect exact duplicates: are they truly identical text in same ward?
identical_text_same_location = 0
identical_text_different_gps = 0
identical_text_no_gps = 0
same_desc_different_subcat = 0
different_ward_same_desc = 0

for d in exact:
    ca = complaints_by_id.get(d['complaint_id_a'], {})
    cb = complaints_by_id.get(d['complaint_id_b'], {})
    desc_a = (ca.get('description') or '').strip()
    desc_b = (cb.get('description') or '').strip()
    ward_a = ca.get('ward_id')
    ward_b = cb.get('ward_id')
    sub_a = ca.get('subcategory','')
    sub_b = cb.get('subcategory','')
    
    if ward_a != ward_b:
        different_ward_same_desc += 1
    if sub_a != sub_b:
        same_desc_different_subcat += 1
    
    lat_a, lon_a = ca.get('latitude'), ca.get('longitude')
    lat_b, lon_b = cb.get('latitude'), cb.get('longitude')
    
    if lat_a and lat_b and d.get('distance_km') is not None:
        if d['distance_km'] * 1000 <= 50:
            identical_text_same_location += 1
        else:
            identical_text_different_gps += 1
    else:
        identical_text_no_gps += 1

# Sample 5 exact duplicates for display
sample_exact = []
for d in exact[:5]:
    ca = complaints_by_id.get(d['complaint_id_a'], {})
    cb = complaints_by_id.get(d['complaint_id_b'], {})
    sample_exact.append({
        'pair': [d['complaint_id_a'], d['complaint_id_b']],
        'confidence': d['confidence'],
        'signals': d['signals'],
        'days_apart': d.get('days_apart'),
        'distance_km': d.get('distance_km'),
        'ward_a': ca.get('ward_name'), 'ward_b': cb.get('ward_name'),
        'subcat_a': ca.get('subcategory'), 'subcat_b': cb.get('subcategory'),
        'desc_a': (ca.get('description') or '')[:200],
        'desc_b': (cb.get('description') or '')[:200],
        'created_at_a': ca.get('created_at_raw'), 'created_at_b': cb.get('created_at_raw'),
        'same_description': (ca.get('description') or '').strip() == (cb.get('description') or '').strip(),
    })

# Near-dup analysis: how many have GPS proximity signal?
near_with_gps = [d for d in near if 'gps_within_200m' in d.get('signals',[]) or 'gps_within_50m' in d.get('signals',[])]
near_text_only = [d for d in near if 'identical_description' in d.get('signals',[]) and not any('gps' in s for s in d.get('signals',[]))]
near_no_text = [d for d in near if 'identical_description' not in d.get('signals',[])]

audit['dedup'] = {
    'exact_total': len(exact),
    'exact_identical_text_close_gps': identical_text_same_location,
    'exact_identical_text_distant_gps': identical_text_different_gps,
    'exact_identical_text_no_gps': identical_text_no_gps,
    'exact_different_ward': different_ward_same_desc,
    'exact_different_subcat': same_desc_different_subcat,
    'near_total': len(near),
    'near_with_gps_signal': len(near_with_gps),
    'near_text_only': len(near_text_only),
    'near_no_text': len(near_no_text),
    'sample_exact': sample_exact,
}

# ---------------------------------------------------------------------------
# 2.2 Cluster quality
# ---------------------------------------------------------------------------
geo_cases = [c for c in cases if c['cluster_method'] == 'geo_dbscan']
ward_cases = [c for c in cases if c['cluster_method'] == 'ward_temporal']

# Geographic extent analysis
extents = [(c['case_id'], c.get('geographic_extent_km'), c['complaint_count']) 
           for c in geo_cases if c.get('geographic_extent_km')]
large_extent = [e for e in extents if e[1] > 1.0]
very_large_extent = [e for e in extents if e[1] > 1.5]

# Multi-ward clusters (potential false merge)
multi_ward = [c for c in cases if len(c.get('all_ward_names', [])) > 2]
# Single-complaint clusters
tiny_clusters = [c for c in cases if c['complaint_count'] < 5]
# High unresolved rate
very_high_unresolved = [c for c in cases if c['unresolved_rate_pct'] >= 80]
# Zero resolved (might indicate status data quality issue)
all_open = [c for c in cases if c['resolved_count'] == 0]

# Ward join quality
crosswalk_joins = [c for c in cases if 'crosswalk' in c.get('ward_join_note','')]
approx_joins = [c for c in cases if 'approximate' in c.get('ward_join_note','')]
low_overlap_joins = []
for c in crosswalk_joins:
    # Extract overlap_confidence from note string
    note = c.get('ward_join_note','')
    if 'overlap_confidence=' in note:
        try:
            oc_str = note.split('overlap_confidence=')[1].rstrip(')')
            oc = float(oc_str)
            if oc < 0.5:
                low_overlap_joins.append({'case_id': c['case_id'], 'overlap_confidence': oc, 'ward': c.get('primary_ward_name')})
        except: pass

audit['cluster_quality'] = {
    'total_clusters': len(cases),
    'geo_clusters': len(geo_cases),
    'ward_clusters': len(ward_cases),
    'geo_large_extent_gt_1km': len(large_extent),
    'geo_very_large_extent_gt_1p5km': len(very_large_extent),
    'top5_largest_extent': sorted(extents, key=lambda x: -(x[1] or 0))[:5],
    'multi_ward_clusters_gt2': len(multi_ward),
    'tiny_clusters_lt5': len(tiny_clusters),
    'all_open_no_resolved': len(all_open),
    'very_high_unresolved_gt80pct': len(very_high_unresolved),
    'crosswalk_joins': len(crosswalk_joins),
    'approx_joins': len(approx_joins),
    'low_overlap_confidence_lt50pct': len(low_overlap_joins),
    'low_overlap_sample': low_overlap_joins[:5],
}

# ---------------------------------------------------------------------------
# 2.3 Case quality: HIGH priority cases
# ---------------------------------------------------------------------------
high_cases = [c for c in cases if c['priority_tier'] == 'HIGH']
case_quality = []
for c in high_cases:
    # Check completeness
    has_title = bool(c.get('problem_title'))
    has_summary = bool(c.get('problem_summary'))
    has_dates = bool(c.get('date_first_complaint')) and bool(c.get('date_last_complaint'))
    has_ward = bool(c.get('primary_ward_name'))
    has_agency = bool(c.get('responsible_agency'))
    has_evidence = len(c.get('evidence_items',[])) >= 2
    has_next_steps = len(c.get('recommended_next_steps',[])) >= 1
    has_rep_complaints = len(c.get('representative_complaints',[])) >= 3
    
    # Check evidence consistency: open+resolved+reopened == complaint_count?
    reported_total = c['open_count'] + c['resolved_count'] + c['reopened_count']
    # Note: "in_progress" and "rejected" statuses not in these three counts
    reported_total_vs_count = abs(reported_total - c['complaint_count'])
    
    # Check centroid in BBMP bounds
    lat = c.get('centroid_lat')
    lon = c.get('centroid_lon')
    centroid_valid = (lat and lon and 12.70 <= lat <= 13.20 and 77.40 <= lon <= 77.85) if lat else True
    
    # Agency attribution strength
    agency_note = c.get('agency_attribution_note','')
    
    case_quality.append({
        'case_id': c['case_id'],
        'ward': c.get('primary_ward_name'),
        'score': c['priority_score'],
        'complaint_count': c['complaint_count'],
        'years': c['years_active'],
        'unresolved_pct': c['unresolved_rate_pct'],
        'has_title': has_title,
        'has_summary': has_summary,
        'has_dates': has_dates,
        'has_ward': has_ward,
        'has_agency': has_agency,
        'has_evidence_ge2': has_evidence,
        'has_next_steps': has_next_steps,
        'has_rep_complaints_ge3': has_rep_complaints,
        'open_plus_resolved_plus_reopened': reported_total,
        'complaint_count': c['complaint_count'],
        'status_sum_gap': reported_total_vs_count,
        'centroid_valid': centroid_valid,
        'ward_join_note_excerpt': c.get('ward_join_note','')[:80],
    })

audit['case_quality'] = case_quality

# ---------------------------------------------------------------------------
# 2.4 Priority model audit
# ---------------------------------------------------------------------------
# Check if crash_risk factor is inflating scores for large-ward cases
crash_inflated = [c for c in cases if c.get('priority_factors',{}).get('crash_risk',0) >= 0.5]
high_crash_low_complaint = [c for c in crash_inflated if c['complaint_count'] < 15]

# Check recurrence_years saturation (many cases hit 4-year max = score 1.0)
max_recurrence = [c for c in cases if c.get('priority_factors',{}).get('recurrence_years',0) >= 1.0]

# Cases where crash_risk alone elevates to HIGH tier
score_without_crash = []
for c in cases[:20]:
    pf = c.get('priority_factors',{})
    # Remove crash_risk weight (0.10) and re-normalise
    score_no_crash = sum(v * {'complaint_volume':0.278,'recurrence_years':0.278,'unresolved_rate':0.222,'reopened_rate':0.111,'description_severity':0.111}.get(k,0) for k,v in pf.items() if k != 'crash_risk')
    score_without_crash.append({'case_id': c['case_id'], 'score': c['priority_score'], 'score_no_crash': round(score_no_crash,3), 'crash_factor': pf.get('crash_risk',0)})

audit['priority_audit'] = {
    'cases_with_high_crash_factor': len(crash_inflated),
    'high_crash_low_complaint_lt15': len(high_crash_low_complaint),
    'cases_at_max_recurrence_years': len(max_recurrence),
    'sample_score_without_crash': score_without_crash[:10],
    'scoring_weights': {'complaint_volume':0.25,'recurrence_years':0.25,'unresolved_rate':0.20,'reopened_rate':0.10,'crash_risk':0.10,'description_severity':0.10},
    'tier_thresholds': {'HIGH': 0.50, 'MEDIUM': 0.30, 'LOW': 0.0},
}

# ---------------------------------------------------------------------------
# 2.5 Evidence traceability
# ---------------------------------------------------------------------------
evidence_types_all = collections.Counter()
for c in cases:
    for e in c.get('evidence_items',[]):
        evidence_types_all[e.get('type','')] += 1

# Check: do ALL cases have traceable_to fields?
missing_trace = sum(1 for c in cases for e in c.get('evidence_items',[]) if not e.get('traceable_to'))

audit['evidence_traceability'] = {
    'evidence_type_distribution': dict(evidence_types_all),
    'evidence_items_missing_traceable_to': missing_trace,
    'cases_missing_complaint_ids': sum(1 for c in cases if 'complaint_ids' not in c),
    'note': 'complaint_ids field not stored in civic_cases.json — cannot trace individual complaints from case JSON alone',
}

# ---------------------------------------------------------------------------
# Phase 3: Begur case deep audit
# ---------------------------------------------------------------------------
top_case = max(cases, key=lambda c: c['priority_score'])
print('Top case cluster_id:', top_case['cluster_id'])
print('Primary ward ID:', top_case['primary_ward_id'])

# Get all Begur complaints from ICMC
begur_all = [c for c in complaints if 'Begur' in (c.get('ward_name') or '') and c['source'] == 'ichangemycity']
begur_road = [c for c in begur_all if c['category'] == 'road_infrastructure']
print('Total Begur ICMC complaints:', len(begur_all))
print('Begur road complaints:', len(begur_road))

# Get all Begur complaints matching ward_id of top case
begur_by_id = [c for c in complaints if c.get('ward_id') == top_case['primary_ward_id'] and c['source'] == 'ichangemycity']
print('Complaints at ward_id=%d: %d' % (top_case['primary_ward_id'] or 0, len(begur_by_id)))

# Understand the GEO-0044 cluster
# Since complaint_ids not in case JSON, reconstruct from cluster
# by matching representative_complaints
rep_complaints = top_case.get('representative_complaints', [])
rep_ids = [r['complaint_id'] for r in rep_complaints]
print('Representative complaint IDs:', rep_ids)
print()

# GPS spread of representative complaints
print('Rep complaint GPS:')
for r in rep_complaints:
    print('  %s lat=%.4f lon=%.4f sub=%s status=%s' % (
        r['complaint_id'], r.get('latitude',0) or 0, r.get('longitude',0) or 0,
        r.get('subcategory','?')[:30], r.get('status','?')))

# Subcategory distribution for the case
sub_dist_rep = collections.Counter(r.get('subcategory','') for r in rep_complaints)
print('Subcategory dist (rep):', dict(sub_dist_rep))

# Ward join for Begur
ward_id = top_case['primary_ward_id']
print()
print('Ward join note:', top_case.get('ward_join_note'))
if ward_id in crosswalk_by_bbmp225:
    cw = crosswalk_by_bbmp225[ward_id]
    print('Crosswalk entry:', cw)

# Check KAUN ward metrics for the mapped datameet243 ID
# Top case maps ICMC ward 192 -> datameet243 204
# Get ward name for 204
mapped_id = None
note = top_case.get('ward_join_note','')
if 'datameet243=' in note:
    try:
        mapped_id = int(note.split('datameet243=')[1].split(' ')[0])
    except: pass
print('Mapped datameet243_no:', mapped_id)
if mapped_id and mapped_id in ward_metrics_by_no:
    wm = ward_metrics_by_no[mapped_id]
    print('Ward metrics for datameet243=%d:' % mapped_id)
    print('  ward_name:', wm.get('ward_name'))
    print('  pothole_complaints:', wm.get('pothole_complaints'))
    print('  spend_roads_and_infrastructure:', wm.get('spend_roads_and_infrastructure'))
    print('  road_crashes_2024:', wm.get('road_crashes_2024'))
    print('  fatal_crashes_2024:', wm.get('fatal_crashes_2024'))

# Check if Begur (ward 192) is the same as datameet243=204
if 192 in crosswalk_by_bbmp225:
    cw192 = crosswalk_by_bbmp225[192]
    print()
    print('Crosswalk bbmp225=192:')
    for k,v in cw192.items():
        print('  %s: %s' % (k, v))

# Check raw ICMC complaints for Begur/ward_id=192
raw_begur = [r for r in raw_icmc if r.get('ward_id') == '192']
print()
print('Raw ICMC rows with ward_id=192:', len(raw_begur))
raw_begur_road = [r for r in raw_begur if 'Mobility' in r.get('category_title','') or 'Road' in r.get('category_title','')]
print('Road complaints at ward_id=192:', len(raw_begur_road))
subcat_192 = collections.Counter(r.get('sub_category_title','') for r in raw_begur_road)
print('Subcategories at ward 192 (road):')
for k,v in subcat_192.most_common(10):
    print('  %4d  %s' % (v, k))

# Status breakdown
status_192 = collections.Counter(r.get('complaint_status_title','') for r in raw_begur_road)
print('Status at ward 192 (road):', dict(status_192))

# Year distribution
import re
year_192 = collections.Counter(re.search(r'(201\d|202\d)', r.get('created_at','')).group(1) 
                                 if re.search(r'(201\d|202\d)', r.get('created_at','')) else 'unknown'
                                 for r in raw_begur_road)
print('Year dist at ward 192 (road):', dict(sorted(year_192.items())))

# GPS spread of ward 192 road complaints
lats = [float(r['latitude']) for r in raw_begur_road if r.get('latitude')]
lons = [float(r['longitude']) for r in raw_begur_road if r.get('longitude')]
if lats:
    print('GPS range ward 192 road: lat %.4f-%.4f lon %.4f-%.4f' % (min(lats), max(lats), min(lons), max(lons)))

# How many distinct description texts?
descs_192 = set(r.get('description','').strip() for r in raw_begur_road if r.get('description','').strip())
print('Distinct descriptions at ward 192 (road):', len(descs_192))
print('Total road complaints at ward 192:', len(raw_begur_road))
print('Duplicate descriptions:', len(raw_begur_road) - len(descs_192))

begur_audit = {
    'top_case_id': top_case['case_id'],
    'reported_cluster_id': top_case['cluster_id'],
    'reported_ward': top_case['primary_ward_name'],
    'reported_primary_ward_id': top_case['primary_ward_id'],
    'reported_complaint_count': top_case['complaint_count'],
    'ward_join_note': top_case.get('ward_join_note',''),
    'mapped_datameet243': mapped_id,
    'raw_icmc_ward192_total': len(raw_begur),
    'raw_icmc_ward192_road': len(raw_begur_road),
    'raw_icmc_ward192_road_distinct_descs': len(descs_192),
    'raw_icmc_ward192_road_duplicated_descs': len(raw_begur_road) - len(descs_192),
    'subcategory_dist': dict(subcat_192),
    'status_dist': dict(status_192),
    'year_dist': dict(sorted(year_192.items())),
    'gps_range': {'lat_min': min(lats), 'lat_max': max(lats), 'lon_min': min(lons), 'lon_max': max(lons)} if lats else None,
    'gap_complaint_ids_not_in_case_json': True,
    'note_on_cluster': 'GEO-0044 is a DBSCAN geographic cluster — it groups complaints within 300m radius across multiple years. The 56 complaint_count comes from the cluster builder, but the actual complaint IDs are not stored in civic_cases.json.',
}
audit['begur_case'] = begur_audit

# Save audit
with open(PROC / 'sprint3_audit_data.json', 'w', encoding='utf-8') as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)
print()
print('Saved sprint3_audit_data.json')
