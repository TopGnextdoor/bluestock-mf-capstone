-- SQL Queries for Bluestock Mutual Fund Capstone Project

-- 1. Top 5 funds by AUM (as of the latest available date)
-- Business meaning: Find which mutual funds command the highest assets under management overall.
SELECT date, fund_house, aum_crore
FROM fact_aum
WHERE date = (SELECT MAX(date) FROM fact_aum)
ORDER BY aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month for SBI Bluechip Growth (amfi_code: 119551)
-- Business meaning: Month-on-month trend of NAV values for the SBI Bluechip scheme.
SELECT d.year, d.month_name, AVG(n.nav) AS avg_nav
FROM fact_nav n
JOIN dim_date d ON n.date = d.date
WHERE n.amfi_code = 119551
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- 3. SIP YoY Growth (Total Inflows by Year)
-- Business meaning: Trend analysis of total SIP investment volume over the years.
SELECT year, SUM(amount_inr) AS total_sip_amount,
       LAG(SUM(amount_inr)) OVER (ORDER BY year) AS prev_year_sip_amount,
       (SUM(amount_inr) - LAG(SUM(amount_inr)) OVER (ORDER BY year)) * 100.0 / LAG(SUM(amount_inr)) OVER (ORDER BY year) AS yoy_growth_pct
FROM fact_transactions t
JOIN dim_date d ON t.transaction_date = d.date
WHERE t.transaction_type = 'SIP'
GROUP BY d.year;

-- 4. Retail Transactions Count and Amount by State
-- Business meaning: Demographical distribution of mutual fund investments.
SELECT state, COUNT(*) AS txn_count, SUM(amount_inr) AS total_investment
FROM fact_transactions
GROUP BY state
ORDER BY total_investment DESC;

-- 5. Schemes with Expense Ratio < 1%
-- Business meaning: Identify cost-effective mutual funds for investors.
SELECT amfi_code, scheme_name, fund_house, expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- 6. Total Redemption volume by State and Tier
-- Business meaning: Detect which geographic segments are pulling out investments.
SELECT state, city_tier, COUNT(*) AS redemption_count, SUM(amount_inr) AS total_redeemed_inr
FROM fact_transactions
WHERE transaction_type = 'Redemption'
GROUP BY state, city_tier
ORDER BY total_redeemed_inr DESC;

-- 7. Fund Houses ranking by scheme counts
-- Business meaning: Identify the most prolific Asset Management Companies (AMCs) based on active product counts.
SELECT fund_house, COUNT(*) AS total_schemes_offered
FROM dim_fund
GROUP BY fund_house
ORDER BY total_schemes_offered DESC;

-- 8. Average returns over 1yr, 3yr and 5yr by Risk Category
-- Business meaning: Risk-to-reward ratio analysis across different risk classes.
SELECT f.risk_category, 
       AVG(p.return_1yr_pct) AS avg_return_1yr, 
       AVG(p.return_3yr_pct) AS avg_return_3yr, 
       AVG(p.return_5yr_pct) AS avg_return_5yr
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
GROUP BY f.risk_category;

-- 9. Top 10 Stocks by total weight in Holdings across all funds
-- Business meaning: Portfolio overlap and systemic exposure to specific equity stocks.
SELECT stock_name, stock_symbol, sector, SUM(weight_pct) AS total_cumulative_weight
FROM portfolio_holdings
GROUP BY stock_symbol
ORDER BY total_cumulative_weight DESC
LIMIT 10;

-- 10. Daily Closing Price Trend for NIFTY50 in 2025
-- Business meaning: Chronological index level tracking to check benchmark performance.
SELECT date, close_value
FROM benchmark_indices
WHERE index_name = 'NIFTY50' AND date LIKE '2025-%'
ORDER BY date ASC;
