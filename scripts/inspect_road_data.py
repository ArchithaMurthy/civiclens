import csv, json, collections

rows = []
with open('data/raw/ichangemycity_complaints.csv', encoding='cp1252', errors='replace') as f:
    rows = list(csv.DictReader(f))

road_rows = [r for r in rows if r.get('category_title','') == 'Mobility - Roads, Footpaths and Infrastructure']
print(f'Road/mobility complaints: {len(road_rows)}')

sub = collections.Counter(r['sub_category_title'] for r in road_rows)
print('\nRoad subcategories:')
for k,v in sub.most_common(20):
    print(f'  {v:5d}  {k}')

status = collections.Counter(r['complaint_status_title'] for r in road_rows)
print('\nStatus for road complaints:')
for k,v in status.most_common():
    print(f'  {v:5d}  {k}')

agency = collections.Counter(r['civic_agency_title'] for r in road_rows if r.get('civic_agency_title'))
print('\nAgency for road complaints:')
for k,v in agency.most_common():
    print(f'  {v:5d}  {k}')

# Top wards for road complaints
ward_dist = collections.Counter(r['ward_title'] for r in road_rows if r.get('ward_title'))
print('\nTop 15 wards (road complaints):')
for k,v in ward_dist.most_common(15):
    print(f'  {v:4d}  {k}')

# Year distribution
def get_year(d):
    import re
    m = re.search(r'(201\d|202\d)', d)
    return m.group(1) if m else 'unknown'
year_dist = collections.Counter(get_year(r['created_at']) for r in road_rows)
print('\nYear distribution (road complaints):')
for k,v in sorted(year_dist.items()):
    print(f'  {k}  {v}')

# Sample pothole descriptions
potholes = [r for r in road_rows if 'Pothole' in r.get('sub_category_title','')][:3]
print('\nSample pothole descriptions:')
for r in potholes:
    ward = r.get('ward_title','?')
    dt = r.get('created_at','?')
    desc = r.get('description','')[:250]
    lat = r.get('latitude','?')
    lon = r.get('longitude','?')
    print(f'  Ward: {ward} | Date: {dt} | GPS: {lat},{lon}')
    print(f'  Desc: {desc}')
    print()
