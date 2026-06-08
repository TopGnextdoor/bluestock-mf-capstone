/* ══════════════════════════════════════════════════════════════
   Bluestock MF Dashboard — Application Logic
   ══════════════════════════════════════════════════════════════ */

// ── Globals ───────────────────────────────────────────────────
let DATA = {};
let chartInstances = {};

const PALETTE = [
    '#1E90FF','#00D4FF','#00E676','#FF9100',
    '#FF4081','#BB86FC','#FFD740','#64FFDA',
    '#FF6E40','#7C4DFF','#18FFFF','#EEFF41',
];

const CHART_DEFAULTS = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
        legend: { labels: { color: '#F0F4FF', font: { family: 'Inter', size: 11 } } },
        tooltip: {
            backgroundColor: 'rgba(13,19,51,0.95)',
            titleColor: '#00D4FF',
            bodyColor: '#F0F4FF',
            borderColor: '#1E90FF',
            borderWidth: 1,
            cornerRadius: 8,
            padding: 12,
            titleFont: { family: 'Inter', weight: '700' },
            bodyFont: { family: 'Inter' },
        }
    },
    scales: {
        x: { ticks: { color: '#7889A8', font: { family: 'Inter' } }, grid: { color: '#1A224040' } },
        y: { ticks: { color: '#7889A8', font: { family: 'Inter' } }, grid: { color: '#1A224040' } },
    }
};

// ── Data Loading ──────────────────────────────────────────────
async function loadAllData() {
    const files = [
        'dim_fund','fact_aum','fact_performance','fact_nav',
        'fact_transactions','monthly_sip_inflows','category_inflows',
        'industry_folio_count','benchmark_indices'
    ];
    for (const f of files) {
        try {
            const resp = await fetch(`data/${f}.json`);
            DATA[f] = await resp.json();
        } catch(e) {
            console.warn(`Failed to load ${f}:`, e);
            DATA[f] = [];
        }
    }
}

// ── Navigation ────────────────────────────────────────────────
function initNav() {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const pageId = btn.dataset.page;
            showPage(pageId);
        });
    });
}

function showPage(pageId) {
    document.querySelectorAll('.page').forEach(p => p.classList.add('hidden'));
    document.getElementById(pageId).classList.remove('hidden');
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    const navBtn = document.querySelector(`[data-page="${pageId}"]`);
    if (navBtn) navBtn.classList.add('active');
}

// ══════════════════════════════════════════════════════════════
// PAGE 1: INDUSTRY OVERVIEW
// ══════════════════════════════════════════════════════════════
function renderPage1() {
    const aum = DATA.fact_aum;
    const sip = DATA.monthly_sip_inflows;
    const folio = DATA.industry_folio_count;

    // KPIs
    const latestDate = aum.reduce((max, r) => r.date > max ? r.date : max, '');
    const totalAumCr = aum.filter(r => r.date === latestDate).reduce((s, r) => s + r.aum_crore, 0);
    const totalAumLCr = totalAumCr / 100000;
    const maxSip = Math.max(...sip.map(r => r.sip_inflow_crore));
    const maxFolio = Math.max(...folio.map(r => r.total_folios_crore));
    const totalSchemes = aum.filter(r => r.date === latestDate).reduce((s, r) => s + (r.num_schemes || 0), 0);

    document.getElementById('kpi-aum-value').textContent = `₹${Math.round(totalAumLCr)}L Cr`;
    document.getElementById('kpi-sip-value').textContent = `₹${maxSip.toLocaleString()} Cr`;
    document.getElementById('kpi-folio-value').textContent = `${maxFolio.toFixed(2)} Cr`;
    document.getElementById('kpi-schemes-value').textContent = totalSchemes.toLocaleString();

    // AUM Trend line chart
    const aumByDate = {};
    aum.forEach(r => { aumByDate[r.date] = (aumByDate[r.date] || 0) + r.aum_crore; });
    const dates = Object.keys(aumByDate).sort();
    const aumVals = dates.map(d => aumByDate[d] / 100000);

    destroyChart('chart-aum-trend');
    const ctx1 = document.getElementById('chart-aum-trend').getContext('2d');
    document.getElementById('chart-aum-trend').parentElement.style.height = '320px';
    chartInstances['chart-aum-trend'] = new Chart(ctx1, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Industry AUM (₹ Lakh Cr)',
                data: aumVals,
                borderColor: '#00D4FF',
                backgroundColor: 'rgba(0,212,255,0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 6,
                pointBackgroundColor: '#00D4FF',
                pointBorderColor: '#111836',
                pointBorderWidth: 2,
                borderWidth: 3,
            }]
        },
        options: {
            ...CHART_DEFAULTS,
            plugins: {
                ...CHART_DEFAULTS.plugins,
                datalabels: {
                    color: '#F0F4FF',
                    anchor: 'end',
                    align: 'top',
                    font: { weight: '700', size: 11, family: 'Inter' },
                    formatter: v => `₹${v.toFixed(1)}L Cr`
                }
            }
        },
        plugins: [ChartDataLabels]
    });

    // AUM by AMC bar chart
    const amcData = aum.filter(r => r.date === latestDate).sort((a, b) => b.aum_crore - a.aum_crore);
    destroyChart('chart-aum-amc');
    const ctx2 = document.getElementById('chart-aum-amc').getContext('2d');
    document.getElementById('chart-aum-amc').parentElement.style.height = '360px';
    chartInstances['chart-aum-amc'] = new Chart(ctx2, {
        type: 'bar',
        data: {
            labels: amcData.map(r => r.fund_house),
            datasets: [{
                label: 'AUM (₹ Lakh Cr)',
                data: amcData.map(r => r.aum_crore / 100000),
                backgroundColor: PALETTE.slice(0, amcData.length),
                borderRadius: 6,
                borderSkipped: false,
            }]
        },
        options: {
            ...CHART_DEFAULTS,
            indexAxis: 'y',
            plugins: {
                ...CHART_DEFAULTS.plugins,
                legend: { display: false },
                datalabels: {
                    color: '#F0F4FF',
                    anchor: 'end',
                    align: 'right',
                    font: { weight: '600', size: 11, family: 'Inter' },
                    formatter: v => `₹${v.toFixed(2)}L Cr`
                }
            },
            scales: {
                x: { ...CHART_DEFAULTS.scales.x, title: { display: true, text: 'AUM (₹ Lakh Crore)', color: '#7889A8' } },
                y: { ...CHART_DEFAULTS.scales.y }
            }
        },
        plugins: [ChartDataLabels]
    });
}

// ══════════════════════════════════════════════════════════════
// PAGE 2: FUND PERFORMANCE
// ══════════════════════════════════════════════════════════════
function renderPage2() {
    const perf = DATA.fact_performance;
    const funds = DATA.dim_fund;
    const nav = DATA.fact_nav;
    const bench = DATA.benchmark_indices;

    // Populate slicers
    populateSelect('slicer-fundhouse', [...new Set(perf.map(r => r.fund_house))].sort());
    populateSelect('slicer-category', [...new Set(perf.map(r => r.category))].sort());
    populateSelect('slicer-plan', [...new Set(perf.map(r => r.plan).filter(Boolean))].sort());

    // Populate NAV fund selector
    const navSelect = document.getElementById('nav-fund-select');
    navSelect.innerHTML = '';
    const uniqueFunds = [...new Set(nav.map(r => r.amfi_code))];
    uniqueFunds.forEach(code => {
        const name = nav.find(r => r.amfi_code === code)?.scheme_name || code;
        const opt = document.createElement('option');
        opt.value = code;
        opt.textContent = name.substring(0, 60);
        navSelect.appendChild(opt);
    });

    // Attach slicer listeners
    ['slicer-fundhouse','slicer-category','slicer-plan'].forEach(id => {
        document.getElementById(id).addEventListener('change', () => updatePage2Charts());
    });
    navSelect.addEventListener('change', () => updateNavBenchChart());

    updatePage2Charts();
    updateNavBenchChart();
}

function getFilteredPerf() {
    let data = DATA.fact_performance;
    const fh = document.getElementById('slicer-fundhouse').value;
    const cat = document.getElementById('slicer-category').value;
    const plan = document.getElementById('slicer-plan').value;
    if (fh !== 'All') data = data.filter(r => r.fund_house === fh);
    if (cat !== 'All') data = data.filter(r => r.category === cat);
    if (plan !== 'All') data = data.filter(r => r.plan === plan);
    return data;
}

function updatePage2Charts() {
    const data = getFilteredPerf();
    renderScatterChart(data);
    renderScorecardTable(data);
}

function renderScatterChart(data) {
    const categories = [...new Set(data.map(r => r.category))];
    const catColors = {};
    categories.forEach((c, i) => catColors[c] = PALETTE[i % PALETTE.length]);

    const datasets = categories.map(cat => ({
        label: cat,
        data: data.filter(r => r.category === cat).map(r => ({
            x: r.return_3yr_pct,
            y: r.std_dev_ann_pct,
            r: Math.max(5, Math.sqrt((r.aum || 10000) / 500)),
            _raw: r
        })),
        backgroundColor: catColors[cat] + '99',
        borderColor: catColors[cat],
        borderWidth: 1,
    }));

    destroyChart('chart-scatter');
    const ctx = document.getElementById('chart-scatter').getContext('2d');
    document.getElementById('chart-scatter').parentElement.style.height = '380px';
    chartInstances['chart-scatter'] = new Chart(ctx, {
        type: 'bubble',
        data: { datasets },
        options: {
            ...CHART_DEFAULTS,
            plugins: {
                ...CHART_DEFAULTS.plugins,
                datalabels: { display: false },
                tooltip: {
                    ...CHART_DEFAULTS.plugins.tooltip,
                    callbacks: {
                        title: items => items[0]?.raw?._raw?.scheme_name?.substring(0, 50) || '',
                        label: item => {
                            const r = item.raw._raw;
                            return [
                                `3Y Return: ${r.return_3yr_pct}%`,
                                `Std Dev: ${r.std_dev_ann_pct}%`,
                                `Sharpe: ${r.sharpe_ratio}`,
                                `Rating: ${'★'.repeat(r.morningstar_rating || 0)}`
                            ];
                        }
                    }
                }
            },
            scales: {
                x: { ...CHART_DEFAULTS.scales.x, title: { display: true, text: '3Y Return (%)', color: '#7889A8' } },
                y: { ...CHART_DEFAULTS.scales.y, title: { display: true, text: 'Std Dev / Risk (%)', color: '#7889A8' } }
            }
        }
    });
}

function renderScorecardTable(data) {
    const wrap = document.getElementById('scorecard-table-wrap');
    const sorted = [...data].sort((a, b) => b.return_3yr_pct - a.return_3yr_pct);

    let html = `<table class="scorecard-table" id="scorecard-table">
        <thead><tr>
            <th data-col="scheme_name">Scheme ▼</th>
            <th data-col="return_1yr_pct">1Y Ret%</th>
            <th data-col="return_3yr_pct">3Y Ret%</th>
            <th data-col="sharpe_ratio">Sharpe</th>
            <th data-col="morningstar_rating">★ Rating</th>
            <th data-col="risk_grade">Risk</th>
        </tr></thead><tbody>`;

    sorted.forEach(r => {
        html += `<tr data-amfi="${r.amfi_code}" class="drill-row">
            <td title="${r.scheme_name}">${r.scheme_name?.substring(0, 35) || '—'}${r.scheme_name?.length > 35 ? '…' : ''}</td>
            <td style="color:${r.return_1yr_pct >= 0 ? '#00E676' : '#FF4081'}">${r.return_1yr_pct?.toFixed(1)}%</td>
            <td style="color:${r.return_3yr_pct >= 0 ? '#00E676' : '#FF4081'}">${r.return_3yr_pct?.toFixed(1)}%</td>
            <td>${r.sharpe_ratio?.toFixed(2)}</td>
            <td>${'★'.repeat(r.morningstar_rating || 0)}</td>
            <td>${r.risk_grade || '—'}</td>
        </tr>`;
    });
    html += '</tbody></table>';
    wrap.innerHTML = html;

    // Sort on header click
    document.querySelectorAll('#scorecard-table th').forEach(th => {
        th.addEventListener('click', () => {
            const col = th.dataset.col;
            const rows = [...data];
            const isNumeric = ['return_1yr_pct','return_3yr_pct','sharpe_ratio','morningstar_rating'].includes(col);
            rows.sort((a, b) => isNumeric ? (b[col] || 0) - (a[col] || 0) : String(a[col] || '').localeCompare(String(b[col] || '')));
            renderScorecardTable(rows);
        });
    });

    // Drill-through on row click
    document.querySelectorAll('.drill-row').forEach(row => {
        row.addEventListener('click', () => {
            const amfi = parseInt(row.dataset.amfi);
            openDrillThrough(amfi);
        });
    });
}

function updateNavBenchChart() {
    const selectedCode = parseInt(document.getElementById('nav-fund-select').value);
    const navData = DATA.fact_nav.filter(r => r.amfi_code === selectedCode).sort((a, b) => a.date.localeCompare(b.date));
    const benchData = DATA.benchmark_indices.filter(r => r.index_name === 'NIFTY50').sort((a, b) => a.date.localeCompare(b.date));

    if (!navData.length) return;

    // Aggregate daily NAV to monthly averages (YYYY-MM)
    const navMonthly = {};
    navData.forEach(r => {
        const m = r.date.substring(0, 7); // "YYYY-MM"
        if (!navMonthly[m]) navMonthly[m] = { sum: 0, count: 0 };
        navMonthly[m].sum += r.nav;
        navMonthly[m].count += 1;
    });

    // Build benchmark lookup by month
    const benchMonthly = {};
    benchData.forEach(r => {
        benchMonthly[r.date.substring(0, 7)] = r.close_value;
    });

    // Create union of all months, sorted
    const allMonths = [...new Set([...Object.keys(navMonthly), ...Object.keys(benchMonthly)])].sort();

    // Compute normalised values
    const navValues = allMonths.map(m => navMonthly[m] ? navMonthly[m].sum / navMonthly[m].count : null);
    const benchValues = allMonths.map(m => benchMonthly[m] ?? null);

    const navBase = navValues.find(v => v !== null) || 1;
    const benchBase = benchValues.find(v => v !== null) || 1;

    const navNorm = navValues.map(v => v !== null ? parseFloat((v / navBase * 100).toFixed(2)) : null);
    const benchNorm = benchValues.map(v => v !== null ? parseFloat((v / benchBase * 100).toFixed(2)) : null);

    destroyChart('chart-nav-bench');
    const ctx = document.getElementById('chart-nav-bench').getContext('2d');
    document.getElementById('chart-nav-bench').parentElement.style.height = '340px';
    chartInstances['chart-nav-bench'] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: allMonths,
            datasets: [
                {
                    label: 'Fund NAV (normalised)',
                    data: navNorm,
                    borderColor: '#00D4FF',
                    backgroundColor: 'rgba(0,212,255,0.08)',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 2,
                    pointHoverRadius: 5,
                    borderWidth: 2.5,
                    spanGaps: true,
                },
                {
                    label: 'Nifty 50 (normalised)',
                    data: benchNorm,
                    borderColor: '#FF9100',
                    backgroundColor: 'rgba(255,145,0,0.05)',
                    fill: false,
                    tension: 0.3,
                    pointRadius: 2,
                    pointHoverRadius: 5,
                    borderWidth: 2.5,
                    borderDash: [6, 3],
                    spanGaps: true,
                }
            ]
        },
        options: {
            ...CHART_DEFAULTS,
            plugins: { ...CHART_DEFAULTS.plugins, datalabels: { display: false } },
            scales: {
                x: { ...CHART_DEFAULTS.scales.x, ticks: { maxTicksLimit: 12 } },
                y: { ...CHART_DEFAULTS.scales.y, title: { display: true, text: 'Normalised Value (Base=100)', color: '#7889A8' } }
            }
        }
    });
}

// ══════════════════════════════════════════════════════════════
// PAGE 3: INVESTOR ANALYTICS
// ══════════════════════════════════════════════════════════════
function renderPage3() {
    const tx = DATA.fact_transactions;

    // Populate slicers
    populateSelect('slicer-state', [...new Set(tx.map(r => r.state).filter(Boolean))].sort());
    populateSelect('slicer-agegroup', ['18-25','26-35','36-45','46-55','56+']);
    populateSelect('slicer-citytier', [...new Set(tx.map(r => r.city_tier).filter(Boolean))].sort());

    ['slicer-state','slicer-agegroup','slicer-citytier'].forEach(id => {
        document.getElementById(id).addEventListener('change', () => updatePage3Charts());
    });

    updatePage3Charts();
}

function getFilteredTx() {
    let data = DATA.fact_transactions;
    const state = document.getElementById('slicer-state').value;
    const age = document.getElementById('slicer-agegroup').value;
    const tier = document.getElementById('slicer-citytier').value;
    if (state !== 'All') data = data.filter(r => r.state === state);
    if (age !== 'All') data = data.filter(r => r.age_group === age);
    if (tier !== 'All') data = data.filter(r => r.city_tier === tier);
    return data;
}

function updatePage3Charts() {
    const data = getFilteredTx();

    // 1. Bar chart — Transaction amount by state (top 10)
    const stateAmt = {};
    data.forEach(r => { stateAmt[r.state] = (stateAmt[r.state] || 0) + r.amount_inr; });
    const topStates = Object.entries(stateAmt).sort((a, b) => b[1] - a[1]).slice(0, 10);

    destroyChart('chart-state');
    const ctx1 = document.getElementById('chart-state').getContext('2d');
    document.getElementById('chart-state').parentElement.style.height = '360px';
    chartInstances['chart-state'] = new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: topStates.map(s => s[0]),
            datasets: [{
                label: 'Amount (₹ Cr)',
                data: topStates.map(s => s[1] / 1e7),
                backgroundColor: PALETTE.slice(0, topStates.length),
                borderRadius: 6,
            }]
        },
        options: {
            ...CHART_DEFAULTS,
            indexAxis: 'y',
            plugins: { ...CHART_DEFAULTS.plugins, legend: { display: false }, datalabels: { display: false } },
            scales: {
                x: { ...CHART_DEFAULTS.scales.x, title: { display: true, text: 'Amount (₹ Crore)', color: '#7889A8' } },
                y: { ...CHART_DEFAULTS.scales.y }
            }
        }
    });

    // 2. Donut — SIP/Lumpsum/Redemption
    const typeSplit = {};
    data.forEach(r => { typeSplit[r.transaction_type] = (typeSplit[r.transaction_type] || 0) + r.amount_inr; });

    destroyChart('chart-donut');
    const ctx2 = document.getElementById('chart-donut').getContext('2d');
    document.getElementById('chart-donut').parentElement.style.height = '360px';
    chartInstances['chart-donut'] = new Chart(ctx2, {
        type: 'doughnut',
        data: {
            labels: Object.keys(typeSplit),
            datasets: [{
                data: Object.values(typeSplit),
                backgroundColor: ['#00E676', '#1E90FF', '#FF4081'],
                borderColor: '#111836',
                borderWidth: 3,
                hoverOffset: 10,
            }]
        },
        options: {
            ...CHART_DEFAULTS,
            cutout: '55%',
            scales: {},
            plugins: {
                ...CHART_DEFAULTS.plugins,
                datalabels: {
                    color: '#F0F4FF',
                    font: { weight: '700', size: 12, family: 'Inter' },
                    formatter: (val, ctx) => {
                        const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                        return (val / total * 100).toFixed(1) + '%';
                    }
                }
            }
        },
        plugins: [ChartDataLabels]
    });

    // 3. Bar — Age group vs avg SIP
    const ageOrder = ['18-25','26-35','36-45','46-55','56+'];
    const sipData = data.filter(r => r.transaction_type === 'SIP');
    const ageSip = {};
    const ageCnt = {};
    sipData.forEach(r => {
        ageSip[r.age_group] = (ageSip[r.age_group] || 0) + r.amount_inr;
        ageCnt[r.age_group] = (ageCnt[r.age_group] || 0) + 1;
    });
    const ageAvg = ageOrder.map(a => ageCnt[a] ? ageSip[a] / ageCnt[a] : 0);

    destroyChart('chart-age-sip');
    const ctx3 = document.getElementById('chart-age-sip').getContext('2d');
    document.getElementById('chart-age-sip').parentElement.style.height = '360px';
    chartInstances['chart-age-sip'] = new Chart(ctx3, {
        type: 'bar',
        data: {
            labels: ageOrder,
            datasets: [{
                label: 'Avg SIP Amount (₹)',
                data: ageAvg,
                backgroundColor: PALETTE.slice(0, 5),
                borderRadius: 8,
            }]
        },
        options: {
            ...CHART_DEFAULTS,
            plugins: {
                ...CHART_DEFAULTS.plugins,
                legend: { display: false },
                datalabels: {
                    color: '#F0F4FF',
                    anchor: 'end',
                    align: 'top',
                    font: { weight: '700', size: 11, family: 'Inter' },
                    formatter: v => `₹${Math.round(v).toLocaleString()}`
                }
            },
            scales: {
                x: { ...CHART_DEFAULTS.scales.x },
                y: { ...CHART_DEFAULTS.scales.y, title: { display: true, text: 'Avg SIP Amount (₹)', color: '#7889A8' } }
            }
        },
        plugins: [ChartDataLabels]
    });

    // 4. Line — Monthly transaction volume
    const monthlyVol = {};
    data.forEach(r => {
        const m = r.transaction_date?.substring(0, 7);
        if (m) monthlyVol[m] = (monthlyVol[m] || 0) + 1;
    });
    const months = Object.keys(monthlyVol).sort();

    destroyChart('chart-monthly-vol');
    const ctx4 = document.getElementById('chart-monthly-vol').getContext('2d');
    document.getElementById('chart-monthly-vol').parentElement.style.height = '360px';
    chartInstances['chart-monthly-vol'] = new Chart(ctx4, {
        type: 'line',
        data: {
            labels: months,
            datasets: [{
                label: 'Transactions',
                data: months.map(m => monthlyVol[m]),
                borderColor: '#BB86FC',
                backgroundColor: 'rgba(187,134,252,0.1)',
                fill: true,
                tension: 0.4,
                pointRadius: 3,
                borderWidth: 2,
            }]
        },
        options: {
            ...CHART_DEFAULTS,
            plugins: { ...CHART_DEFAULTS.plugins, datalabels: { display: false } },
            scales: {
                x: { ...CHART_DEFAULTS.scales.x, ticks: { maxTicksLimit: 12 } },
                y: { ...CHART_DEFAULTS.scales.y, title: { display: true, text: 'Number of Transactions', color: '#7889A8' } }
            }
        }
    });
}

// ══════════════════════════════════════════════════════════════
// PAGE 4: SIP & MARKET TRENDS
// ══════════════════════════════════════════════════════════════
function renderPage4() {
    const sip = DATA.monthly_sip_inflows;
    const bench = DATA.benchmark_indices;
    const catInflow = DATA.category_inflows;

    // 1. Dual-axis: SIP (bar) + Nifty (line)
    const sipMonths = sip.map(r => r.month).sort();
    const sipVals = sipMonths.map(m => sip.find(r => r.month === m)?.sip_inflow_crore || 0);

    // Monthly average Nifty
    const niftyByMonth = {};
    const niftyCnt = {};
    bench.filter(r => r.index_name === 'NIFTY50').forEach(r => {
        const m = r.date.substring(0, 7);
        niftyByMonth[m] = (niftyByMonth[m] || 0) + r.close_value;
        niftyCnt[m] = (niftyCnt[m] || 0) + 1;
    });
    const niftyMonths = Object.keys(niftyByMonth).sort();
    const niftyAvg = niftyMonths.map(m => niftyByMonth[m] / niftyCnt[m]);

    destroyChart('chart-sip-nifty');
    const ctx1 = document.getElementById('chart-sip-nifty').getContext('2d');
    document.getElementById('chart-sip-nifty').parentElement.style.height = '360px';
    chartInstances['chart-sip-nifty'] = new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: sipMonths,
            datasets: [
                {
                    type: 'bar',
                    label: 'SIP Inflow (₹ Cr)',
                    data: sipVals,
                    backgroundColor: '#1E90FF99',
                    borderRadius: 4,
                    yAxisID: 'y',
                    order: 2,
                },
                {
                    type: 'line',
                    label: 'Nifty 50',
                    data: sipMonths.map(m => {
                        return niftyByMonth[m] ? (niftyByMonth[m] / niftyCnt[m]) : null;
                    }),
                    borderColor: '#FF9100',
                    backgroundColor: 'transparent',
                    tension: 0.4,
                    pointRadius: 2,
                    borderWidth: 2.5,
                    yAxisID: 'y1',
                    order: 1,
                }
            ]
        },
        options: {
            ...CHART_DEFAULTS,
            plugins: { ...CHART_DEFAULTS.plugins, datalabels: { display: false } },
            scales: {
                x: { ...CHART_DEFAULTS.scales.x, ticks: { maxTicksLimit: 16 } },
                y: {
                    ...CHART_DEFAULTS.scales.y,
                    position: 'left',
                    title: { display: true, text: 'SIP Inflow (₹ Crore)', color: '#1E90FF' },
                    ticks: { color: '#1E90FF' }
                },
                y1: {
                    position: 'right',
                    title: { display: true, text: 'Nifty 50 Close', color: '#FF9100' },
                    ticks: { color: '#FF9100' },
                    grid: { drawOnChartArea: false }
                }
            }
        }
    });

    // 2. Category heatmap
    renderHeatmap(catInflow);

    // 3. Top 5 categories FY25
    const fy25 = catInflow.filter(r => r.month >= '2024-04' && r.month <= '2025-03');
    const catTotals = {};
    fy25.forEach(r => { catTotals[r.category] = (catTotals[r.category] || 0) + r.net_inflow_crore; });
    const top5 = Object.entries(catTotals).sort((a, b) => b[1] - a[1]).slice(0, 5);

    destroyChart('chart-top5');
    const ctx3 = document.getElementById('chart-top5').getContext('2d');
    document.getElementById('chart-top5').parentElement.style.height = '360px';
    chartInstances['chart-top5'] = new Chart(ctx3, {
        type: 'bar',
        data: {
            labels: top5.map(t => t[0]),
            datasets: [{
                label: 'Net Inflow (₹ Cr)',
                data: top5.map(t => t[1]),
                backgroundColor: ['#00D4FF', '#FF9100', '#1E90FF', '#00E676', '#BB86FC'],
                borderRadius: 8,
            }]
        },
        options: {
            ...CHART_DEFAULTS,
            indexAxis: 'y',
            plugins: {
                ...CHART_DEFAULTS.plugins,
                legend: { display: false },
                datalabels: {
                    color: '#F0F4FF',
                    anchor: 'end',
                    align: 'right',
                    font: { weight: '700', size: 11, family: 'Inter' },
                    formatter: v => `₹${v.toLocaleString()} Cr`
                }
            },
            scales: {
                x: { ...CHART_DEFAULTS.scales.x, title: { display: true, text: 'Net Inflow (₹ Crore)', color: '#7889A8' } },
                y: { ...CHART_DEFAULTS.scales.y }
            }
        },
        plugins: [ChartDataLabels]
    });
}

function renderHeatmap(catInflow) {
    const container = document.getElementById('heatmap-container');
    const months = [...new Set(catInflow.map(r => r.month))].sort();
    const categories = [...new Set(catInflow.map(r => r.category))].sort();
    const last12 = months.slice(-12);

    // Build pivot
    const pivot = {};
    categories.forEach(cat => {
        pivot[cat] = {};
        last12.forEach(m => { pivot[cat][m] = 0; });
    });
    catInflow.filter(r => last12.includes(r.month)).forEach(r => {
        if (pivot[r.category]) pivot[r.category][r.month] = r.net_inflow_crore;
    });

    // Find min/max for color scale
    let allVals = [];
    Object.values(pivot).forEach(row => Object.values(row).forEach(v => allVals.push(v)));
    const minV = Math.min(...allVals);
    const maxV = Math.max(...allVals);

    let html = '<table class="heatmap-table"><thead><tr><th>Category</th>';
    last12.forEach(m => { html += `<th>${m}</th>`; });
    html += '</tr></thead><tbody>';

    categories.forEach(cat => {
        html += `<tr><td>${cat}</td>`;
        last12.forEach(m => {
            const val = pivot[cat][m] || 0;
            const color = heatmapColor(val, minV, maxV);
            const textColor = val > (maxV * 0.6) ? '#000' : '#F0F4FF';
            html += `<td style="background:${color};color:${textColor}" title="${cat}: ₹${val.toLocaleString()} Cr (${m})">${val > 0 ? Math.round(val) : '—'}</td>`;
        });
        html += '</tr>';
    });
    html += '</tbody></table>';
    container.innerHTML = html;
}

function heatmapColor(val, min, max) {
    if (max === min) return '#1A2248';
    const ratio = (val - min) / (max - min);
    // Gradient from dark blue to cyan to green to yellow
    if (ratio < 0.25) {
        const t = ratio / 0.25;
        return lerpColor('#0D1333', '#1565C0', t);
    } else if (ratio < 0.5) {
        const t = (ratio - 0.25) / 0.25;
        return lerpColor('#1565C0', '#00ACC1', t);
    } else if (ratio < 0.75) {
        const t = (ratio - 0.5) / 0.25;
        return lerpColor('#00ACC1', '#66BB6A', t);
    } else {
        const t = (ratio - 0.75) / 0.25;
        return lerpColor('#66BB6A', '#FFD740', t);
    }
}

function lerpColor(a, b, t) {
    const ar = parseInt(a.slice(1,3),16), ag = parseInt(a.slice(3,5),16), ab = parseInt(a.slice(5,7),16);
    const br = parseInt(b.slice(1,3),16), bg = parseInt(b.slice(3,5),16), bb = parseInt(b.slice(5,7),16);
    const r = Math.round(ar + (br-ar)*t).toString(16).padStart(2,'0');
    const g = Math.round(ag + (bg-ag)*t).toString(16).padStart(2,'0');
    const bl = Math.round(ab + (bb-ab)*t).toString(16).padStart(2,'0');
    return `#${r}${g}${bl}`;
}

// ══════════════════════════════════════════════════════════════
// DRILL-THROUGH: NAV DETAIL
// ══════════════════════════════════════════════════════════════
function openDrillThrough(amfiCode) {
    const fund = DATA.dim_fund.find(f => f.amfi_code === amfiCode);
    const perf = DATA.fact_performance.find(p => p.amfi_code === amfiCode);
    const navData = DATA.fact_nav.filter(r => r.amfi_code === amfiCode).sort((a, b) => a.date.localeCompare(b.date));

    if (!fund || !navData.length) return;

    showPage('page-drill');
    // Hide nav highlight
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));

    document.getElementById('drill-title').textContent = fund.scheme_name;
    document.getElementById('drill-subtitle').textContent = `${fund.fund_house} | ${fund.category} | ${fund.plan || ''}`;

    // Info cards
    const infoRow = document.getElementById('drill-info-row');
    const infoItems = [
        ['Fund House', fund.fund_house],
        ['Category', fund.category],
        ['Sub-Category', fund.sub_category],
        ['Risk', fund.risk_category || perf?.risk_grade || '—'],
        ['1Y Return', `${perf?.return_1yr_pct?.toFixed(1) || '—'}%`],
        ['3Y Return', `${perf?.return_3yr_pct?.toFixed(1) || '—'}%`],
        ['Sharpe Ratio', perf?.sharpe_ratio?.toFixed(2) || '—'],
        ['★ Rating', '★'.repeat(perf?.morningstar_rating || 0) || '—'],
    ];
    infoRow.innerHTML = infoItems.map(([l, v]) =>
        `<div class="drill-info-item"><div class="drill-info-label">${l}</div><div class="drill-info-value">${v}</div></div>`
    ).join('');

    // NAV chart
    destroyChart('chart-drill-nav');
    const ctx = document.getElementById('chart-drill-nav').getContext('2d');
    document.getElementById('chart-drill-nav').parentElement.style.height = '400px';
    chartInstances['chart-drill-nav'] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: navData.map(r => r.date),
            datasets: [{
                label: 'NAV (₹)',
                data: navData.map(r => r.nav),
                borderColor: '#00D4FF',
                backgroundColor: 'rgba(0,212,255,0.08)',
                fill: true,
                tension: 0.3,
                pointRadius: 0,
                borderWidth: 2,
            }]
        },
        options: {
            ...CHART_DEFAULTS,
            plugins: { ...CHART_DEFAULTS.plugins, datalabels: { display: false } },
            scales: {
                x: { ...CHART_DEFAULTS.scales.x, ticks: { maxTicksLimit: 15 } },
                y: { ...CHART_DEFAULTS.scales.y, title: { display: true, text: 'NAV (₹)', color: '#7889A8' } }
            }
        }
    });
}

document.getElementById('drill-back-btn')?.addEventListener('click', () => showPage('page2'));

// ══════════════════════════════════════════════════════════════
// UTILITIES
// ══════════════════════════════════════════════════════════════
function populateSelect(id, values) {
    const sel = document.getElementById(id);
    const current = sel.value;
    sel.innerHTML = '<option value="All">All</option>';
    values.forEach(v => {
        const opt = document.createElement('option');
        opt.value = v;
        opt.textContent = v;
        sel.appendChild(opt);
    });
    if (values.includes(current)) sel.value = current;
}

function destroyChart(id) {
    if (chartInstances[id]) {
        chartInstances[id].destroy();
        delete chartInstances[id];
    }
}

// ── Initialise ────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
    await loadAllData();
    initNav();
    renderPage1();
    renderPage2();
    renderPage3();
    renderPage4();
});
