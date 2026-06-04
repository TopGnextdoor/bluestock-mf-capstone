import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).resolve().parent
RAW_DIR       = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# 1. Clean nav_history.csv
def clean_nav_history():
    print("Cleaning nav_history.csv...")
    df = pd.read_csv(RAW_DIR / "02_nav_history.csv")

    # Remove duplicates
    df = df.drop_duplicates()

    # Parse dates
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Sort
    df = df.sort_values(by=["amfi_code", "date"]).reset_index(drop=True)

    # Forward-fill missing NAV for holidays/weekends per fund
    df_list = []
    for amfi, group in df.groupby("amfi_code"):
        # Create a complete date range from min to max date for this fund
        min_date = group["date"].min()
        max_date = group["date"].max()
        if pd.notnull(min_date) and pd.notnull(max_date):
            full_range = pd.date_range(start=min_date, end=max_date, freq="D")
            group = group.set_index("date").reindex(full_range)
            group["amfi_code"] = amfi
            group["nav"] = group["nav"].ffill()
            group = group.reset_index().rename(columns={"index": "date"})
        df_list.append(group)

    df_cleaned = pd.concat(df_list, ignore_index=True)

    # Validate NAV > 0
    df_cleaned = df_cleaned[df_cleaned["nav"] > 0]

    # Convert date to string format for CSV saving
    df_cleaned["date"] = df_cleaned["date"].dt.strftime("%Y-%m-%d")

    df_cleaned.to_csv(PROCESSED_DIR / "02_nav_history.csv", index=False)
    # Also save as nav_history.csv in processed
    df_cleaned.to_csv(PROCESSED_DIR / "nav_history.csv", index=False)
    print(f"Cleaned nav_history: {len(df_cleaned)} rows saved.")


# 2. Clean investor_transactions.csv
def clean_investor_transactions():
    print("Cleaning investor_transactions.csv...")
    df = pd.read_csv(RAW_DIR / "08_investor_transactions.csv")

    # Standardise transaction_type values (SIP/Lumpsum/Redemption)
    df["transaction_type"] = df["transaction_type"].str.strip().str.capitalize()
    df["transaction_type"] = df["transaction_type"].replace({
        "Sip": "SIP",
        "Lump_sum": "Lumpsum",
        "Lumpsum": "Lumpsum",
        "Redemption": "Redemption"
    })

    # Validate amount > 0
    df = df[df["amount_inr"] > 0]

    # Fix date formats
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df = df.dropna(subset=["transaction_date"])
    df["transaction_date"] = df["transaction_date"].dt.strftime("%Y-%m-%d")

    # Check KYC status enum values (Standardise to Verified / Pending)
    df["kyc_status"] = df["kyc_status"].str.strip().str.capitalize()
    df["kyc_status"] = df["kyc_status"].replace({
        "Yes": "Verified",
        "No": "Pending",
        "Verified": "Verified",
        "Pending": "Pending"
    })

    df.to_csv(PROCESSED_DIR / "08_investor_transactions.csv", index=False)
    # Also save as investor_transactions.csv
    df.to_csv(PROCESSED_DIR / "investor_transactions.csv", index=False)
    print(f"Cleaned investor_transactions: {len(df)} rows saved.")


# 3. Clean scheme_performance.csv
def clean_scheme_performance():
    print("Cleaning scheme_performance.csv...")
    df = pd.read_csv(RAW_DIR / "07_scheme_performance.csv")

    # Validate all return values are numeric (replace strings/nulls if any)
    for col in ["return_1yr_pct", "return_3yr_pct", "return_5yr_pct"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[col] = df[col].fillna(df[col].median())

    # Check expense_ratio range (0.1% – 2.5%)
    df["expense_ratio_pct"] = pd.to_numeric(df["expense_ratio_pct"], errors="coerce")
    # Clip expense ratio to normal bounds if any outliers exist
    df["expense_ratio_pct"] = df["expense_ratio_pct"].clip(lower=0.1, upper=2.5)

    df.to_csv(PROCESSED_DIR / "07_scheme_performance.csv", index=False)
    # Also save as scheme_performance.csv
    df.to_csv(PROCESSED_DIR / "scheme_performance.csv", index=False)
    print(f"Cleaned scheme_performance: {len(df)} rows saved.")


# 4. Copy/Clean remaining 7 files to processed directory
def process_remaining_files():
    print("Processing remaining datasets...")

    # fund_master
    df_fm = pd.read_csv(RAW_DIR / "01_fund_master.csv")
    df_fm.to_csv(PROCESSED_DIR / "01_fund_master.csv", index=False)
    df_fm.to_csv(PROCESSED_DIR / "fund_master.csv", index=False)

    # aum_by_fund_house
    df_aum = pd.read_csv(RAW_DIR / "03_aum_by_fund_house.csv")
    df_aum.to_csv(PROCESSED_DIR / "03_aum_by_fund_house.csv", index=False)
    df_aum.to_csv(PROCESSED_DIR / "aum_by_fund_house.csv", index=False)

    # monthly_sip_inflows
    df_sip = pd.read_csv(RAW_DIR / "04_monthly_sip_inflows.csv")
    df_sip.to_csv(PROCESSED_DIR / "04_monthly_sip_inflows.csv", index=False)
    df_sip.to_csv(PROCESSED_DIR / "monthly_sip_inflows.csv", index=False)

    # category_inflows
    df_cat = pd.read_csv(RAW_DIR / "05_category_inflows.csv")
    df_cat.to_csv(PROCESSED_DIR / "05_category_inflows.csv", index=False)
    df_cat.to_csv(PROCESSED_DIR / "category_inflows.csv", index=False)

    # industry_folio_count
    df_folio = pd.read_csv(RAW_DIR / "06_industry_folio_count.csv")
    df_folio.to_csv(PROCESSED_DIR / "06_industry_folio_count.csv", index=False)
    df_folio.to_csv(PROCESSED_DIR / "industry_folio_count.csv", index=False)

    # portfolio_holdings
    df_holdings = pd.read_csv(RAW_DIR / "09_portfolio_holdings.csv")
    df_holdings.to_csv(PROCESSED_DIR / "09_portfolio_holdings.csv", index=False)
    df_holdings.to_csv(PROCESSED_DIR / "portfolio_holdings.csv", index=False)

    # benchmark_indices
    df_bench = pd.read_csv(RAW_DIR / "10_benchmark_indices.csv")
    df_bench.to_csv(PROCESSED_DIR / "10_benchmark_indices.csv", index=False)
    df_bench.to_csv(PROCESSED_DIR / "benchmark_indices.csv", index=False)

    print("Remaining files successfully saved to data/processed/.")


if __name__ == "__main__":
    clean_nav_history()
    clean_investor_transactions()
    clean_scheme_performance()
    process_remaining_files()
