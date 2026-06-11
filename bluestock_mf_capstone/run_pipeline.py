#!/usr/bin/env python3
"""
Bluestock Mutual Fund Capstone — Master Pipeline Execution Script
================================================================

This script orchestrates the entire mutual fund analysis pipeline:
  1. Downloads raw datasets from Google Drive.
  2. Live downloads updates from AMFI / MFAPI.
  3. Cleans, standardises, and validates datasets.
  4. Creates database schema and loads SQLite database (bluestock_mf.db).
  5. Validates loaded schema and data integrity.
  6. Executes advanced analytics.
  7. Generates visual dashboard charts (PNGs) and combined PDF page set.
  8. Compiles the final 18-page analytical Report (Final_Report.pdf).
  9. Generates the 12-slide presentation (Bluestock_MF_Presentation.pptx).
"""

import sys
import subprocess
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent

def run_script(script_name, cwd=BASE_DIR):
    """Utility to run a script and check its return code."""
    script_path = cwd / script_name
    print("\n" + "=" * 80)
    print(f" RUNNING: {script_name}")
    print("=" * 80)
    
    if not script_path.exists():
        print(f"Error: {script_name} does not exist at {script_path}")
        sys.exit(1)
        
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(cwd),
            check=True,
            capture_output=False
        )
        print(f" SUCCESS: {script_name} completed.")
    except subprocess.CalledProcessError as e:
        print(f" FAILED: {script_name} failed with return code {e.returncode}.")
        sys.exit(1)

def main():
    print("=" * 80)
    print("Starting Bluestock Mutual Fund Capstone End-to-End Pipeline Execution")
    print("=" * 80)

    # 1. Download raw data
    run_script("download_drive_datasets.py")
    
    # 2. Fetch live master and nav data
    run_script("fetch_fund_master.py")
    run_script("fetch_nav.py")
    
    # 3. Clean and standardise datasets
    run_script("clean_datasets.py")
    
    # 4. Load database SQLite star schema
    run_script("load_db.py")
    
    # 5. Validate the database data quality
    run_script("explore_and_validate.py")
    
    # 6. Run basic analytics printouts
    run_script("analyze_data.py")
    
    # 7. Generate dashboard visualisations
    run_script("generate_dashboard.py", cwd=BASE_DIR / "dashboard")
    
    # 8. Generate Final PDF Report (15-20 pages)
    run_script("generate_report.py")
    
    # 9. Generate PPTX Slide Deck (12 slides)
    run_script("generate_presentation.py")
    
    print("\n" + "=" * 80)
    print(" PIPELINE SUCCESSFULLY COMPLETE!")
    print("=" * 80)
    print("The following key outputs have been generated:")
    print("  - SQLite Database: bluestock_mf.db")
    print("  - Dashboard Images: dashboard/Page1_Industry_Overview.png etc.")
    print("  - Dashboard PDF: dashboard/Dashboard.pdf")
    print("  - Final Report PDF: Final_Report.pdf (18 pages)")
    print("  - Slide Presentation: Bluestock_MF_Presentation.pptx (12 slides)")
    print("=" * 80)

if __name__ == "__main__":
    main()
