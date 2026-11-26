import csv, json, collections

with open('data/raw/kaun_work_orders_all_wards.json', encoding='utf-8', errors='replace') as f:
    wo_data = json.load(f)

work_orders = wo_data['work_orders']
print(f'Total work orders: {len(work_orders)}')
print(f'Fields: {list(work_orders[0].keys())}')

road_kw = ['road','tarring','asphal','pothole','white top','whitetopping','resurfac','laying','macadam','concreting']
drain_kw = ['drain','swd','stormwater','storm water','nalla','culvert','desilting','flooding']
footpath_kw = ['footpath','footway','pavement','pedestrian','sidewalk']
streetlight_kw = ['streetlight','street light','lighting']
water_kw = ['water','bwssb','sewage','pipeline','ug drainage']

def classify_wo(desc):
    d = desc.lower()
    if any(k in d for k in road_kw): return 'road'
    if any(k in d for k in drain_kw): return 'drain'
    if any(k in d for k in footpath_kw): return 'footpath'
    if any(k in d for k in streetlight_kw): return 'streetlight'
    if any(k in d for k in water_kw): return 'water'
    return 'other'

wo_cats = collections.Counter(classify_wo(r.get('description','')) for r in work_orders)
print('\nWork order categories (by keywords):')
for k,v in wo_cats.most_common():
    print(f'  {v:5d}  {k}')

fy_dist = collections.Counter(r.get('fy','') for r in work_orders)
print('\nFiscal year distribution:')
for k,v in sorted(fy_dist.items()):
    print(f'  {k}  {v}')

# How many work orders have matching wards that also appear in ichangemycity?
icmc = []
with open('data/raw/ichangemycity_complaints.csv', encoding='cp1252', errors='replace') as f:
    icmc = list(csv.DictReader(f))
icmc_ward_ids = set(r['ward_id'] for r in icmc if r.get('ward_id'))
wo_datameet_ids = set(str(r.get('datameet243_no','')) for r in work_orders if r.get('datameet243_no'))
overlap = icmc_ward_ids & wo_datameet_ids
print(f'\nICMC ward IDs: {len(icmc_ward_ids)}')
print(f'Work order datameet243 IDs: {len(wo_datameet_ids)}')
print(f'Overlap (matching ward IDs): {len(overlap)}')

# Ward metrics pothole data
metrics = []
with open('data/raw/kaun_ward_metrics.csv', encoding='utf-8') as f:
    metrics = list(csv.DictReader(f))
metrics_with_potholes = [r for r in metrics if r.get('pothole_complaints') and r['pothole_complaints'] != '']
print(f'\nWard metrics rows: {len(metrics)}')
print(f'Wards with pothole complaint counts: {len(metrics_with_potholes)}')
total_potholes = sum(int(r['pothole_complaints']) for r in metrics_with_potholes)
print(f'Total ward-aggregated pothole complaints: {total_potholes}')
print(f'Sample ward metrics fields: {list(metrics[0].keys()[:10])}')

print('\nSample work order descriptions (road type):')
road_wos = [r for r in work_orders if classify_wo(r.get('description','')) == 'road'][:3]
for r in road_wos:
    wid = r.get('work_order_id','?')
    ward = r.get('datameet243_no','?')
    fy = r.get('fy','?')
    cname = r.get('contractor_name','?')
    amt = r.get('sanctioned_amount','?')
    desc = r.get('description','')[:180]
    print(f'  WO={wid} ward243={ward} FY={fy} contractor={cname} amt={amt}')
    print(f'  Desc: {desc}')
    print()
