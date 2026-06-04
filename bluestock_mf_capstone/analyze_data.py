import pandas as pd
import numpy as np
import glob
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR  = BASE_DIR / "data" / "raw"


def analyze_datasets():
    csv_files = list(RAW_DIR.glob("*.csv"))
    print(f"Found {len(csv_files)} CSV files to analyze.\n")

    for file_path in csv_files:
        file_name = file_path.name
        print("=" * 60)
        print(f"DATASET: {file_name}")
        print("=" * 60)

        try:
            df = pd.read_csv(file_path)
            print(f"Shape: {df.shape}")
            print("\nData Types:")
            print(df.dtypes)
            print("\nFirst 5 Rows:")
            print(df.head())
            print("\nMissing Values:")
            print(df.isnull().sum())
            print("\nAnomalies & Notes:")

            # Duplicate rows
            duplicates = df.duplicated().sum()
            if duplicates > 0:
                print(f"- Warning: Found {duplicates} duplicate rows.")
            else:
                print("- No duplicate rows found.")

            # NAV validation
            if "nav" in df.columns:
                df_nav = pd.to_numeric(df["nav"], errors="coerce")
                neg_nav = (df_nav < 0).sum()
                nan_nav = df_nav.isna().sum()
                if neg_nav > 0:
                    print(f"- Warning: Found {neg_nav} negative NAV values.")
                if nan_nav > 0:
                    print(f"- Warning: Found {nan_nav} non-numeric or missing NAV values.")
                if neg_nav == 0 and nan_nav == 0:
                    print("- NAV column contains valid positive numeric values.")

            # Scheme code validation (fund master only)
            scheme_col = (
                "amfi_code" if "amfi_code" in df.columns
                else ("scheme_code" if "scheme_code" in df.columns else None)
            )
            if file_name in ["fund_master.csv", "01_fund_master.csv"] and scheme_col:
                null_codes = df[scheme_col].isnull().sum()
                if null_codes > 0:
                    print(f"- Warning: Found {null_codes} null scheme codes.")
                dup_codes = df[scheme_col].duplicated().sum()
                if dup_codes > 0:
                    print(f"- Note: Found {dup_codes} duplicate codes.")

        except Exception as e:
            print(f"Error loading {file_name}: {e}")
        print("\n")


if __name__ == "__main__":
    analyze_datasets()
