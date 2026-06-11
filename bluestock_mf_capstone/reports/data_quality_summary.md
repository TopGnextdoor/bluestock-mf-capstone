# Data Quality Summary Report (Google Drive Datasets)

## Overview
This report summarizes the structure and data quality of the 10 Mutual Fund datasets downloaded from Google Drive on 2026-06-11 19:56:57.

## Datasets Overview
1. **01_fund_master.csv / fund_master.csv**
   - **Records**: 40 Mutual Fund schemes
   - **Columns**: `amfi_code`, `fund_house`, `scheme_name`, `category`, `sub_category`, `plan`, `launch_date`, `benchmark`, `expense_ratio_pct`, `exit_load_pct`, `min_sip_amount`, `min_lumpsum_amount`, `fund_manager`, `risk_category`, `sebi_category_code`
   - **Data Quality**: 0 missing values across all columns. No duplicates.
   
2. **02_nav_history.csv / nav_history.csv**
   - **Records**: 46000 historical NAV rows across 40 schemes.
   - **Columns**: `amfi_code`, `date`, `nav`
   - **Data Quality**: 0 missing values. NAV contains all positive floating point values.

3. **Other Datasets Ingested**
   - **03_aum_by_fund_house.csv**: AUM for 90 AMCs.
   - **04_monthly_sip_inflows.csv**: 48 months of SIP flows.
   - **05_category_inflows.csv**: Inflows across categories for 144 months.
   - **06_industry_folio_count.csv**: Folio metrics over time.
   - **07_scheme_performance.csv**: Alpha, beta, sharpe ratios for schemes.
   - **08_investor_transactions.csv**: 32778 retail transaction records.
   - **09_portfolio_holdings.csv**: Stock weights for schemes.
   - **10_benchmark_indices.csv**: 8050 daily close values for benchmarks.

## AMFI Codes Validation
- **Validation Rule**: Every unique scheme code in `nav_history` must exist in `fund_master`.
- **Result**: **PASSED**
  - All 40 schemes present in the transaction database exist in the master schemes database.
  - Schemes verified: [119552, 120841, 120842, 120843, 120844, 119598, 119599, 100016, 119092, 119093, 119094, 120503, 120504, 100025, 120506, 120505, 125497, 125498, 120507, 119095, 100033, 149322, 149323, 149324, 119120, 101206, 101207, 101208, 148567, 148568, 148569, 102885, 102886, 102887, 118632, 118633, 118634, 118635, 118636, 119551]

## Summary & Key Findings
- **AMFI Structure**: The AMFI scheme code is a unique 5-to-6 digit identifier.
- **Fund Houses**: There are 10 unique fund houses (AMCs) listed.
- **Categories**: The funds are classified into 2 main categories (e.g. Equity, Debt) and 12 sub-categories.
- **Risk Profiles**: Risk grades correctly highlight risk categories: ['Moderate', 'Very High', 'Low', 'High', 'Moderately High'].
