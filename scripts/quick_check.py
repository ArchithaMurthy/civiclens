import json
from pathlib import Path
cases = json.loads(Path("data/processed/civic_cases.json").read_text(encoding="utf-8"))
print(f"Cases loaded: {len(cases)}")
print(f"First case: {cases[0]['case_id']}")
print(f"Has complaint_ids: {'complaint_ids' in cases[0]}")
print(f"complaint_ids count: {len(cases[0]['complaint_ids'])}")
print(f"First 3 IDs: {cases[0]['complaint_ids'][:3]}")
print(f"Has ward_join_confidence: {'ward_join_confidence' in cases[0]}")
print(f"ward_join_confidence: {cases[0]['ward_join_confidence']}")
