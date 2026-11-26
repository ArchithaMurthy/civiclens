import json

with open('data/processed/civic_cases.json', encoding='utf-8') as f:
    cases = json.load(f)

print('Case JSON fields:', list(cases[0].keys()))
rc = cases[0].get('representative_complaints', [])
print('representative_complaints count:', len(rc))
print('rep_complaints[0] keys:', list(rc[0].keys()) if rc else 'EMPTY')
print('complaint_ids in case[0]:', 'complaint_ids' in cases[0])

top = max(cases, key=lambda c: c['priority_score'])
print()
print('Top case:', top['case_id'])
print('  complaint_count:', top['complaint_count'])
print('  ward:', top['primary_ward_name'])
print('  years:', top['years_active'])
print('  score:', top['priority_score'])
print('  unresolved_rate_pct:', top['unresolved_rate_pct'])
print('  open_count:', top['open_count'])
print('  resolved_count:', top['resolved_count'])
print('  reopened_count:', top['reopened_count'])
print('  evidence items count:', len(top.get('evidence_items', [])))
print('  rep_complaints count:', len(top.get('representative_complaints', [])))
print()
print('Evidence items:')
for e in top.get('evidence_items', []):
    etype = e.get('type','?')
    edesc = e.get('description','')[:120]
    esrc = e.get('source','?')
    etrace = e.get('traceable_to','?')
    print(f'  TYPE={etype}')
    print(f'  DESC={edesc}')
    print(f'  SRC={esrc}')
    print(f'  TRACE={etrace}')
    print()

print('Hypotheses:')
for h in top.get('hypotheses', []):
    print(f'  {h[:300]}')
print()
print('Priority factors:', top.get('priority_factors'))
print('Cluster confidence:', top.get('cluster_confidence'))
print('Ward join note:', top.get('ward_join_note'))
print()
# Show rep complaints
print('Representative complaints:')
for rc_item in top.get('representative_complaints', []):
    print('  id=%s ward=%s sub=%s status=%s lat=%s lon=%s' % (
        rc_item.get('complaint_id','?'),
        rc_item.get('ward_name','?'),
        rc_item.get('subcategory','?'),
        rc_item.get('status','?'),
        rc_item.get('latitude','?'),
        rc_item.get('longitude','?')
    ))
    print('  desc:', (rc_item.get('description_excerpt','') or '')[:120])
    print()
