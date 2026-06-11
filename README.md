# Bluestock Mutual Fund Capstone Project

This project is the final capstone deliverable for the Bluestock Fintech Data Analytics & Engineering track. It showcases a fully functional Extract, Transform, and Load (ETL) pipeline, an SQLite star schema database for mutual fund analytics, performance metric calculations (Alpha, Beta, Sharpe, Sortino), an interactive HTML/Python dashboard, and robust PDF and PPTX reporting scripts.

## Project Overview

The objective is to consolidate heterogeneous mutual fund datasets (daily NAVs, master fund metadata, industry AUMs, SIP flows, retail investor demographic transactions) into a central data warehouse, analyze them for key business insights, and visualize the trends.

### Key Features
- **Data Ingestion**: Automates downloads from Google Drive and live API endpoints (AMFI / MFAPI).
- **Data Validation & Cleansing**: Standardizes transaction histories, drops duplicates, validates bounds (expense ratios: 0.1%-2.5%), and forward-fills missing daily NAV prices.
- **Relational Star Schema**: Loads into `bluestock_mf.db` with 2 fact tables (`fact_nav`, `fact_transactions`) and corresponding dimension tables (`dim_fund`, `dim_date`).
- **Risk Profiling & Recommender**: Computes Sharpe ratios and standard deviations, serving top recommendations through a CLI interactive tool (`recommender.py`).
- **Data Visualizations**: Autogenerates a 4-page PNG visual dashboard covering Industry Overview, Fund Performance, Investor Analytics, and SIP Trends.
- **Comprehensive Reporting**: Autogenerates a highly formatted 18-page `Final_Report.pdf` and a 12-slide executive presentation `Bluestock_MF_Presentation.pptx`.

## Repository Structure

```
bluestock_mf_capstone/
├── run_pipeline.py                 # Master execution script orchestrating all stages
├── download_drive_datasets.py      # Module for data ingestion
├── fetch_fund_master.py            # Fetches AMFI NAV0 live daily file
├── fetch_nav.py                    # Fetches live historical NAV from MFAPI
├── clean_datasets.py               # Cleans and standardizes raw CSVs
├── load_db.py                      # Initializes schema and bulk-inserts into SQLite
├── explore_and_validate.py         # Audits AMFI codes and generates Markdown summaries
├── analyze_data.py                 # Computes descriptive statistics and handles EDA
├── recommender.py                  # CLI app: suggests mutual funds based on Risk Appetite
├── generate_report.py              # ReportLab script producing the 18-page Final_Report.pdf
├── generate_presentation.py        # python-pptx script producing the 12-slide slide deck
├── schema.sql                      # DDL for SQLite database
├── data_dictionary.md              # Documentation of table structures
├── data/                           # Contains /raw and /processed CSV files
├── dashboard/                      # Contains generate_dashboard.py and HTML static files
```

## Setup Instructions

### Prerequisites
- Python 3.9+
- The required dependencies are listed in `requirements.txt`.

### Installation
1. Clone the repository and navigate to the project directory:
   ```bash
   git clone https://github.com/bluestock-mf-capstone.git
   cd bluestock_mf_capstone
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install reportlab python-pptx
   ```

## Running the ETL Pipeline

To run the entire end-to-end pipeline (downloading, cleaning, database creation, analytics, and reporting):
```bash
cd bluestock_mf_capstone
python run_pipeline.py
```

This master script will print structured logs to the console and orchestrate all required steps sequentially.

## Opening the Dashboards and Deliverables

Upon a successful pipeline run, the following deliverables are generated:

1. **Dashboard Overview**: Check the `dashboard/` directory for 4 generated PNGs showing analytical insights. You can also view them sequentially in `dashboard/Dashboard.pdf`.
2. **Final Report**: The comprehensive 18-page written report is available at `Final_Report.pdf`.
3. **Executive Presentation**: The 12-slide presentation is available at `Bluestock_MF_Presentation.pptx`.
4. **Interactive Recommendation CLI**: 
   To get personalized mutual fund recommendations based on risk:
   ```bash
   python recommender.py --risk Moderate
   ```

*(Optional) Power BI/Tableau*: The processed CSV datasets in `data/processed/` are clean and strictly formatted for direct ingestion into Power BI or Tableau Public. A setup guide is available in `dashboard/POWERBI_SETUP_GUIDE.md`.

## Data Dictionary
Please refer to `data_dictionary.md` for a comprehensive explanation of the star schema, entity-relationship structures, and business logic applied to column aggregations.

## License & Acknowledgements
Built for the Bluestock Fintech Data Analytics Capstone.
