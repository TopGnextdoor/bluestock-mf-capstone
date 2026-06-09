#!/usr/bin/env python3
"""
Simple Mutual Fund Recommender
Usage:
    python recommender.py --risk [Low|Moderate|High]
    or run without arguments for interactive mode.
"""

import os
import sys
import sqlite3
import argparse
import pandas as pd

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "bluestock_mf.db")
DATA_DIR = os.path.join(BASE_DIR, "data", "processed")

def load_data():
    """Loads fund and performance data, preferring SQLite, falling back to CSVs."""
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            query = """
                SELECT 
                    f.amfi_code, 
                    f.scheme_name, 
                    f.category, 
                    f.sub_category, 
                    p.sharpe_ratio, 
                    p.risk_grade
                FROM fact_performance p
                JOIN dim_fund f ON p.amfi_code = f.amfi_code
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Warning: Failed to read from database ({e}). Falling back to CSVs.")
    
    # Fallback to CSV
    try:
        df_funds = pd.read_csv(os.path.join(DATA_DIR, "fund_master.csv"))
        df_perf = pd.read_csv(os.path.join(DATA_DIR, "scheme_performance.csv"))
        df = pd.merge(df_funds, df_perf, on="amfi_code", how="inner")
        return df[['amfi_code', 'scheme_name', 'category', 'sub_category', 'sharpe_ratio', 'risk_grade']]
    except Exception as e:
        print(f"Error: Could not load data from CSVs ({e}).")
        sys.exit(1)

def get_recommendations(risk_appetite):
    """Returns top 3 funds by Sharpe ratio within matching risk grades."""
    df = load_data()
    
    # Map risk appetite to risk grades
    appetite = risk_appetite.strip().lower()
    if appetite == "low":
        grades = ["Low"]
    elif appetite == "moderate":
        # We include both Moderate and Moderately High for Moderate appetite
        grades = ["Moderate", "Moderately High"]
    elif appetite == "high":
        # We include both High and Very High for High appetite
        grades = ["High", "Very High"]
    else:
        raise ValueError("Invalid risk appetite. Choose from: Low, Moderate, High.")
    
    # Filter and sort
    filtered_df = df[df["risk_grade"].isin(grades)].copy()
    # Sort by Sharpe Ratio descending
    filtered_df = filtered_df.sort_values(by="sharpe_ratio", ascending=False)
    
    return filtered_df.head(3)

def print_recommendation_table(risk_appetite, df_rec):
    """Prints the recommendations in a beautiful ASCII table."""
    print("\n" + "=" * 80)
    print(f" RECOMMENDATION REPORT FOR RISK APPETITE: {risk_appetite.upper()} ")
    print("=" * 80)
    if df_rec.empty:
        print("No matching funds found for this risk appetite.")
        print("=" * 80)
        return
    
    # Define headers and column widths
    headers = ["AMFI Code", "Scheme Name", "Category", "Sub-Category", "Sharpe", "Risk Grade"]
    col_widths = [10, 35, 10, 15, 8, 12]
    
    # Print Header
    header_str = " | ".join(f"{h:<{w}}" for h, w in zip(headers, col_widths))
    print(header_str)
    print("-" * 80)
    
    # Print Rows
    for _, row in df_rec.iterrows():
        # Truncate long scheme names to fit column width
        name = row['scheme_name']
        if len(name) > col_widths[1]:
            name = name[:col_widths[1]-3] + "..."
            
        row_str = (
            f"{str(row['amfi_code']):<{col_widths[0]}} | "
            f"{name:<{col_widths[1]}} | "
            f"{row['category']:<{col_widths[2]}} | "
            f"{row['sub_category']:<{col_widths[3]}} | "
            f"{row['sharpe_ratio']:<{col_widths[4]}.2f} | "
            f"{row['risk_grade']:<{col_widths[5]}}"
        )
        print(row_str)
    print("=" * 80)

def main():
    parser = argparse.ArgumentParser(description="Simple Mutual Fund Recommender CLI Tool")
    parser.add_argument(
        "-r", "--risk", 
        choices=["Low", "Moderate", "High", "low", "moderate", "high"], 
        help="Investor risk appetite (Low / Moderate / High)"
    )
    args = parser.parse_args()
    
    if args.risk:
        risk_appetite = args.risk.capitalize()
    else:
        # Interactive mode
        print("Welcome to the Bluestock Mutual Fund Recommender!")
        while True:
            val = input("Enter your risk appetite (Low / Moderate / High): ").strip()
            if val.lower() in ["low", "moderate", "high"]:
                risk_appetite = val.capitalize()
                break
            print("Invalid input. Please enter 'Low', 'Moderate', or 'High'.\n")
            
    df_rec = get_recommendations(risk_appetite)
    print_recommendation_table(risk_appetite, df_rec)

if __name__ == "__main__":
    main()
