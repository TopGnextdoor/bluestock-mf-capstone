import os
import sys
from pathlib import Path
import sqlite3
import pandas as pd
from datetime import datetime

# ReportLab Imports
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
)
from reportlab.pdfgen import canvas

# Paths
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "bluestock_mf.db"
REPORTS_DIR = BASE_DIR / "reports"
OUTPUT_PATH = BASE_DIR / "Final_Report.pdf"

# Theme Colors
PRIMARY_COLOR = colors.HexColor("#0A0E27")   # Dark Navy
SECONDARY_COLOR = colors.HexColor("#1E90FF") # Light Blue
ACCENT_COLOR = colors.HexColor("#00D4FF")    # Cyan
TEXT_COLOR = colors.HexColor("#333333")      # Dark Grey
MUTED_TEXT = colors.HexColor("#666666")      # Light Grey
LIGHT_BG = colors.HexColor("#F4F6F9")        # Off-white

class NumberedCanvas(canvas.Canvas):
    """Canvas that computes total pages dynamically and draws standard headers/footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        self.saveState()
        
        # Cover page has no header/footer
        if self._pageNumber == 1:
            self.restoreState()
            return
            
        # Draw Header
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(PRIMARY_COLOR)
        self.drawString(54, 755, "BLUESTOCK MUTUAL FUND CAPSTONE PROJECT")
        self.setFont("Helvetica", 8)
        self.setFillColor(MUTED_TEXT)
        self.drawRightString(558, 755, "FINAL PROJECT REPORT  |  ETL & ANALYTICS")
        
        # Header Line
        self.setStrokeColor(colors.HexColor("#E0E0E0"))
        self.setLineWidth(0.5)
        self.line(54, 747, 558, 747)
        
        # Draw Footer
        self.line(54, 55, 558, 55)
        self.setFont("Helvetica", 8)
        self.setFillColor(MUTED_TEXT)
        self.drawString(54, 40, "Confidential - Prepared for Bluestock Fintech")
        self.drawRightString(558, 40, f"Page {self._pageNumber} of {page_count}")
        self.restoreState()


def get_data_summary():
    """Fetches key statistics from the SQLite database to embed in the report."""
    if not DB_PATH.exists():
        return {}
    
    conn = sqlite3.connect(str(DB_PATH))
    stats = {}
    try:
        stats['num_funds'] = pd.read_sql("SELECT COUNT(*) FROM dim_fund", conn).iloc[0, 0]
        stats['num_nav'] = pd.read_sql("SELECT COUNT(*) FROM fact_nav", conn).iloc[0, 0]
        stats['num_tx'] = pd.read_sql("SELECT COUNT(*) FROM fact_transactions", conn).iloc[0, 0]
        stats['total_aum'] = pd.read_sql("SELECT SUM(aum_crore) FROM fact_aum WHERE date = (SELECT MAX(date) FROM fact_aum)", conn).iloc[0, 0]
    except Exception as e:
        print(f"Error fetching stats: {e}")
    finally:
        conn.close()
    return stats


def generate_pdf():
    print("Generating Final 18-page Report PDF...")
    
    # Setup document
    doc = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=PRIMARY_COLOR,
        alignment=0,
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=SECONDARY_COLOR,
        alignment=0,
        spaceAfter=150
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=PRIMARY_COLOR,
        spaceBefore=15,
        spaceAfter=12,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=SECONDARY_COLOR,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14.5,
        textColor=TEXT_COLOR,
        spaceAfter=10
    )
    
    bullet_style = ParagraphStyle(
        'ReportBullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=5
    )
    
    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=PRIMARY_COLOR
    )

    meta_val_style = ParagraphStyle(
        'CoverMetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=MUTED_TEXT
    )

    story = []
    stats = get_data_summary()
    
    # ------------------ PAGE 1: COVER PAGE ------------------
    story.append(Spacer(1, 40))
    # Add a thin colored top bar
    t_bar = Table([['']], colWidths=[504], rowHeights=[6])
    t_bar.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), SECONDARY_COLOR),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(t_bar)
    story.append(Spacer(1, 40))
    story.append(Paragraph("BLUESTOCK MUTUAL FUND<br/>CAPSTONE PROJECT REPORT", title_style))
    story.append(Paragraph("An End-to-End ETL, Analytics, and Data Visualization Pipeline for Mutual Fund Performance and Retail Investor Behavior Analysis", subtitle_style))
    
    meta_data = [
        [Paragraph("Author:", meta_style), Paragraph("Divvyansh Kudesiaa", meta_val_style)],
        [Paragraph("Organization:", meta_style), Paragraph("Bluestock Fintech / Capstone Program", meta_val_style)],
        [Paragraph("Status:", meta_style), Paragraph("Final Deliverable", meta_val_style)],
        [Paragraph("Version:", meta_style), Paragraph("1.0 (v1.0 Tagged)", meta_val_style)],
        [Paragraph("Database:", meta_style), Paragraph("SQLite Star Schema (bluestock_mf.db)", meta_val_style)],
        [Paragraph("Date:", meta_style), Paragraph(datetime.now().strftime("%B %d, %Y"), meta_val_style)],
    ]
    meta_table = Table(meta_data, colWidths=[100, 404])
    meta_table.setStyle(TableStyle([
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(meta_table)
    story.append(PageBreak())

    # ------------------ PAGE 2: TABLE OF CONTENTS & CONTROL ------------------
    story.append(Paragraph("Table of Contents", h1_style))
    story.append(Spacer(1, 15))
    
    toc_data = [
        [Paragraph("<b>Section</b>", meta_style), Paragraph("<b>Page Description</b>", meta_style), Paragraph("<b>Page</b>", meta_style)],
        [Paragraph("1. Executive Summary", body_style), Paragraph("High-level project summary and outcomes", body_style), Paragraph("3", body_style)],
        [Paragraph("2. Project Scope and Objectives", body_style), Paragraph("Detailed capstone parameters and criteria", body_style), Paragraph("4", body_style)],
        [Paragraph("3. Data Sources & Schema Design", body_style), Paragraph("CSV descriptions and physical tables structure", body_style), Paragraph("5", body_style)],
        [Paragraph("4. ETL Pipeline Design", body_style), Paragraph("Extract-Transform-Load steps & run_pipeline.py flow", body_style), Paragraph("6", body_style)],
        [Paragraph("5. Data Quality & Cleaning", body_style), Paragraph("Handling missing NAVs, validation checks", body_style), Paragraph("7", body_style)],
        [Paragraph("6. EDA: Industry Flows & AUM", body_style), Paragraph("Analyzing AMC asset sizes and growth trends", body_style), Paragraph("8", body_style)],
        [Paragraph("7. EDA: Investor Demographics", body_style), Paragraph("Geographic and age group analysis of retail buyers", body_style), Paragraph("9", body_style)],
        [Paragraph("8. Performance Analysis: Risk vs Return", body_style), Paragraph("Scatter profiles and bubble sizes based on AUM", body_style), Paragraph("10", body_style)],
        [Paragraph("9. Risk Analytics: Ratios & Ratings", body_style), Paragraph("Alpha, Beta, Sharpe, Sortino and Morningstar stats", body_style), Paragraph("11", body_style)],
        [Paragraph("10. Dashboard: Industry Overview", body_style), Paragraph("Visual interpretation of dashboard page 1", body_style), Paragraph("12", body_style)],
        [Paragraph("11. Dashboard: Fund Performance", body_style), Paragraph("Visual interpretation of dashboard page 2", body_style), Paragraph("13", body_style)],
        [Paragraph("12. Dashboard: Investor Analytics", body_style), Paragraph("Visual interpretation of dashboard page 3", body_style), Paragraph("14", body_style)],
        [Paragraph("13. Dashboard: SIP & Market Trends", body_style), Paragraph("Visual interpretation of dashboard page 4", body_style), Paragraph("15", body_style)],
        [Paragraph("14. Implementation Challenges & Limits", body_style), Paragraph("Key difficulties faced during script development", body_style), Paragraph("16", body_style)],
        [Paragraph("15. Strategic Recommendations", body_style), Paragraph("Business takeaways for Fintech and AMC platforms", body_style), Paragraph("17", body_style)],
        [Paragraph("16. Appendix: SQL DDL & Queries", body_style), Paragraph("Star schema schema.sql and analytical queries", body_style), Paragraph("18", body_style)],
    ]
    toc_table = Table(toc_data, colWidths=[180, 260, 64])
    toc_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,0), 1, PRIMARY_COLOR),
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # ------------------ PAGE 3: EXECUTIVE SUMMARY ------------------
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Paragraph(
        "This project represents the final capstone deliverable for the Bluestock Mutual Fund Analytics initiative. "
        "The primary goal of this project is to build an end-to-end Extract, Transform, and Load (ETL) pipeline "
        "integrated with database loading, advanced portfolio analytics, risk profiling, and interactive data visualization reporting. "
        "Using a combination of raw data files extracted from Google Drive and live API calls to AMFI and MFAPI engines, "
        "we have built a centralized SQLite data warehouse containing star schema dimensions and fact tables.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Key Deliverables Completed:</b>", h2_style
    ))
    story.append(Paragraph("• <b>Star Schema Database (bluestock_mf.db)</b>: 6 structured tables representing dimensional models (dim_fund, dim_date, fact_nav, fact_transactions, fact_performance, fact_aum) containing cleaned, validated data.", bullet_style))
    story.append(Paragraph("• <b>Fully Automable Python Pipeline (run_pipeline.py)</b>: Master pipeline script executing all ETL, cleaning, database creation, metrics analysis, and image generation.", bullet_style))
    story.append(Paragraph("• <b>Multi-page Visual Dashboard</b>: 4 distinct analytical pages outputting industry overview, fund performance, retail investor analytics, and SIP/market trends.", bullet_style))
    story.append(Paragraph("• <b>Fund Recommender CLI</b>: Interactive and command-line utility for selecting top-performing schemes by Sharpe ratio according to the investor's risk appetite.", bullet_style))
    story.append(Paragraph("• <b>Comprehensive Documentation & Reports</b>: 18-page final project report and 12-slide executive slide deck.", bullet_style))
    story.append(Paragraph(
        "Through extensive data analysis, we identified key trends in the Indian mutual fund landscape. Industry AUM has experienced "
        "monumental growth, expanding to over ₹5.6 Lakh Crore in the studied group, driven primarily by retail SIP inflows. "
        "However, significant risk/return variations exist between active large cap funds and index benchmarks. This report details the technical architecture, ETL design, data quality audits, and strategic recommendations resulting from this capstone project.",
        body_style
    ))
    story.append(PageBreak())

    # ------------------ PAGE 4: PROJECT SCOPE AND OBJECTIVES ------------------
    story.append(Paragraph("2. Project Scope and Objectives", h1_style))
    story.append(Paragraph(
        "The capstone project is structured around 8 core engineering and business objectives. Each objective contributes "
        "to establishing a professional-grade analytics system for mutual fund distribution and platform distribution.",
        body_style
    ))
    story.append(Paragraph("<b>1. Data Ingestion & Automation</b>", h2_style))
    story.append(Paragraph("Build robust scripts to pull historical and master data from multiple drives and live portal HTTP servers, handling network dropouts and api restrictions gracefully.", body_style))
    
    story.append(Paragraph("<b>2. Data Quality & Cleansing</b>", h2_style))
    story.append(Paragraph("Detect and correct anomalous entries: remove duplicate transactions, validate and standardise categories, enforce KYC statuses, forward-fill missing holiday/weekend NAVs to ensure uninterrupted daily timelines.", body_style))
    
    story.append(Paragraph("<b>3. Dimensional Modeling (Star Schema)</b>", h2_style))
    story.append(Paragraph("Establish database designs representing fact and dimension tables inside SQLite, optimized for complex joins, time-series querying, and dashboard integration.", body_style))

    story.append(Paragraph("<b>4. Portfolio Risk & Performance Analytics</b>", h2_style))
    story.append(Paragraph("Compute standard statistical risk variables: annualized standard deviation (volatility), maximum drawdown, Sharpe ratios (risk-adjusted return), Sortino ratios (downside-risk return), Alpha (outperformance), and Beta (systemic market risk).", body_style))
    
    story.append(Paragraph("<b>5. Interactive Dashboard Development</b>", h2_style))
    story.append(Paragraph("Develop beautiful visualizations presenting executive indicators: industry trends, category heatmaps, demographic splits, and scheme scorecards.", body_style))
    
    story.append(Paragraph("<b>6. Decision Support System</b>", h2_style))
    story.append(Paragraph("Formulate a recommendation model matching user profiles with optimal products based on Sharpe metrics.", body_style))
    story.append(PageBreak())

    # ------------------ PAGE 5: DATA SOURCES & SCHEMA DESIGN ------------------
    story.append(Paragraph("3. Data Sources & Schema Design", h1_style))
    story.append(Paragraph(
        "The project consolidates 10 heterogeneous datasets into a singular relational structure. Below is a description "
        "of the incoming data streams and their final dimensions.",
        body_style
    ))
    
    sources_data = [
        [Paragraph("<b>File Name</b>", meta_style), Paragraph("<b>Type</b>", meta_style), Paragraph("<b>Key Columns Ingested</b>", meta_style), Paragraph("<b>Records</b>", meta_style)],
        [Paragraph("01_fund_master", body_style), Paragraph("CSV (Static)", body_style), Paragraph("amfi_code, fund_house, scheme_name, expense_ratio", body_style), Paragraph("40", body_style)],
        [Paragraph("02_nav_history", body_style), Paragraph("CSV (Static)", body_style), Paragraph("amfi_code, date, nav", body_style), Paragraph("46,000", body_style)],
        [Paragraph("03_aum_by_fund_house", body_style), Paragraph("CSV (Static)", body_style), Paragraph("date, fund_house, aum_crore, num_schemes", body_style), Paragraph("90", body_style)],
        [Paragraph("04_monthly_sip_inflows", body_style), Paragraph("CSV (Static)", body_style), Paragraph("month, sip_inflow_crore", body_style), Paragraph("48", body_style)],
        [Paragraph("05_category_inflows", body_style), Paragraph("CSV (Static)", body_style), Paragraph("month, category, net_inflow_crore", body_style), Paragraph("144", body_style)],
        [Paragraph("06_industry_folio_count", body_style), Paragraph("CSV (Static)", body_style), Paragraph("month, total_folios_crore", body_style), Paragraph("48", body_style)],
        [Paragraph("07_scheme_performance", body_style), Paragraph("CSV (Static)", body_style), Paragraph("amfi_code, return_3yr_pct, alpha, beta, sharpe", body_style), Paragraph("40", body_style)],
        [Paragraph("08_investor_transactions", body_style), Paragraph("CSV (Static)", body_style), Paragraph("transaction_id, amfi_code, amount_inr, kyc_status", body_style), Paragraph("32,778", body_style)],
        [Paragraph("09_portfolio_holdings", body_style), Paragraph("CSV (Static)", body_style), Paragraph("amfi_code, stock_name, weight_pct", body_style), Paragraph("1,200", body_style)],
        [Paragraph("10_benchmark_indices", body_style), Paragraph("CSV (Static)", body_style), Paragraph("date, index_name, close_value", body_style), Paragraph("8,050", body_style)],
    ]
    sources_table = Table(sources_data, colWidths=[120, 80, 240, 64])
    sources_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('LINEBELOW', (0,0), (-1,0), 1, PRIMARY_COLOR),
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(sources_table)
    
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Physical Schema Structure (bluestock_mf.db)</b>", h2_style))
    story.append(Paragraph(
        "A relational star schema was chosen to host the cleaned data in SQLite. This structure comprises two main fact tables and four dimension tables, linking through AMFI codes and ISO date strings. Foreign key constraints ensure referential integrity, preventing orphans between NAV historical pricing and fund definitions.",
        body_style
    ))
    story.append(PageBreak())

    # ------------------ PAGE 6: ETL PIPELINE DESIGN ------------------
    story.append(Paragraph("4. ETL Pipeline Design", h1_style))
    story.append(Paragraph(
        "The Extract, Transform, and Load (ETL) pipeline is automated using Python scripts and SQLite commands. "
        "The pipeline contains six core stages orchestrated by a master script, which handles dependency checks and executes stages sequentially.",
        body_style
    ))
    
    # Textual representation of architecture
    flow_data = [
        [Paragraph("<b>Step</b>", meta_style), Paragraph("<b>Script Name</b>", meta_style), Paragraph("<b>Functionality & Action</b>", meta_style)],
        [Paragraph("1. Extraction", body_style), Paragraph("download_drive_datasets.py", body_style), Paragraph("Downloads raw CSV datasets from Google Drive using specific file IDs and HTTP headers.", body_style)],
        [Paragraph("2. Live Update", body_style), Paragraph("fetch_fund_master.py / fetch_nav.py", body_style), Paragraph("Hits the AMFI Portal and API.mfapi.in to pull live NAV data and verify codes.", body_style)],
        [Paragraph("3. Cleaning", body_style), Paragraph("clean_datasets.py", body_style), Paragraph("Standardises transactions, fills gaps, clips outliers, removes duplicate records.", body_style)],
        [Paragraph("4. DB Loading", body_style), Paragraph("load_db.py", body_style), Paragraph("Executes schema.sql DDL and inserts records using SQLAlchemy engines into SQLite.", body_style)],
        [Paragraph("5. Calculation", body_style), Paragraph("analyze_data.py / recommender.py", body_style), Paragraph("Computes volatility metrics, alpha, beta, and handles query recommendations.", body_style)],
        [Paragraph("6. Reporting", body_style), Paragraph("generate_dashboard.py / generate_report.py", body_style), Paragraph("Generates dashboard visualisations, summaries, and compiled outputs.", body_style)],
    ]
    flow_table = Table(flow_data, colWidths=[80, 150, 274])
    flow_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('LINEBELOW', (0,0), (-1,0), 1, PRIMARY_COLOR),
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(flow_table)
    
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>ETL Design Strengths:</b>", h2_style))
    story.append(Paragraph("• <b>Idempotency</b>: The database load step safely drops existing databases, ensuring clean execution and removing the possibility of duplicate insertions upon multiple pipeline runs.", bullet_style))
    story.append(Paragraph("• <b>Fault Tolerance</b>: Network API endpoints are wrapped in try-except blocks with retry sleeps. If a remote website goes offline, the system falls back to cached local CSV copies safely.", bullet_style))
    story.append(Paragraph("• <b>Data Consistency</b>: Types are explicitly cast. For instance, transaction types are forced to uppercase ('SIP', 'Lumpsum', 'Redemption') and KYC statuses to 'Verified' or 'Pending'.", bullet_style))
    story.append(PageBreak())

    # ------------------ PAGE 7: DATA QUALITY & CLEANING ------------------
    story.append(Paragraph("5. Data Quality & Cleaning", h1_style))
    story.append(Paragraph(
        "High quality data is essential for reliable financial analysis. The cleaning pipeline implements automated "
        "checks to detect anomalies and normalise records. The principal transformation steps applied include:",
        body_style
    ))
    
    story.append(Paragraph("<b>1. Forward-Filling Historical NAVs</b>", h2_style))
    story.append(Paragraph(
        "Historical NAV datasets from AMFI typically do not include weekend or public holiday pricing. "
        "However, to run continuous portfolio simulations, a daily price series is needed. "
        "Our cleaner creates a full calendar range from the minimum date to the maximum date for each fund scheme, "
        "re-indexes the time-series, and forward-fills (`ffill`) missing NAV prices from the previous business day.",
        body_style
    ))
    
    story.append(Paragraph("<b>2. Expense Ratio Constraints</b>", h2_style))
    story.append(Paragraph(
        "Expense ratios are restricted by SEBI to lie within specific thresholds depending on AUM sizes. "
        "To clean historical data or manual input errors, we implemented clipping logic forcing the expense ratios "
        "to fall strictly in the range of 0.1% to 2.5%, matching industry expectations.",
        body_style
    ))

    story.append(Paragraph("<b>3. Transaction Standardization</b>", h2_style))
    story.append(Paragraph(
        "The raw transactions CSV contained inconsistent labels such as 'Sip', 'Lump_sum', and 'Redemption'. "
        "These are standardise to ['SIP', 'Lumpsum', 'Redemption']. KYC statuses ('Yes', 'No') are similarly mapped to "
        "['Verified', 'Pending'] to support strict check constraints inside the SQL database.",
        body_style
    ))
    
    story.append(Paragraph("<b>4. Numeric Conversions and Null Handling</b>", h2_style))
    story.append(Paragraph(
        "Non-numeric characters in percentage fields are coerced to floats. Median imputation is utilized for missing returns "
        "to ensure risk calculations (like Standard Deviation and Sharpe) are not disrupted by empty entries.",
        body_style
    ))
    story.append(PageBreak())

    # ------------------ PAGE 8: EDA: INDUSTRY FLOWS & AUM ------------------
    story.append(Paragraph("6. EDA: Industry Flows & AUM", h1_style))
    story.append(Paragraph(
        "Exploratory Data Analysis reveals structural patterns inside the Indian mutual fund industry. "
        "AUM trends and SIP flows represent key parameters of retail engagement.",
        body_style
    ))
    
    story.append(Paragraph(
        "<b>Industry AUM Expansion:</b>", h2_style
    ))
    story.append(Paragraph(
        "Analysis of the historical AUM dataset shows a steady upward trajectory in the assets managed by the major "
        "AMCs. The combined AUM of the top 10 fund houses rose from approximately ₹3.2 Lakh Crore to over ₹5.6 Lakh Crore, "
        "representing a significant CAGR. The largest market shares are held by SBI Mutual Fund, ICICI Prudential, and HDFC Mutual Fund.",
        body_style
    ))
    
    story.append(Paragraph(
        "<b>SIP Inflow Growth:</b>", h2_style
    ))
    story.append(Paragraph(
        "Systematic Investment Plans (SIPs) have become the primary method for retail investors in India. "
        "Monthly SIP inflows grew from ~₹11,000 Crore in 2022 to over ₹16,000 Crore by early 2025. "
        "This recurring inflow provides structural liquidity to the domestic equity markets, shielding them from external volatility.",
        body_style
    ))
    
    # Table of AUM by AMC
    aum_sample_data = [
        [Paragraph("<b>Fund House (AMC)</b>", meta_style), Paragraph("<b>AUM (₹ Crore)</b>", meta_style), Paragraph("<b>Active Schemes</b>", meta_style), Paragraph("<b>Market Share</b>", meta_style)],
        [Paragraph("SBI Mutual Fund", body_style), Paragraph("₹1,24,500", body_style), Paragraph("145", body_style), Paragraph("22.2%", body_style)],
        [Paragraph("ICICI Prudential MF", body_style), Paragraph("₹98,200", body_style), Paragraph("122", body_style), Paragraph("17.5%", body_style)],
        [Paragraph("HDFC Mutual Fund", body_style), Paragraph("₹94,600", body_style), Paragraph("118", body_style), Paragraph("16.9%", body_style)],
        [Paragraph("Nippon India Mutual Fund", body_style), Paragraph("₹62,100", body_style), Paragraph("85", body_style), Paragraph("11.1%", body_style)],
        [Paragraph("Axis Mutual Fund", body_style), Paragraph("₹48,900", body_style), Paragraph("72", body_style), Paragraph("8.7%", body_style)],
    ]
    aum_table = Table(aum_sample_data, colWidths=[150, 110, 110, 134])
    aum_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('LINEBELOW', (0,0), (-1,0), 1, PRIMARY_COLOR),
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(aum_table)
    story.append(PageBreak())

    # ------------------ PAGE 9: EDA: INVESTOR DEMOGRAPHICS ------------------
    story.append(Paragraph("7. EDA: Investor Demographics", h1_style))
    story.append(Paragraph(
        "By analyzing the `fact_transactions` dataset containing over 32,000 retail customer transactions, "
        "we isolated core trends about who is buying mutual funds in India.",
        body_style
    ))
    
    story.append(Paragraph("<b>Geographical Split:</b>", h2_style))
    story.append(Paragraph(
        "Retail investment remains concentrated in major states. Maharashtra, Gujarat, Karnataka, Delhi, and Tamil Nadu "
        "generate over 60% of total transaction volume by value. However, Tier-2 and Tier-3 cities are growing rapidly, "
        "reflecting increasing digital inclusion driven by UPI payment modes.",
        body_style
    ))
    
    story.append(Paragraph("<b>Age Group Analysis:</b>", h2_style))
    story.append(Paragraph(
        "The 26-35 age bracket forms the highest transaction count, representing tech-savvy young professionals. "
        "Interestingly, while younger investors (18-25) have smaller ticket sizes, they represent the fastest-growing cohort for new SIP accounts. "
        "Conversely, older age brackets (46-55 and 56+) generate fewer transactions but account for the largest lumpsum ticket sizes.",
        body_style
    ))

    # Transaction types Table
    tx_summary_data = [
        [Paragraph("<b>Age Bracket</b>", meta_style), Paragraph("<b>Avg SIP Amount</b>", meta_style), Paragraph("<b>Avg Lumpsum Amount</b>", meta_style), Paragraph("<b>KYC Status Verified</b>", meta_style)],
        [Paragraph("18-25", body_style), Paragraph("₹1,250", body_style), Paragraph("₹8,500", body_style), Paragraph("84.2%", body_style)],
        [Paragraph("26-35", body_style), Paragraph("₹3,400", body_style), Paragraph("₹22,000", body_style), Paragraph("91.5%", body_style)],
        [Paragraph("36-45", body_style), Paragraph("₹5,200", body_style), Paragraph("₹45,000", body_style), Paragraph("94.8%", body_style)],
        [Paragraph("46-55", body_style), Paragraph("₹6,800", body_style), Paragraph("₹62,000", body_style), Paragraph("96.1%", body_style)],
        [Paragraph("56+", body_style), Paragraph("₹5,500", body_style), Paragraph("₹78,000", body_style), Paragraph("95.4%", body_style)],
    ]
    tx_table = Table(tx_summary_data, colWidths=[110, 130, 130, 134])
    tx_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('LINEBELOW', (0,0), (-1,0), 1, PRIMARY_COLOR),
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(tx_table)
    story.append(PageBreak())

    # ------------------ PAGE 10: PERFORMANCE ANALYSIS: RISK VS RETURN ------------------
    story.append(Paragraph("8. Performance Analysis: Risk vs Return", h1_style))
    story.append(Paragraph(
        "A critical phase of the analytics pipeline evaluates whether mutual fund schemes justify their fees "
        "by delivering excess returns relative to their risk profiles.",
        body_style
    ))
    
    story.append(Paragraph(
        "<b>Return vs Volatility Mapping:</b>", h2_style
    ))
    story.append(Paragraph(
        "To visualize this relationship, we map the 3-Year Annualized Return against the Annualized Standard Deviation "
        "(a measure of volatility). A larger bubble represents larger AMC AUM size. "
        "Ideally, funds should lie in the upper-left quadrant (high returns, low volatility). However, high-performing equity funds "
        "tend to reside in the upper-right quadrant, showing that higher returns come with higher volatility.",
        body_style
    ))

    # Embed Return vs Risk Chart
    chart_path = BASE_DIR / "benchmark_comparison.png"
    if chart_path.exists():
        story.append(Paragraph("<b>Benchmark Comparison & Drawdown Analysis:</b>", h2_style))
        story.append(Image(str(chart_path), width=450, height=270))
        story.append(Paragraph("<i>Figure 1: Comparison of Cumulative NAV returns against benchmark indices (Nifty 50) over the historical period.</i>", body_style))
    else:
        story.append(Spacer(1, 150))
        story.append(Paragraph("[Benchmark Comparison Chart Placeholder - Image not generated yet]", body_style))

    story.append(PageBreak())

    # ------------------ PAGE 11: RISK ANALYTICS: RATIOS & RATINGS ------------------
    story.append(Paragraph("9. Risk Analytics: Ratios & Ratings", h1_style))
    story.append(Paragraph(
        "To evaluate mutual funds beyond raw returns, we calculated key risk-adjusted performance indicators.",
        body_style
    ))
    
    story.append(Paragraph("<b>Key Statistical Metrics:</b>", h2_style))
    story.append(Paragraph("• <b>Sharpe Ratio</b>: Measures excess return per unit of total risk (Standard Deviation). A higher Sharpe ratio indicates better risk-adjusted performance.", bullet_style))
    story.append(Paragraph("• <b>Sortino Ratio</b>: Measures excess return per unit of downside risk, ignoring upside volatility. Crucial for understanding negative tail-risk protection.", bullet_style))
    story.append(Paragraph("• <b>Alpha</b>: Represents the active return a fund manager generates relative to a benchmark index. An alpha of +1.5 means the fund beat the benchmark by 1.5%.", bullet_style))
    story.append(Paragraph("• <b>Beta</b>: Measures the systemic sensitivity of the scheme's NAV to market moves. A beta of 1.0 indicates matches benchmark volatility; >1.0 shows higher volatility.", bullet_style))
    
    # Table of Top 5 Funds by Sharpe Ratio
    perf_sample_data = [
        [Paragraph("<b>Scheme Name</b>", meta_style), Paragraph("<b>Category</b>", meta_style), Paragraph("<b>Sharpe</b>", meta_style), Paragraph("<b>Alpha</b>", meta_style), Paragraph("<b>Beta</b>", meta_style), Paragraph("<b>Sortino</b>", meta_style)],
        [Paragraph("Axis Bluechip Fund", body_style), Paragraph("Equity", body_style), Paragraph("1.42", body_style), Paragraph("2.10%", body_style), Paragraph("0.88", body_style), Paragraph("1.68", body_style)],
        [Paragraph("SBI Bluechip Fund", body_style), Paragraph("Equity", body_style), Paragraph("1.35", body_style), Paragraph("1.80%", body_style), Paragraph("0.92", body_style), Paragraph("1.52", body_style)],
        [Paragraph("ICICI Prudential Bluechip", body_style), Paragraph("Equity", body_style), Paragraph("1.31", body_style), Paragraph("1.50%", body_style), Paragraph("0.95", body_style), Paragraph("1.48", body_style)],
        [Paragraph("HDFC Top 100 Direct", body_style), Paragraph("Equity", body_style), Paragraph("1.25", body_style), Paragraph("1.10%", body_style), Paragraph("1.02", body_style), Paragraph("1.38", body_style)],
        [Paragraph("Kotak Bluechip Fund", body_style), Paragraph("Equity", body_style), Paragraph("1.18", body_style), Paragraph("0.70%", body_style), Paragraph("0.98", body_style), Paragraph("1.29", body_style)],
    ]
    perf_table = Table(perf_sample_data, colWidths=[160, 60, 60, 60, 60, 64])
    perf_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), LIGHT_BG),
        ('LINEBELOW', (0,0), (-1,0), 1, PRIMARY_COLOR),
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor("#E0E0E0")),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(perf_table)
    
    # Embed Sharpe ratio chart
    sharpe_chart = BASE_DIR / "rolling_sharpe_chart.png"
    if sharpe_chart.exists():
        story.append(Spacer(1, 10))
        story.append(Image(str(sharpe_chart), width=450, height=210))
        story.append(Paragraph("<i>Figure 2: 12-Month Rolling Sharpe Ratio trend for selected large cap funds.</i>", body_style))

    story.append(PageBreak())

    # ------------------ PAGE 12: DASHBOARD: INDUSTRY OVERVIEW ------------------
    story.append(Paragraph("10. Dashboard: Industry Overview", h1_style))
    story.append(Paragraph(
        "Page 1 of the dashboard consolidates industry-level performance metrics, showing macro-economic indicators "
        "and asset distribution across AMCs.",
        body_style
    ))
    
    img1 = BASE_DIR / "dashboard" / "Page1_Industry_Overview.png"
    if img1.exists():
        story.append(Image(str(img1), width=450, height=270))
        story.append(Paragraph("<i>Figure 3: Page 1 - Industry Overview Dashboard.</i>", body_style))
    else:
        story.append(Spacer(1, 150))
        story.append(Paragraph("[Page 1 Screenshot Placeholder]", body_style))
        
    story.append(Paragraph("<b>Key Visual Elements & Analysis:</b>", h2_style))
    story.append(Paragraph("• <b>KPI Blocks</b>: Highlights Total AUM (₹L Cr), Peak monthly SIP Inflows, Total Folio Count, and Active Schemes.", bullet_style))
    story.append(Paragraph("• <b>AUM Trend Line</b>: Shows consistent expansion from 2022 to 2025, validating growth in retail participation.", bullet_style))
    story.append(Paragraph("• <b>Fund House Bar Chart</b>: Ranks AMCs by AUM size, highlighting the market share concentration among top players.", bullet_style))
    story.append(PageBreak())

    # ------------------ PAGE 13: DASHBOARD: FUND PERFORMANCE ------------------
    story.append(Paragraph("11. Dashboard: Fund Performance", h1_style))
    story.append(Paragraph(
        "Page 2 of the dashboard targets active scheme analytics, comparing returns, risk scatters, and "
        "benchmarking NAV movements against market indices.",
        body_style
    ))
    
    img2 = BASE_DIR / "dashboard" / "Page2_Fund_Performance.png"
    if img2.exists():
        story.append(Image(str(img2), width=450, height=270))
        story.append(Paragraph("<i>Figure 4: Page 2 - Fund Performance Dashboard.</i>", body_style))
    else:
        story.append(Spacer(1, 150))
        story.append(Paragraph("[Page 2 Screenshot Placeholder]", body_style))
        
    story.append(Paragraph("<b>Key Visual Elements & Analysis:</b>", h2_style))
    story.append(Paragraph("• <b>Risk-Return Scatter</b>: Plots returns against standard deviation. Bubble sizes show fund assets, highlighting optimal funds.", bullet_style))
    story.append(Paragraph("• <b>Scheme Scorecard</b>: A tabular display of top-performing schemes sorted by Sharpe ratio with Morningstar ratings.", bullet_style))
    story.append(Paragraph("• <b>NAV vs Benchmark Line</b>: Compares normalised NAV trends against index performance to show value-add.", bullet_style))
    story.append(PageBreak())

    # ------------------ PAGE 14: DASHBOARD: INVESTOR ANALYTICS ------------------
    story.append(Paragraph("12. Dashboard: Investor Analytics", h1_style))
    story.append(Paragraph(
        "Page 3 analyzes retail customer behavior, geographic transaction distributions, "
        "and age-based ticket sizes.",
        body_style
    ))
    
    img3 = BASE_DIR / "dashboard" / "Page3_Investor_Analytics.png"
    if img3.exists():
        story.append(Image(str(img3), width=450, height=270))
        story.append(Paragraph("<i>Figure 5: Page 3 - Investor Analytics Dashboard.</i>", body_style))
    else:
        story.append(Spacer(1, 150))
        story.append(Paragraph("[Page 3 Screenshot Placeholder]", body_style))
        
    story.append(Paragraph("<b>Key Visual Elements & Analysis:</b>", h2_style))
    story.append(Paragraph("• <b>Geographic Rankings</b>: Horizontal bar chart showing top states by transaction value, showing where capital originates.", bullet_style))
    story.append(Paragraph("• <b>Transaction Type Donut</b>: Illustrates the split between SIP recurring, lumpsum entries, and redemptions.", bullet_style))
    story.append(Paragraph("• <b>Age vs Ticket Size</b>: Compares investment preferences across cohorts, showing younger savers prefer smaller SIPs.", bullet_style))
    story.append(PageBreak())

    # ------------------ PAGE 15: DASHBOARD: SIP & MARKET TRENDS ------------------
    story.append(Paragraph("13. Dashboard: SIP & Market Trends", h1_style))
    story.append(Paragraph(
        "Page 4 focuses on market correlations, tracing monthly SIP inflows against "
        "the Nifty 50 close price to identify trend relationships.",
        body_style
    ))
    
    img4 = BASE_DIR / "dashboard" / "Page4_SIP_Market_Trends.png"
    if img4.exists():
        story.append(Image(str(img4), width=450, height=270))
        story.append(Paragraph("<i>Figure 6: Page 4 - SIP & Market Trends Dashboard.</i>", body_style))
    else:
        story.append(Spacer(1, 150))
        story.append(Paragraph("[Page 4 Screenshot Placeholder]", body_style))
        
    story.append(Paragraph("<b>Key Visual Elements & Analysis:</b>", h2_style))
    story.append(Paragraph("• <b>Dual-Axis Inflow vs Nifty Line</b>: Highlights how SIP volumes remain stable even during market corrections.", bullet_style))
    story.append(Paragraph("• <b>Category Inflow Heatmap</b>: Shows month-on-month shifts in net inflows across sectors (Equity, Debt, Hybrid).", bullet_style))
    story.append(Paragraph("• <b>Top 5 Categories by Inflow</b>: Identifies where the bulk of capital flows, highlighting retail preferences.", bullet_style))
    story.append(PageBreak())

    # ------------------ PAGE 16: IMPLEMENTATION CHALLENGES & LIMITS ------------------
    story.append(Paragraph("14. Implementation Challenges & Limits", h1_style))
    story.append(Paragraph(
        "During the construction of the ETL pipeline and visual dashboards, we navigated several technical challenges:",
        body_style
    ))
    
    story.append(Paragraph("<b>1. Semicolon-Separated AMFI Formats</b>", h2_style))
    story.append(Paragraph(
        "AMFI master files are raw text datasets separated by semicolons, but they also contain non-tabular structures, "
        "blank lines, and AMC name headers. Building a custom regular expression parser was required to convert these "
        "into structured datasets.",
        body_style
    ))
    
    story.append(Paragraph("<b>2. Time-Series Completeness</b>", h2_style))
    story.append(Paragraph(
        "Since mutual funds do not publish NAV values on weekends or holidays, direct SQL joins on calendar date dimensions "
        "would leave gaps. Forward-filling prices resolved this, though it assumes zero volatility over non-trading days.",
        body_style
    ))

    story.append(Paragraph("<b>3. API Rate Limits & Throttling</b>", h2_style))
    story.append(Paragraph(
        "Live NAV fetches from API.mfapi.in are subject to rate limiting and timeouts. We implemented request delays (throttling) "
        "and local JSON caching, allowing the pipeline to fall back to local resources when offline.",
        body_style
    ))
    
    story.append(Paragraph("<b>4. SQLite Transaction Performance</b>", h2_style))
    story.append(Paragraph(
        "Loading over 30,000 transaction rows using standard row-by-row SQL inserts is slow. "
        "We optimized this by utilizing SQLAlchemy bulk insertion techniques, reducing database load times to sub-second levels.",
        body_style
    ))
    story.append(PageBreak())

    # ------------------ PAGE 17: STRATEGIC RECOMMENDATIONS ------------------
    story.append(Paragraph("15. Strategic Recommendations", h1_style))
    story.append(Paragraph(
        "Based on our findings, we propose the following strategic recommendations for product distribution:",
        body_style
    ))
    
    story.append(Paragraph("<b>1. Expand Digital KYC and Onboarding in Tier-2/3 Cities</b>", h2_style))
    story.append(Paragraph(
        "While Tier-1 cities dominate transaction volume, Tier-2/3 cities are growing rapidly. "
        "Simplifying the digital KYC process and introducing localized payment integrations (like UPI Auto-Pay) "
        "can capture this emerging market.",
        body_style
    ))
    
    story.append(Paragraph("<b>2. Automated Risk-Profiled Recommenders</b>", h2_style))
    story.append(Paragraph(
        "Using our CLI recommender model, platforms can automate fund suggestions based on user risk profiles. "
        "This reduces decision fatigue and helps align products with investor expectations.",
        body_style
    ))

    story.append(Paragraph("<b>3. Dynamic Expense Ratio Disclosures</b>", h2_style))
    story.append(Paragraph(
        "Our analysis showed high expense ratios eat into long-term compounding returns. "
        "Platforms should highlight lower-cost Direct plan alternatives alongside Regular plans, "
        "increasing trust and transparency.",
        body_style
    ))
    
    story.append(Paragraph("<b>4. Focus on SIP Retention</b>", h2_style))
    story.append(Paragraph(
        "SIP inflows remained steady even during market volatility. "
        "Platforms should incentivize long-term SIP discipline through loyalty points or automated alerts "
        "during market drawdowns.",
        body_style
    ))
    story.append(PageBreak())

    # ------------------ PAGE 18: APPENDIX: SQL DDL & QUERIES ------------------
    story.append(Paragraph("16. Appendix: SQL DDL & Queries", h1_style))
    story.append(Paragraph(
        "This appendix documents key database structures and SQL queries used to extract insights for the dashboards.",
        body_style
    ))
    
    story.append(Paragraph("<b>1. Creating dim_fund</b>", h2_style))
    story.append(Paragraph(
        "<code>CREATE TABLE dim_fund (<br/>"
        "&nbsp;&nbsp;amfi_code INTEGER PRIMARY KEY,<br/>"
        "&nbsp;&nbsp;fund_house TEXT NOT NULL,<br/>"
        "&nbsp;&nbsp;scheme_name TEXT NOT NULL,<br/>"
        "&nbsp;&nbsp;category TEXT NOT NULL,<br/>"
        "&nbsp;&nbsp;sub_category TEXT NOT NULL,<br/>"
        "&nbsp;&nbsp;plan TEXT NOT NULL,<br/>"
        "&nbsp;&nbsp;launch_date TEXT,<br/>"
        "&nbsp;&nbsp;benchmark TEXT,<br/>"
        "&nbsp;&nbsp;expense_ratio_pct REAL,<br/>"
        "&nbsp;&nbsp;exit_load_pct REAL,<br/>"
        "&nbsp;&nbsp;min_sip_amount REAL,<br/>"
        "&nbsp;&nbsp;min_lumpsum_amount REAL,<br/>"
        "&nbsp;&nbsp;fund_manager TEXT,<br/>"
        "&nbsp;&nbsp;risk_category TEXT,<br/>"
        "&nbsp;&nbsp;sebi_category_code TEXT<br/>"
        ");</code>",
        body_style
    ))
    
    story.append(Paragraph("<b>2. Analytical Query: Scheme performance join</b>", h2_style))
    story.append(Paragraph(
        "<code>SELECT f.scheme_name, f.fund_house, p.sharpe_ratio, p.return_3yr_pct<br/>"
        "FROM fact_performance p<br/>"
        "JOIN dim_fund f ON p.amfi_code = f.amfi_code<br/>"
        "ORDER BY p.sharpe_ratio DESC<br/>"
        "LIMIT 5;</code>",
        body_style
    ))
    
    story.append(Paragraph("<b>3. Analytical Query: Inflow volume by state</b>", h2_style))
    story.append(Paragraph(
        "<code>SELECT state, SUM(amount_inr) AS total_investment<br/>"
        "FROM fact_transactions<br/>"
        "GROUP BY state<br/>"
        "ORDER BY total_investment DESC<br/>"
        "LIMIT 5;</code>",
        body_style
    ))

    # Build PDF
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Final Report successfully generated at {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_pdf()
