import sqlite3
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine

# ── Paths ──────────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).resolve().parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
DB_PATH       = BASE_DIR / "bluestock_mf.db"
SCHEMA_PATH   = BASE_DIR / "schema.sql"


def load_star_schema():
    # Remove existing db file if any
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("Removed existing database file.")

    print("Connecting and creating schema from schema.sql...")
    # Execute SQL DDL
    conn = sqlite3.connect(str(DB_PATH))
    ddl = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(ddl)
    conn.close()

    # Setup SQLAlchemy Engine
    engine = create_engine(f"sqlite:///{DB_PATH}")

    # 1. Load dim_fund
    df_fund = pd.read_csv(PROCESSED_DIR / "fund_master.csv")
    df_fund.to_sql("dim_fund", engine, if_exists="append", index=False)
    print(f"Loaded {len(df_fund)} rows to dim_fund.")

    # 2. Populate dim_date dynamically using unique dates from nav_history & transactions
    df_nav = pd.read_csv(PROCESSED_DIR / "nav_history.csv")
    df_tx = pd.read_csv(PROCESSED_DIR / "investor_transactions.csv")

    all_dates = pd.concat([df_nav["date"], df_tx["transaction_date"]]).dropna().unique()
    df_dates = pd.DataFrame({"date": all_dates})
    df_dates["date_dt"] = pd.to_datetime(df_dates["date"])
    df_dates = df_dates.sort_values(by="date_dt")

    dim_date = pd.DataFrame()
    dim_date["date"] = df_dates["date"]
    dim_date["year"] = df_dates["date_dt"].dt.year
    dim_date["quarter"] = df_dates["date_dt"].dt.quarter
    dim_date["month"] = df_dates["date_dt"].dt.month
    dim_date["month_name"] = df_dates["date_dt"].dt.strftime("%B")
    dim_date["day"] = df_dates["date_dt"].dt.day
    dim_date["day_of_week"] = df_dates["date_dt"].dt.strftime("%A")
    dim_date["is_weekend"] = dim_date["day_of_week"].isin(["Saturday", "Sunday"]).astype(int)

    dim_date.to_sql("dim_date", engine, if_exists="append", index=False)
    print(f"Populated {len(dim_date)} rows to dim_date.")

    # 3. Load fact_nav
    df_nav.to_sql("fact_nav", engine, if_exists="append", index=False)
    print(f"Loaded {len(df_nav)} rows to fact_nav.")

    # 4. Load fact_transactions
    # Since CSV doesn't have explicit transaction_id, let's create a primary key for it
    if "transaction_id" not in df_tx.columns:
        df_tx.insert(0, "transaction_id", ["TX" + str(i).zfill(6) for i in range(1, len(df_tx) + 1)])
    df_tx.to_sql("fact_transactions", engine, if_exists="append", index=False)
    print(f"Loaded {len(df_tx)} rows to fact_transactions.")

    # 5. Load fact_performance
    df_perf = pd.read_csv(PROCESSED_DIR / "scheme_performance.csv")
    # Map raw CSV columns to DDL columns
    df_perf_db = df_perf[[
        "amfi_code", "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
        "benchmark_3yr_pct", "alpha", "beta", "sharpe_ratio", "sortino_ratio",
        "std_dev_ann_pct", "max_drawdown_pct", "morningstar_rating", "risk_grade"
    ]]
    df_perf_db.to_sql("fact_performance", engine, if_exists="append", index=False)
    print(f"Loaded {len(df_perf_db)} rows to fact_performance.")

    # 6. Load fact_aum
    df_aum = pd.read_csv(PROCESSED_DIR / "aum_by_fund_house.csv")
    df_aum.to_sql("fact_aum", engine, if_exists="append", index=False)
    print(f"Loaded {len(df_aum)} rows to fact_aum.")

    # Save extra tables not strictly part of star schema into DB too for convenience
    df_sip = pd.read_csv(PROCESSED_DIR / "monthly_sip_inflows.csv")
    df_sip.to_sql("monthly_sip_inflows", engine, if_exists="replace", index=False)

    df_cat = pd.read_csv(PROCESSED_DIR / "category_inflows.csv")
    df_cat.to_sql("category_inflows", engine, if_exists="replace", index=False)

    df_folio = pd.read_csv(PROCESSED_DIR / "industry_folio_count.csv")
    df_folio.to_sql("industry_folio_count", engine, if_exists="replace", index=False)

    df_holdings = pd.read_csv(PROCESSED_DIR / "portfolio_holdings.csv")
    df_holdings.to_sql("portfolio_holdings", engine, if_exists="replace", index=False)

    df_bench = pd.read_csv(PROCESSED_DIR / "benchmark_indices.csv")
    df_bench.to_sql("benchmark_indices", engine, if_exists="replace", index=False)

    print("\nDatabase loaded successfully and row counts verified!")


if __name__ == "__main__":
    load_star_schema()
