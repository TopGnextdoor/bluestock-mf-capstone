import requests
import json
import csv
import pandas as pd
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# 1. Fetch live NAV for HDFC Top 100 Direct (125497)
def fetch_hdfc_nav():
    url = "https://api.mfapi.in/mf/125497"
    print(f"Fetching NAV from {url}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Save raw JSON
        with open(RAW_DIR / "hdfc_125497_raw.json", "w") as f:
            json.dump(data, f, indent=4)
            
        # Parse and save as CSV
        meta = data.get("meta", {})
        nav_list = data.get("data", [])
        
        csv_path = RAW_DIR / "hdfc_125497_nav.csv"
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["date", "nav"])
            for item in nav_list:
                writer.writerow([item["date"], item["nav"]])
                
        print(f"Saved HDFC Top 100 Direct NAV to {csv_path}")
    except Exception as e:
        print(f"Error fetching HDFC NAV: {e}")

# 2. Fetch NAV for 5 key schemes
# SBI Bluechip (119551), ICICI Bluechip (120503), Nippon Large Cap (118632), Axis Bluechip (119092), Kotak Bluechip (120841)
def fetch_5_schemes():
    schemes = {
        "119551": "sbi_bluechip",
        "120503": "icici_bluechip",
        "118632": "nippon_large_cap",
        "119092": "axis_bluechip",
        "120841": "kotak_bluechip"
    }
    
    for code, name in schemes.items():
        url = f"https://api.mfapi.in/mf/{code}"
        print(f"Fetching NAV for {name} ({code})...")
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            nav_list = data.get("data", [])
            csv_path = RAW_DIR / f"{name}_{code}_nav.csv"
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["date", "nav"])
                for item in nav_list:
                    writer.writerow([item["date"], item["nav"]])
            print(f"Saved {name} NAV to {csv_path}")
            time.sleep(1) # Be nice to the API
        except Exception as e:
            print(f"Error fetching {name} ({code}): {e}")

if __name__ == "__main__":
    fetch_hdfc_nav()
    fetch_5_schemes()

