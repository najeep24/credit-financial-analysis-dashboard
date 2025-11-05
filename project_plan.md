# Project Plan — Streamlit Dashboard for Credit Analysis Copilot

**Tujuan:**  
Menyediakan blueprint yang jelas, terstruktur, dan tidak ambigu agar _Claude Code_ dapat langsung membangun prototype **Streamlit dashboard** yang menampilkan hasil analitik kredit (input: hasil preprocessing yang sudah selesai). Dashboard ini berfungsi sebagai _copilot_ untuk credit analyst: cepat, explainable, dan actionable.

---

## 1. Data Contract (Input files)

Semua file diharapkan berbentuk CSV dan diunggah user. Nama file dan struktur kolom wajib sesuai berikut:(data ada di folder D:\Project\portfolio\coba_streamlit(this project)\data)

### 1.1 `df_credit_score.csv` (singkat: df_credit_score)

- **Rows**: per `firm_id` (biasanya 1 per upload) - but dashboard should support multiple firms too.
- **Expected columns (34)** — wajib hadir persis (case-sensitive):

```
firm_id,
liquidity_score, liquidity_reason, liquidity_status,
solvency_score, solvency_reason, solvency_status,
profitability_score, profitability_reason, profitability_status,
activity_score, activity_reason, activity_status,
coverage_score, coverage_reason, coverage_status,
cashflow_score, cashflow_reason, cashflow_status,
structure_score, structure_reason, structure_status,
final_score, kategori, rekomendasi,
reasoning,
liquidity_analysis, solvency_analysis, profitability_analysis,
activity_analysis, coverage_analysis, cashflow_analysis, structure_analysis,
genai_recommendation
```

- **Datatype hints:** `*_score` = numeric (0-100 float). `*_status` = categorical (e.g. "Strong"/"Weak"/"Watch"). `*_reason` and `*_analysis` are strings (long text). `final_score` numeric.

### 1.2 `df_agg.csv` (aggregated features)

- 1 row per `firm_id` with multi-year aggregated features: columns named like `{ratio}_mean`, `{ratio}_std`, `{ratio}_trend` (e.g. `roa_mean`, `roa_std`, `roa_trend`). There are ~235 columns.
- Dashboard must not rely on exact ordering — rely on prefix/suffix patterns (`_mean`, `_std`, `_trend`).

### 1.3 `df_ratios.csv` (yearly ratios)

- Multi-year dataset: columns include `firm_id`, `year`, and many `bs_*`, `ii_*`, `cf_*` plus computed ratios such as `current_ratio`, `roa`, `days_inventory`, `ocf_ratio`, `fund_flow_balance`, dscr etc. ~81 columns.
- `year` must be integer and sortable.

### 1.4 `company_info_sub.csv`, `balance_sheet_sub.csv`, `income_info_sub.csv`, `cash_flow_sub.csv`

- Raw statements per year for drilldown. `balance_sheet_sub`, `income_info_sub`, `cash_flow_sub` are multi-year and should contain `firm_id` + `year` + relevant numeric fields.

**Validation:** On upload, dashboard should validate presence and minimal data (e.g. `firm_id`, `final_score`, at least one year in `df_ratios`) and display user-friendly error messages listing missing columns.

---

## 2. High-level UI / Navigation (Streamlit)

Buat dashboard dengan layout dan pages/tabs berikut (left sidebar navigation recommended):

1. **Analysis Summary** (Default landing page)
2. **Performance Insight Deck** (Deep-dive per-aspect aggregated view)
3. **Sub-Ratio Explorer** (Detailed ratio panels, per ratio time series and stats)
4. **Financial Statements** (Raw statements presented as tidy tables with trend badges)
5. **Settings / Export** (Export CSV / PDF / Download narratives)

Semua halaman harus memiliki `firm_id` selector (dropdown) di header untuk berpindah antar perusahaan jika file berisi banyak firm.

---

## 3. Analysis Summary (Detail UI spec)

**Tujuan page:** memberi credit analyst gambaran cepat dan actionable: final_score, kategori, rekomendasi, explanation, plus visual diagnosis (radar + bars).

### 3.1 Top summary box (left column)

- Show **Final Score** (besar, prominent) — `df_credit_score['final_score']`.
- Show **Kategori** — `df_credit_score['kategori']`.
- Show **Recommendation** — `df_credit_score['rekomendasi']`.
- Under these, show **`reasoning`** (full text) for explainability. Allow collapse/expand.
- Under that, show **`genai_recommendation`** (if present) in clearly styled box.

### 3.2 Right column: Radar Chart

- Radar with 7 axes: `liquidity_score`, `solvency_score`, `profitability_score`, `activity_score`, `coverage_score`, `cashflow_score`, `structure_score`.
- Scale for each axis: 0..100. Fill area with semi-transparent color. Add markers and axis labels. Provide hover tooltips with exact numeric value and `*_status`.
- Add small legend: color mapping.

### 3.3 Middle: Combined Bar Chart (importance-weighted)

- Horizontal bar chart showing the 7 aspect scores (values 0..100). Bars colored by corresponding `*_status` (e.g. `Strong`=green, `Watch`=yellow, `Weak`=red). Exact color palette must be configurable.
- Display aspect **weight** (as label next to bar) using the weights defined in code: liquidity=0.15, solvency=0.15, profitability=0.20, activity=0.10, coverage=0.10, cashflow=0.15, structure=0.15. Show weight percentage (e.g. `15%`) and absolute contribution to final_score next to each bar (e.g. `liquidity: score 80 * 0.15 -> 12.0`).
- Bars should be **sorted** by contribution to final_score (descending) to highlight biggest drivers.

### 3.4 Section below visualizations: Aspect-by-Aspect breakdown (professional layout)

- For each aspect (order: Liquidity, Solvency, Profitability, Activity, Coverage, Cashflow, Structure) render a row/card with:
  - **Title** (e.g. "Liquidity")
  - **Score** (large), **Status** (`*_status`), **Reason** (`*_reason`) — displayed compactly.
  - **Analysis** (long text) from `*_analysis` (the AI-generated narrative or rule-based analysis) — collapsible.
  - **Small KPI row** with 2–3 most-relevant submetrics names & values (pulled from `df_agg` or `df_ratios` as `*_mean` or `last-year`), e.g. for Liquidity show `current_ratio_last`, `quick_ratio_last`, `cash_ratio_last`.
- Cards should be visually consistent, well spaced, and support copying/exporting individual card text.

---

## 4. Performance Insight Deck (Deep dive) — suggested page name: **"Performance Insight Deck"**

**Tujuan:** Menjelaskan mean / std / trend tiap metrik aggregated (df_agg) dengan narasi singkat.

### Layout

- Left: `firm_id` & quick metadata (sector, region, start_year from company_info_sub).
- Center: Table of metrics (filterable) showing columns: `metric`, `mean`, `std`, `trend`, `interpretation` (auto-generated rule-based text). Support search.
- Right: `metric` detail panel (when user selects a metric row) showing:
  - Title (metric name)
  - Numeric cards: `mean`, `std`, `trend` (with sign/arrows)
  - Small textual interpretation (use rule-based template + optional AI rewrite via ZAI)
  - Sparkline showing last `max_years` trend using `df_ratios` (extract yearly values for the metric)

### Automation rules / interpretation templates (deterministic)

- **Mean** thresholds: give ranges (good/ok/poor) depending on metric type. Use the same thresholds used in the scoring code. Example: `roa_mean > 0.10 => "High"; 0.08-0.10 => "Good"; 0.05-0.08 => "Moderate"; else "Low"`.
- **Std** classification: std small => "Stable"; std large => "Volatile". Provide numeric thresholds configurable (e.g. for ratios std < 0.05 stable).
- **Trend**: positive => "Improving"; negative => "Deteriorating"; near-zero => "Flat". Show slope value.

---

## 5. Sub-Ratio Explorer (Suggested name: **"Ratio Lab"**)

**Tujuan:** Untuk setiap sub-variable (e.g. current_ratio, quick_ratio, cash_ratio, days_inventory, days_receivable, interest_coverage, dscr, ocf_ratio, free_cash_flow, fund_flow_balance, equity_to_assets, cogs_to_revenue, opex_to_revenue etc.) presentasi detail per-year.

### For each sub-ratio panel implement:

1. **Header**: Metric name (humanized), source table (e.g. df_ratios / balance_sheet_sub), and a short formula tooltip.
2. **Top KPIs**: last-year value (labelled `*_last`), direction arrow (up/down/flat), `diff_last_before` (absolute difference), `pct_change` (percentage) — color arrow green/red.
3. **Yearly line chart**: full series from `df_ratios` for that metric. Support hover to show year & value.
4. **Trend & Std block**: show `std` and `trend` (slope) from `df_agg` if available; else compute from `df_ratios` on the fly.
5. **Interpretation**: deterministic text using mean/std/trend rules (same as Performance Insight Deck). Option to call AI to rewrite.

**Notes:** Do this for all sub-variables. Panel layout should be consistent and responsive.

---

## 6. Financial Statements page (Suggested name: **"Financials Explorer"**)

**Tujuan:** Menyajikan tabel "key financial variables" & full statements with trend indicators for each numeric cell.

### 6.1 Key Financial Variables table (top)

- A vertical table listing the key variables (as specified): Net Turnover, Non-Current Assets Total, Capital and Reserves Total, Liabilities, Profit after Tax, Operating Result (Profit). Use columns per `year` horizontally.
- For each cell show: value (formatted with thousands separators) and a small indicator (▲/▼/–) plus `% change vs prior year` in smaller font & colored (green/red/gray). If prior year not available, show `—`.

### 6.2 Full statements (below)

- Present `company_info_sub` (meta), then full `balance_sheet_sub`, `income_info_sub`, `cash_flow_sub` as wide tables with `year` as columns (pivot data so years are columns). Provide toggles to show/hide groups (Current Assets, Non-current Assets, Liabilities, Equity).
- For each value cell include small delta & % change indicator (colored) beneath the main number.
- Enable CSV export per-statement and full export.

---

## 7. UI/UX, Styling & Accessibility

- Use a clean corporate theme (neutral greys + one primary color). Radar fill semi-transparent.
- Font sizes: large for final_score, medium for section headings, small for help text.
- All charts should have tooltips, axis labels, and accessible color-blind friendly palettes.
- Provide a short help modal explaining how scores are computed and the weights applied (show the final_score formula and each weight).

---

## 8. Interactivity and Filtering

- `firm_id` selector at top (supports search). Changing firm updates all panels.
- Time range filter for ratio charts (e.g. last 3/5/10 years) driven from `df_ratios` `year` values.
