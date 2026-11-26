import json
from pathlib import Path

cases = json.loads(Path('data/processed/civic_cases.json').read_text(encoding='utf-8'))
complaint_counts = sorted(c['complaint_count'] for c in cases)
n = len(complaint_counts)
print('Complaint count distribution:')
for p in [50, 75, 85, 90, 95, 99]:
    idx = min(int(p/100 * n), n-1)
    print(f'  P{p}: {complaint_counts[idx]}')
print(f'  Max: {complaint_counts[-1]}')
print(f'  Mean: {sum(complaint_counts)/n:.1f}')

# crash risk coverage
crashes = [c['priority_factors'].get('crash_risk', 0) for c in cases]
nonzero = sum(1 for x in crashes if x > 0)
print(f'\nCrash risk > 0: {nonzero}/{n} cases ({nonzero/n*100:.0f}%)')

# How many cases have description_severity > 0
sev = [c['priority_factors'].get('description_severity', 0) for c in cases]
nonzero_sev = sum(1 for x in sev if x > 0)
print(f'Description severity > 0: {nonzero_sev}/{n} cases ({nonzero_sev/n*100:.0f}%)')

# Average factor scores
print('\nMean factor scores:')
for k in ['complaint_volume','recurrence_years','unresolved_rate','reopened_rate','crash_risk','description_severity']:
    vals = [c['priority_factors'].get(k, 0) for c in cases]
    print(f'  {k}: {sum(vals)/n:.3f}')
