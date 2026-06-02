import urllib.request
import re
import os
import pandas as pd

RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

def download_amfi_master():
    url = "https://portal.amfiindia.com/spages/NAVAll.txt"
    print(f"Downloading AMFI master data from {url}...")
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req) as response:
            content = response.read().decode('utf-8', errors='ignore')
            
        txt_path = os.path.join(RAW_DIR, "amfi_nav0.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Downloaded AMFI master data to {txt_path}")
        
        # Parse schemes
        parse_amfi_to_csv(content)
        
    except Exception as e:
        print(f"Error downloading/parsing AMFI master: {e}")

def parse_amfi_to_csv(content):
    lines = content.split('\n')
    schemes = []
    
    current_fund_house = "Unknown"
    current_category = "Unknown"
    
    # AMFI NAV0 format is text. We parse lines that contain scheme info.
    # Lines are generally semicolon-separated: 
    # Scheme Code;ISIN Div Payout/ ISIN Growth;ISIN Div Reinvestment;Scheme Name;Net Asset Value;Date
    # Or they are headers like:
    # Open Ended Schemes ( Equity Scheme - Large Cap Fund )
    # Mutual Fund AMC Name: ...
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check for Mutual Fund House header
        if line.startswith("Mutual Fund Name") or "Mutual Fund" in line and ";" not in line:
            current_fund_house = line.replace("Mutual Fund Name:", "").replace("Mutual Fund:", "").strip()
            continue
            
        # Check for Category header (often contains no semicolon and has words like "Open Ended Schemes")
        if (line.startswith("Open Ended Schemes") or line.startswith("Close Ended Schemes") or line.startswith("Interval Schemes")) and ";" not in line:
            current_category = line.strip()
            continue
            
        parts = line.split(';')
        if len(parts) >= 4:
            scheme_code = parts[0].strip()
            # Confirm scheme_code is numeric
            if scheme_code.isdigit():
                isin_payout = parts[1].strip()
                isin_reinv = parts[2].strip()
                scheme_name = parts[3].strip()
                nav = parts[4].strip() if len(parts) > 4 else ""
                date = parts[5].strip() if len(parts) > 5 else ""
                
                # Deduce category and sub-category from current_category
                # e.g., "Open Ended Schemes ( Equity Scheme - Large Cap Fund )"
                cat_match = re.search(r'\((.*?)\)', current_category)
                detailed_category = cat_match.group(1).strip() if cat_match else current_category
                
                sub_category = "Other"
                if " - " in detailed_category:
                    sub_parts = detailed_category.split(" - ")
                    main_cat = sub_parts[0].strip()
                    sub_category = sub_parts[1].strip()
                else:
                    main_cat = detailed_category
                
                # Mock a risk grade (since AMFI NAV0.txt doesn't have it directly, we will synthesize it based on category)
                risk_grade = "Moderate"
                if "Equity" in main_cat or "Large Cap" in sub_category or "Small Cap" in sub_category:
                    risk_grade = "Very High" if "Small Cap" in sub_category or "Mid Cap" in sub_category else "Very High"
                elif "Debt" in main_cat:
                    risk_grade = "Low to Moderate"
                elif "Liquid" in main_cat:
                    risk_grade = "Low"
                
                schemes.append({
                    "scheme_code": scheme_code,
                    "scheme_name": scheme_name,
                    "isin_growth": isin_payout,
                    "isin_reinvestment": isin_reinv,
                    "fund_house": current_fund_house,
                    "category": main_cat,
                    "sub_category": sub_category,
                    "risk_grade": risk_grade
                })
                
    df = pd.DataFrame(schemes)
    csv_path = os.path.join(RAW_DIR, "fund_master.csv")
    df.to_csv(csv_path, index=False)
    print(f"Parsed {len(df)} schemes and saved to {csv_path}")

if __name__ == "__main__":
    download_amfi_master()
