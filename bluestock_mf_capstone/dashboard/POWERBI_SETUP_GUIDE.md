# Bluestock MF Dashboard — Power BI Setup Guide

## 📋 Step-by-Step Instructions

This guide walks you through recreating the Bluestock MF Dashboard in Power BI Desktop using the SQLite database and CSV files already prepared.

---

## 1. Connect Power BI to Data

### Option A: Import Cleaned CSVs (Recommended)
1. Open **Power BI Desktop**
2. Click **Get Data → Text/CSV**
3. Import these 10 CSV files from `data/processed/`:

| # | File | Table Name |
|---|------|-----------|
| 1 | `fund_master.csv` | `dim_fund` |
| 2 | `nav_history.csv` | `fact_nav` |
| 3 | `aum_by_fund_house.csv` | `fact_aum` |
| 4 | `monthly_sip_inflows.csv` | `monthly_sip_inflows` |
| 5 | `category_inflows.csv` | `category_inflows` |
| 6 | `industry_folio_count.csv` | `industry_folio_count` |
| 7 | `scheme_performance.csv` | `fact_performance` |
| 8 | `investor_transactions.csv` | `fact_transactions` |
| 9 | `portfolio_holdings.csv` | `portfolio_holdings` |
| 10 | `benchmark_indices.csv` | `benchmark_indices` |

4. Rename each table in Power Query to match the names above

### Option B: Connect via SQLite ODBC
1. Install the [SQLite ODBC Driver](http://www.ch-werner.de/sqliteodbc/)
2. In Power BI: **Get Data → ODBC**
3. Create a DSN pointing to `bluestock_mf.db`
4. Select all 11 tables

### Verify: All tables should show in the Model view with row counts matching:
- `dim_fund`: 40 rows
- `fact_nav`: 64,320 rows
- `fact_transactions`: 32,778 rows
- `fact_performance`: 40 rows
- `fact_aum`: 90 rows
- `monthly_sip_inflows`: 48 rows
- `category_inflows`: 144 rows
- `industry_folio_count`: 21 rows
- `portfolio_holdings`: 322 rows
- `benchmark_indices`: 8,050 rows

---

## 2. Create Relationships

Go to **Model View** and create these relationships:

```
dim_fund.amfi_code  →  fact_nav.amfi_code          (1:Many)
dim_fund.amfi_code  →  fact_transactions.amfi_code  (1:Many)
dim_fund.amfi_code  →  fact_performance.amfi_code   (1:1)
```

### Create a dim_date table
Add this DAX calculated table:

```dax
dim_date = 
ADDCOLUMNS(
    CALENDAR(DATE(2022,1,1), DATE(2026,6,1)),
    "Year", YEAR([Date]),
    "Quarter", QUARTER([Date]),
    "Month", MONTH([Date]),
    "MonthName", FORMAT([Date], "MMMM"),
    "YearMonth", FORMAT([Date], "YYYY-MM"),
    "Day", DAY([Date]),
    "DayOfWeek", FORMAT([Date], "dddd"),
    "IsWeekend", IF(WEEKDAY([Date],2) > 5, 1, 0)
)
```

Then create date relationships:
```
dim_date.Date  →  fact_nav.date              (1:Many)
dim_date.Date  →  fact_transactions.transaction_date  (1:Many)
```

> **Note**: You may need to change the `date` columns to Date type in Power Query first.

---

## 3. DAX Measures

Create a Measures table and add these key measures:

```dax
// KPI Measures
Total AUM (₹L Cr) = 
    DIVIDE(
        CALCULATE(SUM(fact_aum[aum_crore]), 
            FILTER(fact_aum, fact_aum[date] = MAX(fact_aum[date]))),
        100000, 0)

Latest SIP Inflow (₹Cr) = 
    CALCULATE(
        MAX(monthly_sip_inflows[sip_inflow_crore]),
        FILTER(monthly_sip_inflows, 
            monthly_sip_inflows[month] = MAX(monthly_sip_inflows[month])))

Total Folios (Cr) = 
    CALCULATE(
        MAX(industry_folio_count[total_folios_crore]),
        FILTER(industry_folio_count, 
            industry_folio_count[month] = MAX(industry_folio_count[month])))

Active Schemes = 
    CALCULATE(
        SUM(fact_aum[num_schemes]),
        FILTER(fact_aum, fact_aum[date] = MAX(fact_aum[date])))

// Performance Measures  
Avg Return 1Y = AVERAGE(fact_performance[return_1yr_pct])
Avg Return 3Y = AVERAGE(fact_performance[return_3yr_pct])
Avg Sharpe = AVERAGE(fact_performance[sharpe_ratio])

// Transaction Measures
Total Transaction Amt = SUM(fact_transactions[amount_inr])
Avg SIP Amount = 
    CALCULATE(AVERAGE(fact_transactions[amount_inr]),
        fact_transactions[transaction_type] = "SIP")
Transaction Count = COUNTROWS(fact_transactions)

// Net Inflow FY25
Net Inflow FY25 = 
    CALCULATE(SUM(category_inflows[net_inflow_crore]),
        category_inflows[month] >= "2024-04",
        category_inflows[month] <= "2025-03")
```

---

## 4. Page Layouts

### Page 1 — Industry Overview
| Visual | Type | Fields |
|--------|------|--------|
| KPI Card 1 | Card | `[Total AUM (₹L Cr)]` |
| KPI Card 2 | Card | `[Latest SIP Inflow (₹Cr)]` |
| KPI Card 3 | Card | `[Total Folios (Cr)]` |
| KPI Card 4 | Card | `[Active Schemes]` |
| AUM Trend | Line Chart | Axis: `fact_aum[date]`, Values: `SUM(fact_aum[aum_crore])` |
| AUM by AMC | Bar Chart | Axis: `fact_aum[fund_house]`, Values: `SUM(fact_aum[aum_crore])` |

### Page 2 — Fund Performance
| Visual | Type | Fields |
|--------|------|--------|
| Return vs Risk | Scatter | X: `return_3yr_pct`, Y: `std_dev_ann_pct`, Size: `AUM`, Legend: `category` |
| Fund Scorecard | Table | Columns: scheme_name, return_1yr_pct, return_3yr_pct, sharpe_ratio, morningstar_rating, risk_grade |
| NAV vs Benchmark | Line | Axis: date, Values: nav (normalized), benchmark close_value (normalized) |
| Slicers | Slicer | fund_house, category, plan |

### Page 3 — Investor Analytics
| Visual | Type | Fields |
|--------|------|--------|
| By State | Bar Chart (horizontal) | Axis: `state`, Values: `SUM(amount_inr)` |
| Type Split | Donut | Legend: `transaction_type`, Values: `SUM(amount_inr)` |
| Age vs SIP | Bar Chart | Axis: `age_group`, Values: `[Avg SIP Amount]` |
| Monthly Volume | Line Chart | Axis: `transaction_date` (Month), Values: `COUNT(transaction_id)` |
| Slicers | Slicer | state, age_group, city_tier |

### Page 4 — SIP & Market Trends
| Visual | Type | Fields |
|--------|------|--------|
| SIP vs Nifty | Combo (Bar+Line) | Bar: `sip_inflow_crore`, Line: Nifty50 `close_value`, Axis: month |
| Category Heatmap | Matrix with conditional formatting | Rows: category, Columns: month, Values: net_inflow_crore |
| Top 5 FY25 | Bar Chart | Axis: category, Values: `SUM(net_inflow_crore)`, Filter: month 2024-04 to 2025-03, Top N = 5 |

---

## 5. Drill-Through Page

1. Create a new page called **"NAV Detail"**
2. Add a **Drill-through field**: `dim_fund[amfi_code]`
3. Add:
   - Card visuals for scheme_name, fund_house, category, risk
   - Line chart: date vs nav
   - KPI cards for return_1yr_pct, sharpe_ratio, morningstar_rating
4. Right-click any fund in the scorecard table → **Drill through → NAV Detail**

---

## 6. Apply Bluestock Theme

Save this JSON as `bluestock_theme.json` and import via **View → Themes → Browse for themes**:

```json
{
    "name": "Bluestock",
    "dataColors": [
        "#1E90FF", "#00D4FF", "#00E676", "#FF9100",
        "#FF4081", "#BB86FC", "#FFD740", "#64FFDA"
    ],
    "background": "#0A0E27",
    "foreground": "#F0F4FF",
    "tableAccent": "#1E90FF",
    "visualStyles": {
        "*": {
            "*": {
                "background": [{"color": {"solid": {"color": "#111836"}}}],
                "border": [{"color": {"solid": {"color": "#1A2248"}}}]
            }
        }
    }
}
```

---

## 7. Export

1. **Save as .pbix**: File → Save As → `bluestock_mf_dashboard.pbix`
2. **Export to PDF**: File → Export → Export to PDF
3. **Export PNGs**: For each page, use **File → Export → Export to Image (PNG)**
   - Or use Print Screen/Snipping Tool for each page

---

## ✅ Deliverables Checklist

| Deliverable | Status |
|------------|--------|
| `bluestock_mf_dashboard.pbix` | Create in Power BI Desktop |
| `Dashboard.pdf` | ✅ Generated (`dashboard/Dashboard.pdf`) |
| Page 1 PNG — Industry Overview | ✅ Generated (`dashboard/Page1_Industry_Overview.png`) |
| Page 2 PNG — Fund Performance | ✅ Generated (`dashboard/Page2_Fund_Performance.png`) |
| Page 3 PNG — Investor Analytics | ✅ Generated (`dashboard/Page3_Investor_Analytics.png`) |
| Page 4 PNG — SIP & Market Trends | ✅ Generated (`dashboard/Page4_SIP_Market_Trends.png`) |
| Interactive Web Dashboard | ✅ Generated (`dashboard/index.html`) |
