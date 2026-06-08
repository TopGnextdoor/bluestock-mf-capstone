"""
Bluestock Mutual Fund Capstone — Dashboard Generator
=====================================================
Generates 4 dashboard-page PNG images and a combined PDF report
from the bluestock_mf.db SQLite database.

Deliverables produced:
  dashboard/Page1_Industry_Overview.png
  dashboard/Page2_Fund_Performance.png
  dashboard/Page3_Investor_Analytics.png
  dashboard/Page4_SIP_Market_Trends.png
  dashboard/Dashboard.pdf
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.gridspec import GridSpec
from pathlib import Path
import textwrap

# ── Paths ─────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
DB_PATH    = BASE_DIR / "bluestock_mf.db"
OUT_DIR    = Path(__file__).resolve().parent
OUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Bluestock Theme ──────────────────────────────────────────────────────
COLORS = {
    "bg":           "#0A0E27",
    "card_bg":      "#111836",
    "accent_blue":  "#1E90FF",
    "accent_cyan":  "#00D4FF",
    "accent_green": "#00E676",
    "accent_orange":"#FF9100",
    "accent_pink":  "#FF4081",
    "accent_purple":"#BB86FC",
    "text_primary": "#FFFFFF",
    "text_secondary":"#8899AA",
    "grid":         "#1A2040",
    "kpi_border":   "#1E90FF",
}

# Palette for bar/pie charts
CHART_PALETTE = [
    "#1E90FF", "#00D4FF", "#00E676", "#FF9100",
    "#FF4081", "#BB86FC", "#FFD740", "#64FFDA",
    "#FF6E40", "#7C4DFF", "#18FFFF", "#EEFF41",
]

plt.rcParams.update({
    "figure.facecolor": COLORS["bg"],
    "axes.facecolor":   COLORS["card_bg"],
    "axes.edgecolor":   COLORS["grid"],
    "axes.labelcolor":  COLORS["text_primary"],
    "xtick.color":      COLORS["text_secondary"],
    "ytick.color":      COLORS["text_secondary"],
    "text.color":       COLORS["text_primary"],
    "grid.color":       COLORS["grid"],
    "grid.alpha":       0.4,
    "font.family":      "sans-serif",
    "font.size":        10,
})


def get_conn():
    return sqlite3.connect(str(DB_PATH))


# ══════════════════════════════════════════════════════════════════════════
# HELPER — KPI Card
# ══════════════════════════════════════════════════════════════════════════
def draw_kpi(ax, title, value, subtitle="", color=COLORS["accent_blue"]):
    """Draw a styled KPI card on an axis."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color(color)
        spine.set_linewidth(2)
    ax.set_facecolor(COLORS["card_bg"])
    ax.text(0.5, 0.72, title, ha="center", va="center",
            fontsize=10, color=COLORS["text_secondary"], fontweight="bold")
    ax.text(0.5, 0.40, value, ha="center", va="center",
            fontsize=22, color=color, fontweight="bold")
    if subtitle:
        ax.text(0.5, 0.12, subtitle, ha="center", va="center",
                fontsize=8, color=COLORS["text_secondary"])


# ══════════════════════════════════════════════════════════════════════════
# PAGE 1 — INDUSTRY OVERVIEW
# ══════════════════════════════════════════════════════════════════════════
def page1_industry_overview():
    print("Generating Page 1 — Industry Overview …")
    conn = get_conn()

    # --- Fetch data ---
    df_aum = pd.read_sql("SELECT * FROM fact_aum", conn)
    df_sip = pd.read_sql("SELECT * FROM monthly_sip_inflows", conn)
    df_folio = pd.read_sql("SELECT * FROM industry_folio_count", conn)
    df_fund = pd.read_sql("SELECT * FROM dim_fund", conn)
    conn.close()

    # KPI values
    latest_aum_date = df_aum["date"].max()
    total_aum = df_aum[df_aum["date"] == latest_aum_date]["aum_crore"].sum()
    total_aum_lakh_cr = total_aum / 100000  # convert crore to lakh crore
    latest_sip = df_sip["sip_inflow_crore"].max()
    latest_folios = df_folio["total_folios_crore"].max()
    total_schemes = df_aum[df_aum["date"] == latest_aum_date]["num_schemes"].sum()

    # Industry AUM trend
    aum_trend = df_aum.groupby("date")["aum_crore"].sum().reset_index()
    aum_trend["date"] = pd.to_datetime(aum_trend["date"])
    aum_trend = aum_trend.sort_values("date")
    aum_trend["aum_lakh_crore"] = aum_trend["aum_crore"] / 100000

    # AUM by AMC (latest date)
    aum_by_amc = df_aum[df_aum["date"] == latest_aum_date].sort_values("aum_crore", ascending=True)

    # --- Build figure ---
    fig = plt.figure(figsize=(20, 12))
    fig.suptitle("BLUESTOCK  |  Industry Overview", fontsize=20,
                 fontweight="bold", color=COLORS["accent_cyan"], y=0.97)
    gs = GridSpec(3, 4, figure=fig, hspace=0.45, wspace=0.35,
                  top=0.92, bottom=0.06, left=0.06, right=0.96)

    # KPI cards (row 0)
    kpi_data = [
        ("Total AUM", f"₹{total_aum_lakh_cr:.0f}L Cr", "Industry AUM", COLORS["accent_blue"]),
        ("SIP Inflows", f"₹{latest_sip:,.0f} Cr", "Monthly Peak", COLORS["accent_green"]),
        ("Total Folios", f"{latest_folios:.2f} Cr", "Investor Folios", COLORS["accent_orange"]),
        ("Active Schemes", f"{total_schemes:,}", "Across AMCs", COLORS["accent_pink"]),
    ]
    for i, (title, val, sub, clr) in enumerate(kpi_data):
        ax = fig.add_subplot(gs[0, i])
        draw_kpi(ax, title, val, sub, clr)

    # Line chart — AUM trend (row 1, full width)
    ax1 = fig.add_subplot(gs[1, :])
    ax1.fill_between(aum_trend["date"], aum_trend["aum_lakh_crore"],
                     alpha=0.15, color=COLORS["accent_cyan"])
    ax1.plot(aum_trend["date"], aum_trend["aum_lakh_crore"],
             color=COLORS["accent_cyan"], linewidth=2.5, marker="o", markersize=6)
    for _, row in aum_trend.iterrows():
        ax1.annotate(f"₹{row['aum_lakh_crore']:.1f}L Cr",
                     (row["date"], row["aum_lakh_crore"]),
                     textcoords="offset points", xytext=(0, 12),
                     ha="center", fontsize=8, color=COLORS["text_primary"])
    ax1.set_title("Industry AUM Trend (2022 – 2025)", fontsize=13, fontweight="bold",
                  color=COLORS["text_primary"], pad=12)
    ax1.set_ylabel("AUM (₹ Lakh Crore)")
    ax1.grid(True, alpha=0.3)

    # Bar chart — AUM by AMC (row 2, full width)
    ax2 = fig.add_subplot(gs[2, :])
    bars = ax2.barh(aum_by_amc["fund_house"], aum_by_amc["aum_crore"] / 100000,
                    color=CHART_PALETTE[:len(aum_by_amc)], edgecolor="none", height=0.6)
    for bar, val in zip(bars, aum_by_amc["aum_crore"] / 100000):
        ax2.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                 f"₹{val:.2f}L Cr", va="center", fontsize=9, color=COLORS["text_primary"])
    ax2.set_title("AUM by Fund House (Latest)", fontsize=13, fontweight="bold",
                  color=COLORS["text_primary"], pad=12)
    ax2.set_xlabel("AUM (₹ Lakh Crore)")
    ax2.grid(True, axis="x", alpha=0.3)

    fig.savefig(OUT_DIR / "Page1_Industry_Overview.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("  [OK] Page1_Industry_Overview.png saved")
    return fig


# ══════════════════════════════════════════════════════════════════════════
# PAGE 2 — FUND PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════
def page2_fund_performance():
    print("Generating Page 2 — Fund Performance …")
    conn = get_conn()

    df_perf = pd.read_sql("SELECT * FROM fact_performance", conn)
    df_fund = pd.read_sql("SELECT amfi_code, fund_house, scheme_name, category, plan FROM dim_fund", conn)
    df_aum_latest = pd.read_sql(
        "SELECT fund_house, aum_crore FROM fact_aum WHERE date = (SELECT MAX(date) FROM fact_aum)", conn)
    # NAV for a sample fund
    df_nav_sample = pd.read_sql(
        "SELECT date, nav FROM fact_nav WHERE amfi_code = (SELECT amfi_code FROM dim_fund LIMIT 1) ORDER BY date", conn)
    df_bench = pd.read_sql(
        "SELECT date, close_value FROM benchmark_indices WHERE index_name = 'NIFTY50' ORDER BY date", conn)
    conn.close()

    # Merge performance with fund info
    df = df_perf.merge(df_fund, on="amfi_code", how="left")

    # For bubble size — use fund_house AUM as proxy
    aum_map = df_aum_latest.groupby("fund_house")["aum_crore"].sum().to_dict()
    df["aum"] = df["fund_house"].map(aum_map).fillna(100000)

    # --- Build figure ---
    fig = plt.figure(figsize=(20, 12))
    fig.suptitle("BLUESTOCK  |  Fund Performance", fontsize=20,
                 fontweight="bold", color=COLORS["accent_cyan"], y=0.97)
    gs = GridSpec(2, 2, figure=fig, hspace=0.40, wspace=0.30,
                  top=0.92, bottom=0.06, left=0.06, right=0.96)

    # Scatter plot — Return vs Risk
    ax1 = fig.add_subplot(gs[0, 0])
    categories = df["category"].unique()
    cat_colors = {cat: CHART_PALETTE[i % len(CHART_PALETTE)] for i, cat in enumerate(categories)}
    for cat in categories:
        mask = df["category"] == cat
        ax1.scatter(df.loc[mask, "return_3yr_pct"],
                    df.loc[mask, "std_dev_ann_pct"],
                    s=df.loc[mask, "aum"] / 5000,
                    c=cat_colors[cat], alpha=0.7, edgecolors="white", linewidth=0.5,
                    label=cat)
    ax1.set_xlabel("3Y Return (%)")
    ax1.set_ylabel("Std Dev / Risk (%)")
    ax1.set_title("Return vs Risk (Bubble = AUM)", fontsize=12, fontweight="bold", pad=10)
    ax1.legend(fontsize=7, loc="upper left", framealpha=0.3)
    ax1.grid(True, alpha=0.3)

    # Fund Scorecard Table
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.axis("off")
    table_df = df[["scheme_name", "return_1yr_pct", "return_3yr_pct", "sharpe_ratio",
                   "morningstar_rating", "risk_grade"]].copy()
    table_df["scheme_name"] = table_df["scheme_name"].apply(lambda x: textwrap.shorten(x, width=30, placeholder="…"))
    table_df.columns = ["Scheme", "1Y Ret%", "3Y Ret%", "Sharpe", "★ Rating", "Risk"]
    table_df = table_df.sort_values("3Y Ret%", ascending=False).head(12)

    tbl = ax2.table(cellText=table_df.values,
                    colLabels=table_df.columns,
                    loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(7)
    tbl.scale(1, 1.3)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor(COLORS["grid"])
        if row == 0:
            cell.set_facecolor(COLORS["accent_blue"])
            cell.set_text_props(color="white", fontweight="bold")
        else:
            cell.set_facecolor(COLORS["card_bg"])
            cell.set_text_props(color=COLORS["text_primary"])
    ax2.set_title("Fund Scorecard (Top by 3Y Return)", fontsize=12,
                  fontweight="bold", pad=10)

    # NAV Line vs Benchmark
    ax3 = fig.add_subplot(gs[1, :])
    df_nav_sample["date"] = pd.to_datetime(df_nav_sample["date"])
    # Normalise to 100
    nav_base = df_nav_sample["nav"].iloc[0]
    df_nav_sample["nav_norm"] = df_nav_sample["nav"] / nav_base * 100

    df_bench["date"] = pd.to_datetime(df_bench["date"])
    bench_base = df_bench["close_value"].iloc[0]
    df_bench["bench_norm"] = df_bench["close_value"] / bench_base * 100

    ax3.plot(df_nav_sample["date"], df_nav_sample["nav_norm"],
             color=COLORS["accent_cyan"], linewidth=1.5, label="Fund NAV (normalised)")
    ax3.plot(df_bench["date"], df_bench["bench_norm"],
             color=COLORS["accent_orange"], linewidth=1.5, alpha=0.8, label="Nifty 50 (normalised)")
    ax3.fill_between(df_nav_sample["date"], df_nav_sample["nav_norm"],
                     100, alpha=0.08, color=COLORS["accent_cyan"])
    ax3.set_title("NAV vs Benchmark (Nifty 50) — Normalised to 100", fontsize=12,
                  fontweight="bold", pad=10)
    ax3.set_ylabel("Normalised Value")
    ax3.legend(fontsize=9, framealpha=0.3)
    ax3.grid(True, alpha=0.3)

    fig.savefig(OUT_DIR / "Page2_Fund_Performance.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("  [OK] Page2_Fund_Performance.png saved")
    return fig


# ══════════════════════════════════════════════════════════════════════════
# PAGE 3 — INVESTOR ANALYTICS
# ══════════════════════════════════════════════════════════════════════════
def page3_investor_analytics():
    print("Generating Page 3 — Investor Analytics …")
    conn = get_conn()
    df_tx = pd.read_sql("SELECT * FROM fact_transactions", conn)
    conn.close()

    df_tx["transaction_date"] = pd.to_datetime(df_tx["transaction_date"])

    # --- Build figure ---
    fig = plt.figure(figsize=(20, 12))
    fig.suptitle("BLUESTOCK  |  Investor Analytics", fontsize=20,
                 fontweight="bold", color=COLORS["accent_cyan"], y=0.97)
    gs = GridSpec(2, 2, figure=fig, hspace=0.40, wspace=0.30,
                  top=0.92, bottom=0.06, left=0.06, right=0.96)

    # Bar chart — Transaction amount by state (top 10)
    ax1 = fig.add_subplot(gs[0, 0])
    state_amt = df_tx.groupby("state")["amount_inr"].sum().sort_values(ascending=False).head(10)
    state_amt = state_amt.sort_values(ascending=True)
    bars = ax1.barh(state_amt.index, state_amt.values / 1e7,
                    color=CHART_PALETTE[:len(state_amt)], height=0.6)
    ax1.set_xlabel("Amount (₹ Crore)")
    ax1.set_title("Transaction Amount by State (Top 10)", fontsize=12, fontweight="bold", pad=10)
    ax1.grid(True, axis="x", alpha=0.3)

    # Donut — SIP / Lumpsum / Redemption split
    ax2 = fig.add_subplot(gs[0, 1])
    type_split = df_tx.groupby("transaction_type")["amount_inr"].sum()
    donut_colors = [COLORS["accent_green"], COLORS["accent_blue"], COLORS["accent_pink"]]
    wedges, texts, autotexts = ax2.pie(
        type_split.values, labels=type_split.index, autopct="%1.1f%%",
        colors=donut_colors, pctdistance=0.75, startangle=90,
        textprops={"color": COLORS["text_primary"], "fontsize": 10})
    centre_circle = plt.Circle((0, 0), 0.50, fc=COLORS["card_bg"])
    ax2.add_artist(centre_circle)
    ax2.set_title("Transaction Type Split", fontsize=12, fontweight="bold", pad=10)

    # Bar — Age group vs avg SIP amount
    ax3 = fig.add_subplot(gs[1, 0])
    sip_mask = df_tx["transaction_type"] == "SIP"
    age_sip = df_tx[sip_mask].groupby("age_group")["amount_inr"].mean()
    age_order = ["18-25", "26-35", "36-45", "46-55", "56+"]
    age_sip = age_sip.reindex(age_order)
    bars3 = ax3.bar(age_sip.index, age_sip.values, color=CHART_PALETTE[:5],
                    edgecolor="none", width=0.5)
    for bar, val in zip(bars3, age_sip.values):
        ax3.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 100,
                 f"₹{val:,.0f}", ha="center", fontsize=8, color=COLORS["text_primary"])
    ax3.set_ylabel("Avg SIP Amount (₹)")
    ax3.set_title("Avg SIP Amount by Age Group", fontsize=12, fontweight="bold", pad=10)
    ax3.grid(True, axis="y", alpha=0.3)

    # Line — Monthly transaction volume
    ax4 = fig.add_subplot(gs[1, 1])
    monthly_vol = df_tx.set_index("transaction_date").resample("ME").size()
    ax4.fill_between(monthly_vol.index, monthly_vol.values, alpha=0.15,
                     color=COLORS["accent_purple"])
    ax4.plot(monthly_vol.index, monthly_vol.values,
             color=COLORS["accent_purple"], linewidth=2)
    ax4.set_title("Monthly Transaction Volume", fontsize=12, fontweight="bold", pad=10)
    ax4.set_ylabel("Number of Transactions")
    ax4.grid(True, alpha=0.3)

    fig.savefig(OUT_DIR / "Page3_Investor_Analytics.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("  [OK] Page3_Investor_Analytics.png saved")
    return fig


# ══════════════════════════════════════════════════════════════════════════
# PAGE 4 — SIP & MARKET TRENDS
# ══════════════════════════════════════════════════════════════════════════
def page4_sip_market_trends():
    print("Generating Page 4 — SIP & Market Trends …")
    conn = get_conn()
    df_sip = pd.read_sql("SELECT * FROM monthly_sip_inflows", conn)
    df_bench = pd.read_sql(
        "SELECT date, close_value FROM benchmark_indices WHERE index_name = 'NIFTY50' ORDER BY date", conn)
    df_cat = pd.read_sql("SELECT * FROM category_inflows", conn)
    conn.close()

    df_sip["month_dt"] = pd.to_datetime(df_sip["month"] + "-01")
    df_bench["date"] = pd.to_datetime(df_bench["date"])
    # Monthly avg Nifty
    nifty_monthly = df_bench.set_index("date").resample("ME")["close_value"].mean().reset_index()

    # --- Build figure ---
    fig = plt.figure(figsize=(20, 12))
    fig.suptitle("BLUESTOCK  |  SIP & Market Trends", fontsize=20,
                 fontweight="bold", color=COLORS["accent_cyan"], y=0.97)
    gs = GridSpec(2, 2, figure=fig, hspace=0.40, wspace=0.30,
                  top=0.92, bottom=0.06, left=0.06, right=0.96)

    # Dual-axis — SIP inflow (bar) + Nifty 50 (line)
    ax1 = fig.add_subplot(gs[0, :])
    ax1.bar(df_sip["month_dt"], df_sip["sip_inflow_crore"],
            width=20, color=COLORS["accent_blue"], alpha=0.7, label="SIP Inflow (₹ Cr)")
    ax1.set_ylabel("SIP Inflow (₹ Crore)", color=COLORS["accent_blue"])
    ax1.set_title("SIP Inflows vs Nifty 50 (2022 – 2025)", fontsize=13,
                  fontweight="bold", pad=12)
    ax1.grid(True, alpha=0.3)

    ax1b = ax1.twinx()
    ax1b.plot(nifty_monthly["date"], nifty_monthly["close_value"],
              color=COLORS["accent_orange"], linewidth=2, label="Nifty 50")
    ax1b.set_ylabel("Nifty 50 Close", color=COLORS["accent_orange"])
    ax1b.tick_params(axis="y", colors=COLORS["accent_orange"])
    ax1b.spines["right"].set_color(COLORS["accent_orange"])

    # Combine legends
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax1b.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=9, framealpha=0.3, loc="upper left")

    # Category inflow heatmap
    ax2 = fig.add_subplot(gs[1, 0])
    pivot = df_cat.pivot_table(index="category", columns="month",
                               values="net_inflow_crore", aggfunc="sum")
    pivot = pivot.fillna(0)
    # Show only last 12 months for readability
    if pivot.shape[1] > 12:
        pivot = pivot.iloc[:, -12:]
    im = ax2.imshow(pivot.values, aspect="auto", cmap="YlGnBu", interpolation="nearest")
    ax2.set_yticks(range(len(pivot.index)))
    ax2.set_yticklabels(pivot.index, fontsize=7)
    ax2.set_xticks(range(len(pivot.columns)))
    ax2.set_xticklabels(pivot.columns, fontsize=6, rotation=45, ha="right")
    ax2.set_title("Category Net Inflow Heatmap (Last 12 Mo)", fontsize=12,
                  fontweight="bold", pad=10)
    plt.colorbar(im, ax=ax2, fraction=0.046, pad=0.04, label="₹ Crore")

    # Top 5 categories by net inflow FY25
    ax3 = fig.add_subplot(gs[1, 1])
    fy25 = df_cat[(df_cat["month"] >= "2024-04") & (df_cat["month"] <= "2025-03")]
    top5 = fy25.groupby("category")["net_inflow_crore"].sum().sort_values(ascending=False).head(5)
    top5 = top5.sort_values(ascending=True)
    bars = ax3.barh(top5.index, top5.values,
                    color=[COLORS["accent_cyan"], COLORS["accent_green"],
                           COLORS["accent_blue"], COLORS["accent_orange"],
                           COLORS["accent_pink"]], height=0.5)
    for bar, val in zip(bars, top5.values):
        ax3.text(bar.get_width() + 500, bar.get_y() + bar.get_height() / 2,
                 f"₹{val:,.0f} Cr", va="center", fontsize=9, color=COLORS["text_primary"])
    ax3.set_title("Top 5 Categories by Net Inflow (FY25)", fontsize=12,
                  fontweight="bold", pad=10)
    ax3.set_xlabel("Net Inflow (₹ Crore)")
    ax3.grid(True, axis="x", alpha=0.3)

    fig.savefig(OUT_DIR / "Page4_SIP_Market_Trends.png", dpi=180, bbox_inches="tight")
    plt.close(fig)
    print("  [OK] Page4_SIP_Market_Trends.png saved")
    return fig


# ══════════════════════════════════════════════════════════════════════════
# COMBINE INTO PDF
# ══════════════════════════════════════════════════════════════════════════
def combine_pdf():
    print("Combining all pages into Dashboard.pdf …")
    png_files = [
        OUT_DIR / "Page1_Industry_Overview.png",
        OUT_DIR / "Page2_Fund_Performance.png",
        OUT_DIR / "Page3_Investor_Analytics.png",
        OUT_DIR / "Page4_SIP_Market_Trends.png",
    ]
    with PdfPages(OUT_DIR / "Dashboard.pdf") as pdf:
        for png in png_files:
            fig = plt.figure(figsize=(20, 12))
            fig.patch.set_facecolor(COLORS["bg"])
            img = plt.imread(str(png))
            ax = fig.add_axes([0, 0, 1, 1])
            ax.imshow(img)
            ax.axis("off")
            pdf.savefig(fig, dpi=150)
            plt.close(fig)
    print(f"  [OK] Dashboard.pdf saved ({len(png_files)} pages)")


# ══════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  Bluestock MF Dashboard Generator")
    print("=" * 60)
    page1_industry_overview()
    page2_fund_performance()
    page3_investor_analytics()
    page4_sip_market_trends()
    combine_pdf()
    print("\n[SUCCESS] All deliverables generated in:", OUT_DIR)
    print("   - Page1_Industry_Overview.png")
    print("   - Page2_Fund_Performance.png")
    print("   - Page3_Investor_Analytics.png")
    print("   - Page4_SIP_Market_Trends.png")
    print("   - Dashboard.pdf")
