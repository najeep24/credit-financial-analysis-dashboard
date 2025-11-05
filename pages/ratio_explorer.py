import streamlit as st
import pandas as pd
import numpy as np
from utils.charts import ChartGenerator

def show_ratio_explorer(data_loader, data, current_firm):
    """Display Sub-Ratio Explorer page"""
    st.markdown('<div class="main-header"><h1>🧮 Ratio Lab - Sub-Ratio Explorer</h1></div>', unsafe_allow_html=True)

    df_ratios = data['ratios']
    df_agg = data['agg']

    if df_ratios is None or df_ratios.empty:
        st.warning("No ratio data available")
        return

    chart_gen = ChartGenerator()

    # Get all ratio columns (excluding firm_id and year)
    ratio_columns = [col for col in df_ratios.columns if col not in ['firm_id', 'year']]

    # Group ratios by category for better organization
    ratio_categories = {
        'Liquidity Ratios': [col for col in ratio_columns if any(x in col.lower() for x in ['current_ratio', 'quick_ratio', 'cash_ratio', 'working_capital'])],
        'Solvency Ratios': [col for col in ratio_columns if any(x in col.lower() for x in ['debt_to_equity', 'debt_to_assets', 'equity_to_assets', 'leverage', 'long_term_debt_ratio'])],
        'Profitability Ratios': [col for col in ratio_columns if any(x in col.lower() for x in ['roa', 'roe', 'gross_margin', 'gross_profit_margin', 'net_profit_margin', 'ebitda_margin'])],
        'Activity/Efficiency Ratios': [col for col in ratio_columns if any(x in col.lower() for x in ['turnover', 'days_', 'asset_turnover', 'inventory_turnover'])],
        'Cash Flow Ratios': [col for col in ratio_columns if any(x in col.lower() for x in ['ocf_ratio', 'free_cash_flow', 'cash_quality_ratio'])],
        'Structure Ratios': [col for col in ratio_columns if any(x in col.lower() for x in ['fund_flow', 'equity_to_asset', 'net_margin_ratio'])]
    }

    # Remove uncategorized ratios (don't show 'Other Ratios' category)
    categorized_ratios = set()
    for category_ratios in ratio_categories.values():
        categorized_ratios.update(category_ratios)

    st.markdown("---")

    # Display all ratio categories (no selectbox)
    for category_name, category_ratios in ratio_categories.items():
        if not category_ratios:
            continue

        st.markdown(f"## {category_name}")

        # Display ratios in 3-column layout
        for i in range(0, len(category_ratios), 3):
            cols = st.columns(3)
            for j, ratio in enumerate(category_ratios[i:i+3]):
                with cols[j]:
                    _display_ratio_panel(ratio, df_ratios, df_agg, chart_gen)

def _display_ratio_panel(ratio_name: str, df_ratios: pd.DataFrame, df_agg: pd.DataFrame, chart_gen):
    """Display a single ratio panel with all details"""
    with st.container():
        st.markdown('<div class="aspect-card" style="padding: 1rem;">', unsafe_allow_html=True)

        # Header
        display_name = ratio_name.replace('_', ' ').title()
        st.markdown(f"### {display_name}")

  
        # Top KPIs section (1 column with st.metric)
        _display_kpi_section(ratio_name, df_ratios, df_agg)

        # Yearly trend chart
        _display_trend_section(ratio_name, df_ratios, chart_gen)

        # Statistics and interpretation
        _display_stats_section(ratio_name, df_ratios, df_agg)

        st.markdown('</div>', unsafe_allow_html=True)

def _display_kpi_section(ratio_name: str, df_ratios: pd.DataFrame, df_agg: pd.DataFrame):
    """Display top KPIs with trend indicators - single column layout"""
    if df_ratios.empty:
        return

    # Get latest and previous year data
    years_sorted = df_ratios['year'].sort_values().unique()
    if len(years_sorted) < 2:
        st.warning("Insufficient data for trend analysis")
        return

    latest_year = years_sorted[-1]
    previous_year = years_sorted[-2]

    latest_data = df_ratios[df_ratios['year'] == latest_year]
    previous_data = df_ratios[df_ratios['year'] == previous_year]

    if latest_data.empty or previous_data.empty:
        return

    latest_value = latest_data[ratio_name].iloc[0]
    previous_value = previous_data[ratio_name].iloc[0]

    if pd.isna(latest_value):
        st.info("No data available for latest period")
        return

    # Calculate diff and percentage change
    if pd.notna(previous_value) and previous_value != 0:
        abs_change = latest_value - previous_value
        pct_change = (abs_change / previous_value) * 100
    else:
        abs_change = 0
        pct_change = 0

    # Create delta text (without arrow since delta already provides it)
    if pd.notna(previous_value):
        delta_text = f"{abs(abs_change):.3f}/{abs(pct_change):.1f}%"
        delta_color = "normal" if abs_change >= 0 else "inverse"
    else:
        delta_text = "N/A"
        delta_color = "normal"

    # Display single metric with delta
    st.metric(
        label=f"{ratio_name.replace('_', ' ').title()}",
        value=f"{latest_value:.3f}",
        delta=delta_text,
        delta_color=delta_color
    )

def _display_trend_section(ratio_name: str, df_ratios: pd.DataFrame, chart_gen):
    """Display yearly trend chart"""
    if df_ratios.empty:
        return

    # Check if we have sufficient data for trend chart
    valid_data = df_ratios[ratio_name].dropna()
    if len(valid_data) < 2:
        st.info("Insufficient data for trend chart")
        return

    trend_fig = chart_gen.create_trend_chart(df_ratios, ratio_name)
    st.plotly_chart(trend_fig, use_container_width=True)

def _display_stats_section(ratio_name: str, df_ratios: pd.DataFrame, df_agg: pd.DataFrame):
    """Display statistics and interpretation"""
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("**Statistics:**")

        # Calculate stats from df_ratios if df_agg doesn't have them
        if df_agg is not None and not df_agg.empty:
            std_val = df_agg[f"{ratio_name}_std"].iloc[0] if f"{ratio_name}_std" in df_agg.columns else None
            trend_val = df_agg[f"{ratio_name}_trend"].iloc[0] if f"{ratio_name}_trend" in df_agg.columns else None
        else:
            # Calculate from df_ratios
            values = df_ratios[ratio_name].dropna()
            if not values.empty:
                std_val = values.std()
                # Simple trend calculation (linear regression slope)
                if len(values) > 1:
                    years = df_ratios.loc[values.index, 'year']
                    trend_val = np.polyfit(years, values, 1)[0]
                else:
                    trend_val = None
            else:
                std_val = trend_val = None

        # Standard deviation and stability status
        if pd.notna(std_val):
            stability_status = _get_stability_status(std_val)
            st.markdown(f"• **Std Dev:** {std_val:.3f} ({stability_status})")

        # Trend and trend status
        if pd.notna(trend_val):
            trend_status, trend_color = _get_trend_status(trend_val)
            st.markdown(f"• **Trend:** {trend_status} {trend_color}")

        # Data points count
        valid_points = df_ratios[ratio_name].dropna().shape[0]
        total_years = df_ratios['year'].nunique()
        st.markdown(f"• **Data Points:** {valid_points}/{total_years}")

    with col2:
        st.markdown("**Interpretation:**")

        # Generate interpretation based on stats
        interpretation = _generate_ratio_interpretation(ratio_name, std_val, trend_val)
        st.markdown(interpretation)

def _get_stability_status(std_val: float) -> str:
    """Get stability status based on standard deviation"""
    if std_val < 0.05:
        return "High Stability"
    elif std_val < 0.15:
        return "Moderate Stability"
    else:
        return "High Volatility"

def _get_trend_status(trend_val: float) -> tuple:
    """Get trend status and color indicator"""
    if trend_val > 0.02:
        return ("Improving", "🟢")
    elif trend_val < -0.02:
        return ("Declining", "🔴")
    else:
        return ("Stable", "🟡")

def _generate_ratio_interpretation(ratio_name: str, std_val: float, trend_val: float) -> str:
    """Generate interpretation for a ratio based on stability and trend"""
    interpretation_parts = []

    # Stability interpretation
    if pd.notna(std_val):
        if std_val < 0.05:
            interpretation_parts.append("The metric shows **high stability** over time with consistent performance.")
        elif std_val < 0.15:
            interpretation_parts.append("The metric shows **moderate stability** with some acceptable fluctuations.")
        else:
            interpretation_parts.append("The metric shows **high volatility** indicating inconsistent performance that may require attention.")

    # Trend interpretation
    if pd.notna(trend_val):
        if trend_val > 0.02:
            interpretation_parts.append("There is a **positive improving trend** over time, suggesting favorable development.")
        elif trend_val < -0.02:
            interpretation_parts.append("There is a **declining trend** that may require management attention and intervention.")
        else:
            interpretation_parts.append("The metric remains **relatively stable** over time without significant directional change.")

    # Ratio-specific interpretation based on trend
    ratio_lower = ratio_name.lower()
    if pd.notna(trend_val):
        if any(x in ratio_lower for x in ['current_ratio', 'quick_ratio', 'cash_ratio']):
            if trend_val > 0.02:
                interpretation_parts.append("Liquidity position is **strengthening**, improving ability to meet short-term obligations.")
            elif trend_val < -0.02:
                interpretation_parts.append("Liquidity position is **weakening**, potentially creating short-term financial stress.")
        elif any(x in ratio_lower for x in ['debt_to_equity', 'debt_to_assets']):
            if trend_val > 0.02:
                interpretation_parts.append("Leverage is **increasing**, potentially raising financial risk profile.")
            elif trend_val < -0.02:
                interpretation_parts.append("Leverage is **decreasing**, strengthening the balance sheet position.")
        elif any(x in ratio_lower for x in ['roa', 'roe', 'net_profit_margin']):
            if trend_val > 0.02:
                interpretation_parts.append("Profitability is **improving**, indicating better operational efficiency.")
            elif trend_val < -0.02:
                interpretation_parts.append("Profitability is **declining**, suggesting operational challenges that need addressing.")

    return " ".join(interpretation_parts) if interpretation_parts else "Insufficient data for comprehensive interpretation."

def _get_ratio_formula(ratio_name: str) -> str:
    """Get formula for common ratios"""
    formulas = {
        'current_ratio': 'Current Assets / Current Liabilities',
        'quick_ratio': '(Current Assets - Inventory) / Current Liabilities',
        'cash_ratio': 'Cash & Cash Equivalents / Current Liabilities',
        'debt_to_equity': 'Total Debt / Total Equity',
        'debt_to_assets': 'Total Debt / Total Assets',
        'equity_to_assets': 'Total Equity / Total Assets',
        'roa': 'Net Income / Total Assets',
        'roe': 'Net Income / Total Equity',
        'gross_margin': 'Gross Profit / Revenue',
        'net_profit_margin': 'Net Income / Revenue',
        'interest_coverage': 'EBIT / Interest Expense',
        'dscr': 'Operating Cash Flow / Total Debt Service',
        'asset_turnover': 'Revenue / Total Assets',
        'inventory_turnover': 'Cost of Goods Sold / Average Inventory',
        'days_inventory': '365 / Inventory Turnover',
        'days_receivable': '365 / Receivables Turnover',
        'ocf_ratio': 'Operating Cash Flow / Revenue'
    }

    return formulas.get(ratio_name.lower(), "")