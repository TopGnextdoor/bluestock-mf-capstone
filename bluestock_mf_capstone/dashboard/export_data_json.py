"""
Export SQLite database tables to JSON files for the interactive HTML dashboard.
"""
import sqlite3
import json
import math
import pandas as pd
import re
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH  = BASE_DIR / "bluestock_mf.db"
OUT_DIR  = Path(__file__).resolve().parent / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

conn = sqlite3.connect(str(DB_PATH))

tables = {
    "dim_fund": "SELECT * FROM dim_fund",
    "fact_aum": "SELECT * FROM fact_aum",
    "fact_performance": "SELECT fp.*, df.fund_house, df.scheme_name, df.category, df.sub_category, df.plan FROM fact_performance fp JOIN dim_fund df ON fp.amfi_code = df.amfi_code",
    "fact_nav": "SELECT fn.amfi_code, fn.date, fn.nav, df.scheme_name, df.fund_house, df.category FROM fact_nav fn JOIN dim_fund df ON fn.amfi_code = df.amfi_code",
    "fact_transactions": "SELECT * FROM fact_transactions",
    "monthly_sip_inflows": "SELECT * FROM monthly_sip_inflows",
    "category_inflows": "SELECT * FROM category_inflows",
    "industry_folio_count": "SELECT * FROM industry_folio_count",
    "benchmark_indices": "SELECT * FROM benchmark_indices",
}

def sanitize_records(records):
    """Replace float NaN/Inf with None so json.dumps produces valid JSON."""
    cleaned = []
    for row in records:
        new_row = {}
        for k, v in row.items():
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                new_row[k] = None
            else:
                new_row[k] = v
        cleaned.append(new_row)
    return cleaned

for name, query in tables.items():
    print(f"Exporting {name}...")
    df = pd.read_sql(query, conn)

    # For large tables, sample or aggregate
    if name == "fact_nav":
        # Sample every 7th day per fund for size
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values(["amfi_code", "date"])
        sampled = []
        for code, grp in df.groupby("amfi_code"):
            sampled.append(grp.iloc[::7])
        df = pd.concat(sampled, ignore_index=True)
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    if name == "benchmark_indices":
        # Normalize index names (e.g., "NIFTY 50" or "NIFTY_50") to canonical "NIFTY50"
        df["index_name"] = df["index_name"].apply(lambda x: "NIFTY50" if re.search(r"nifty\s*50", str(x), re.I) else x)
        # Keep only NIFTY50 rows for the chart
        nifty_df = df[df["index_name"] == "NIFTY50"].copy()
        if nifty_df.empty:
            # Create a minimal placeholder to avoid empty dataset
            placeholder = {
                "date": datetime.datetime.today().strftime("%Y-%m-01"),
                "index_name": "NIFTY50",
                "close_value": 1.0,
            }
            nifty_df = pd.DataFrame([placeholder])
        # Convert to datetime and aggregate to monthly average
        nifty_df["date"] = pd.to_datetime(nifty_df["date"])
        nifty_df["month"] = nifty_df["date"].dt.strftime("%Y-%m")
        monthly_nifty = (
            nifty_df.groupby(["index_name", "month"], as_index=False)["close_value"].mean()
            .rename(columns={"month": "date"})
            .sort_values(["index_name", "date"]).reset_index(drop=True)
        )
        df = monthly_nifty

    records = df.to_dict(orient="records")
    records = sanitize_records(records)

    with open(OUT_DIR / f"{name}.json", "w", encoding="utf-8") as f:
        json.dump(records, f)
    print(f"  -> {len(records)} records")

conn.close()
print("\nAll JSON data exported to:", OUT_DIR)
