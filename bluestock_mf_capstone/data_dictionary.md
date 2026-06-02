# Bluestock Mutual Fund Capstone Project Data Dictionary

This document provides metadata, business definitions, and schemas for the SQLite Star Schema database tables loaded with the cleaned mutual fund datasets.

---

## 1. Table: `dim_fund`
Stores metadata and details about individual mutual fund schemes.

| Column Name | Data Type | Key / Constraint | Business Description |
|---|---|---|---|
| `amfi_code` | INTEGER | PRIMARY KEY | Unique numeric code assigned to the scheme by AMFI |
| `fund_house` | TEXT | NOT NULL | Asset Management Company (AMC) managing the fund |
| `scheme_name` | TEXT | NOT NULL | Complete commercial name of the mutual fund scheme |
| `category` | TEXT | NOT NULL | Asset class division (e.g. Equity, Debt) |
| `sub_category` | TEXT | NOT NULL | Specific strategy type (e.g. Large Cap, Liquid, Flexi Cap) |
| `plan` | TEXT | NOT NULL | Scheme variant (Direct/Regular) and distribution option (Growth/Dividend) |
| `launch_date` | TEXT | | ISO-8601 string date the fund was first opened |
| `benchmark` | TEXT | | The official index name this fund tracks and is evaluated against |
| `expense_ratio_pct`| REAL | | Management fee percentage charged (Cleaned Range: 0.1% to 2.5%) |
| `exit_load_pct` | REAL | | Penalty percentage charged on early redemption of fund units |
| `min_sip_amount` | REAL | | Minimum monthly SIP amount in Indian Rupees (INR) |
| `min_lumpsum_amount`| REAL | | Minimum one-time lumpsum investment amount in INR |
| `fund_manager` | TEXT | | Name of the lead portfolio manager overseeing investments |
| `risk_category` | TEXT | | Risk class indicator (Low, Moderate, High, Very High) |
| `sebi_category_code`| TEXT | | SEBI specific scheme categorization code |

---

## 2. Table: `dim_date`
Converts transaction and NAV dates into structured components for time-series analytics.

| Column Name | Data Type | Key / Constraint | Business Description |
|---|---|---|---|
| `date` | TEXT | PRIMARY KEY | Calendar Date in ISO-8601 format (YYYY-MM-DD) |
| `year` | INTEGER | NOT NULL | Calendar Year (e.g. 2024) |
| `quarter` | INTEGER | NOT NULL | Calendar Quarter (1, 2, 3, or 4) |
| `month` | INTEGER | NOT NULL | Month integer value (1 to 12) |
| `month_name` | TEXT | NOT NULL | Month name in English (e.g. January, October) |
| `day` | INTEGER | NOT NULL | Day of month (1 to 31) |
| `day_of_week` | TEXT | NOT NULL | Day name (e.g. Monday, Saturday) |
| `is_weekend` | INTEGER | NOT NULL | Flag: 1 if Saturday or Sunday, else 0 |

---

## 3. Table: `fact_nav`
Time-series log of Net Asset Values (NAV) for each scheme. Missing weekend/holiday entries are forward-filled.

| Column Name | Data Type | Key / Constraint | Business Description |
|---|---|---|---|
| `amfi_code` | INTEGER | FOREIGN KEY | Reference code linking to `dim_fund` |
| `date` | TEXT | FOREIGN KEY | Date string linked to `dim_date` |
| `nav` | REAL | NOT NULL | Net Asset Value (price per unit) in INR. Must be > 0. |

---

## 4. Table: `fact_transactions`
Contains retail transaction logs of mutual fund investments.

| Column Name | Data Type | Key / Constraint | Business Description |
|---|---|---|---|
| `transaction_id` | TEXT | PRIMARY KEY | Unique ID prefix `TX` followed by a sequential index |
| `investor_id` | TEXT | NOT NULL | ID code for retail investor |
| `transaction_date`| TEXT | FOREIGN KEY | Date string linked to `dim_date` |
| `amfi_code` | INTEGER | FOREIGN KEY | Reference code linking to `dim_fund` |
| `transaction_type`| TEXT | CHECK Constraint | Type: `SIP`, `Lumpsum`, or `Redemption` |
| `amount_inr` | REAL | NOT NULL | Total amount of transaction in INR. Must be > 0 |
| `state` | TEXT | | Indian state of residence for the retail investor |
| `city` | TEXT | | City of residence |
| `city_tier` | TEXT | | Tier level classification of city (e.g., Tier-1, Tier-2) |
| `age_group` | TEXT | | Age bracket category of investor (e.g., 18-30, 45+) |
| `gender` | TEXT | | Gender classification (e.g., Male, Female) |
| `annual_income_lakh`| REAL | | Self-declared investor income in Lakh INR |
| `payment_mode` | TEXT | | Transaction channel (UPI, Net Banking, Mandate, Cheque) |
| `kyc_status` | TEXT | CHECK Constraint | Flag indicating KYC verification: `Verified` or `Pending` |

---

## 5. Table: `fact_performance`
Captures historical returns, risk metrics, and ratings of schemes.

| Column Name | Data Type | Key / Constraint | Business Description |
|---|---|---|---|
| `amfi_code` | INTEGER | PRIMARY KEY | Scheme code linked to `dim_fund` |
| `return_1yr_pct` | REAL | | 1-Year annualized percentage return of the scheme |
| `return_3yr_pct` | REAL | | 3-Year annualized percentage return of the scheme |
| `return_5yr_pct` | REAL | | 5-Year annualized percentage return of the scheme |
| `benchmark_3yr_pct`| REAL | | Annualized benchmark returns over 3 years |
| `alpha` | REAL | | Outperformance indicator over benchmark returns |
| `beta` | REAL | | Volatility indicator relative to the benchmark index |
| `sharpe_ratio` | REAL | | Risk-adjusted return indicator |
| `sortino_ratio` | REAL | | Downside risk-adjusted return indicator |
| `std_dev_ann_pct`| REAL | | Historical annualized standard deviation (volatility) |
| `max_drawdown_pct`| REAL | | Maximum drawdown percentage fall from historical peak |
| `morningstar_rating`| INTEGER| | Morningstar 1 to 5 star rating metric |
| `risk_grade` | TEXT | | Grade assigned matching standard risk categories |

---

## 6. Table: `fact_aum`
Historical asset values managed by each Mutual Fund House (AMC).

| Column Name | Data Type | Key / Constraint | Business Description |
|---|---|---|---|
| `date` | TEXT | PRIMARY KEY | Ending date of the reporting period |
| `fund_house` | TEXT | PRIMARY KEY | AMC name managing the assets |
| `aum_lakh_crore` | REAL | | Assets Under Management in Lakh Crore INR |
| `aum_crore` | REAL | NOT NULL | Assets Under Management in Crore INR |
| `num_schemes` | INTEGER | | Active scheme count managed by the AMC |
