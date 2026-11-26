"""
Fetch all KAUN work orders across all wards and save to JSON.
Uses stdlib only: urllib, json, time.
"""
import json
import time
import urllib.request
import urllib.error
import sys

WARDS_FILE = "data/raw/kaun_wards.json"
OUTPUT_FILE = "data/raw/kaun_work_orders_all_wards.json"
BASE_URL = "https://kaun.city/api/data/spending?ward={}&type=work-orders"
DELAY = 0.4  # seconds between requests

def fetch_url(url, timeout=15):
    req = urllib.request.Request(url, headers={"User-Agent": "CivicLens/1.0 (data-research)"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    with open(WARDS_FILE, encoding="utf-8") as f:
        wards_data = json.load(f)
    wards = wards_data["data"]
    print(f"Total wards: {len(wards)}", flush=True)

    all_work_orders = []
    failed = []

    for i, ward in enumerate(wards):
        wn = ward["ward_no"]
        url = BASE_URL.format(wn)
        try:
            data = fetch_url(url)
            wos = data.get("work_orders", [])
            all_work_orders.extend(wos)
            if (i + 1) % 25 == 0:
                print(f"  Fetched {i+1}/{len(wards)} wards — {len(all_work_orders)} work orders total", flush=True)
        except Exception as e:
            failed.append({"ward_no": wn, "error": str(e)})
            print(f"  Ward {wn} FAILED: {e}", flush=True)
        time.sleep(DELAY)

    print(f"\nDone. {len(all_work_orders)} work orders, {len(failed)} failed wards", flush=True)

    output = {
        "metadata": {
            "source": "kaun.city API",
            "endpoint": "https://kaun.city/api/data/spending?ward=N&type=work-orders",
            "total_work_orders": len(all_work_orders),
            "wards_fetched": len(wards) - len(failed),
            "wards_failed": len(failed),
            "failed_wards": failed,
            "license": "Public data, MIT licensed platform",
            "attribution": "Data sourced from KAUN Bengaluru (kaun.city) via BBMP/opencity.in"
        },
        "work_orders": all_work_orders
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    import os
    size = os.path.getsize(OUTPUT_FILE)
    print(f"Saved: {OUTPUT_FILE} ({size:,} bytes)", flush=True)

if __name__ == "__main__":
    main()
