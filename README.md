# Credit Analysis Dashboard

A comprehensive Streamlit dashboard for credit analysis, designed as a copilot for credit analysts. This dashboard provides quick, explainable, and actionable insights from preprocessed credit analysis data.

## Features

### 📈 Analysis Summary
- **Final credit score display** with prominent visualization
- **Radar chart** showing 7 aspect scores (Liquidity, Solvency, Profitability, Activity, Coverage, Cashflow, Structure)
- **Weighted bar chart** showing aspect contributions to final score
- **Detailed aspect breakdown** with scores, status, reasons, and analysis
- **AI recommendations** display (if available)

### 🔍 Performance Insight Deck
- **Aggregated metrics table** with mean, standard deviation, and trend analysis
- **Searchable metrics** with intelligent categorization
- **Rule-based interpretations** for each metric
- **Historical trend charts** with sparklines
- **Detailed metric analysis** panel

### 🧮 Ratio Lab - Sub-Ratio Explorer
- **Comprehensive ratio panels** organized by categories:
  - Liquidity Ratios
  - Solvency Ratios
  - Profitability Ratios
  - Activity/Efficiency Ratios
  - Coverage Ratios
  - Cash Flow Ratios
- **KPI displays** with trend indicators
- **Historical trend charts** for each ratio
- **Automated interpretations** based on industry standards

### 💰 Financial Statements Explorer
- **Key financial variables** summary with trend analysis
- **Company information** display
- **Balance sheet** analysis with trend indicators
- **Income statement** with year-over-year comparisons
- **Cash flow statement** breakdown by categories

## Data Requirements

The dashboard expects the following CSV files in the data directory:

### Core Files
- `df_credit_score.csv` - Credit scoring results (34 columns)
- `df_agg.csv` - Aggregated features (~235 columns)
- `df_ratios.csv` - Yearly ratios (~81 columns)

### Supporting Files
- `company_info_sub.csv` - Company metadata
- `balance_sheet_sub.csv` - Balance sheet data
- `income_info_sub.csv` - Income statement data
- `cash_flow_sub.csv` - Cash flow data

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your data files are located in the correct directory:
```
D:/Project/portfolio/coba_streamlit(this project)/data/
```

## Usage

Run the dashboard:
```bash
streamlit run app.py
```

Navigate through the pages using the sidebar:
- **Analysis Summary** - Main overview with visualizations
- **Performance Insight Deck** - Deep-dive into aggregated metrics
- **Sub-Ratio Explorer** - Detailed ratio analysis
- **Financial Statements** - Raw financial data with trends

## Technical Architecture

### Project Structure
```
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── utils/
│   ├── data_loader.py    # Data loading and validation
│   └── charts.py         # Chart generation utilities
└── pages/
    ├── analysis_summary.py
    ├── performance_insight.py
    ├── ratio_explorer.py
    └── financials_explorer.py
```

### Key Components

1. **DataLoader** - Handles CSV loading, validation, and data processing
2. **ChartGenerator** - Creates consistent charts and visualizations
3. **Page Modules** - Separate modules for each dashboard page

### Styling
- Corporate theme with responsive design
- Color-blind friendly palettes
- Interactive tooltips and hover states
- Professional metric cards and layouts

## Data Column Requirements

### df_credit_score.csv (Required columns)
```
firm_id,
liquidity_score, liquidity_reason, liquidity_status,
solvency_score, solvency_reason, solvency_status,
profitability_score, profitability_reason, profitability_status,
activity_score, activity_reason, activity_status,
coverage_score, coverage_reason, coverage_status,
cashflow_score, cashflow_reason, cashflow_status,
structure_score, structure_reason, structure_status,
final_score, kategori, rekomendasi, reasoning,
liquidity_analysis, solvency_analysis, profitability_analysis,
activity_analysis, coverage_analysis, cashflow_analysis,
structure_analysis, genai_recommendation
```

### Scoring Weights
- Liquidity: 15%
- Solvency: 15%
- Profitability: 20%
- Activity: 10%
- Coverage: 10%
- Cashflow: 15%
- Structure: 15%

## Status Color Mapping
- **Strong/Good**: Green (#22c55e)
- **Moderate**: Yellow (#eab308)
- **Watch**: Orange (#f97316)
- **Weak/Poor**: Red (#ef4444)

## Notes

- This dashboard is designed for **single firm analysis** (prototype focus)
- File paths are **fixed** and not configurable in this version
- No **data validation** is performed - assumes clean, preprocessed data
- **Export features** are disabled in this prototype version
- Dashboard runs **locally** only

## Future Enhancements

- Multi-firm comparison mode
- File upload functionality
- PDF export capabilities
- AI-powered insights integration
- Advanced data validation
- Deployment configuration