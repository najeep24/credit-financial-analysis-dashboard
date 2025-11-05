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
        'Solvency Ratios': [col for col in ratio_columns if any(x in col.lower() for x in ['debt_to_equity', 'debt_to_assets', 'equity_to_assets', 'leverage'])],
        'Profitability Ratios': [col for col in ratio_columns if any(x in col.lower() for x in ['roa', 'roe', 'gross_margin', 'net_profit_margin', 'ebitda_margin'])],
        'Activity/Efficiency Ratios': [col for col in ratio_columns if any(x in col.lower() for x in ['turnover', 'days_', 'asset_turnover', 'inventory_turnover'])],
        'Coverage Ratios': [col for col in ratio_columns if any(x in col.lower() for x in ['coverage', 'dscr', 'interest_coverage'])],
        'Cash Flow Ratios': [col for col in ratio_columns if any(x in col.lower() for x in ['ocf', 'fcf', 'cash_flow', 'cash_conversion'])],
        'Other Ratios': []  # Catch-all
    }

    # Move uncategorized ratios to 'Other'
    categorized_ratios = set()
    for category_ratios in ratio_categories.values():
        categorized_ratios.update(category_ratios)

    uncategorized = [col for col in ratio_columns if col not in categorized_ratios]
    ratio_categories['Other Ratios'] = uncategorized

    # Category selector
    selected_category = st.selectbox(
        "Select Ratio Category:",
        list(ratio_categories.keys()),
        index=0
    )

    st.markdown("---")

    # Display ratios for selected category
    category_ratios = ratio_categories[selected_category]

    if not category_ratios:
        st.info(f"No ratios found in {selected_category}")
        return

    # Display each ratio as a panel
    for ratio in category_ratios:
        _display_ratio_panel(ratio, df_ratios, df_agg, chart_gen)

def _display_ratio_panel(ratio_name: str, df_ratios: pd.DataFrame, df_agg: pd.DataFrame, chart_gen):
    """Display a single ratio panel with all details"""
    with st.container():
        st.markdown('<div class="aspect-card">', unsafe_allow_html=True)

        # Header
        col1, col2 = st.columns([3, 1])

        with col1:
            display_name = ratio_name.replace('_', ' ').title()
            st.markdown(f"### {display_name}")

            # Add formula tooltip if available
            formula = _get_ratio_formula(ratio_name)
            if formula:
                st.caption(f"Formula: {formula}")

        with col2:
            # Source indicator
            st.markdown("**Source:** df_ratios")

        # Top KPIs section
        _display_kpi_section(ratio_name, df_ratios, chart_gen)

        # Yearly trend chart
        _display_trend_section(ratio_name, df_ratios, chart_gen)

        # Statistics and interpretation
        _display_stats_section(ratio_name, df_ratios, df_agg)

        st.markdown('</div>', unsafe_allow_html=True)

def _display_kpi_section(ratio_name: str, df_ratios: pd.DataFrame, chart_gen):
    """Display top KPIs with trend indicators"""
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

    # KPI columns
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

    with col1:
        st.metric(
            f"{latest_year} Value",
            f"{latest_value:.3f}",
            delta=None
        )

    with col2:
        if pd.notna(previous_value):
            pct_change = ((latest_value - previous_value) / previous_value) * 100 if previous_value != 0 else 0
            st.metric(
                "% Change",
                f"{pct_change:.1f}%",
                delta=f"{pct_change:.1f}%",
                delta_color="normal" if abs(pct_change) < 5 else ("inverse" if pct_change < 0 else "normal")
            )
        else:
            st.metric("% Change", "N/A")

    with col3:
        if pd.notna(previous_value):
            abs_change = latest_value - previous_value
            st.metric(
                "Abs Change",
                f"{abs_change:.3f}",
                delta=f"{abs_change:.3f}",
                delta_color="normal" if abs(abs_change) < 0.1 else ("inverse" if abs_change < 0 else "normal")
            )
        else:
            st.metric("Abs Change", "N/A")

    with col4:
        # Direction indicator
        if pd.notna(previous_value):
            if latest_value > previous_value:
                st.markdown("📈 **Improving**")
            elif latest_value < previous_value:
                st.markdown("📉 **Declining**")
            else:
                st.markdown("➡️ **Stable**")
        else:
            st.markdown("➡️ **Stable**")

def _display_trend_section(ratio_name: str, df_ratios: pd.DataFrame, chart_gen):
    """Display yearly trend chart"""
    st.markdown("#### Historical Trend")

    trend_fig = chart_gen.create_trend_chart(df_ratios, ratio_name)
    st.plotly_chart(trend_fig, use_container_width=True)

def _display_stats_section(ratio_name: str, df_ratios: pd.DataFrame, df_agg: pd.DataFrame):
    """Display statistics and interpretation"""
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("**Statistics:**")

        # Calculate stats from df_ratios if df_agg doesn't have them
        if df_agg is not None and not df_agg.empty:
            mean_val = df_agg[f"{ratio_name}_mean"].iloc[0] if f"{ratio_name}_mean" in df_agg.columns else None
            std_val = df_agg[f"{ratio_name}_std"].iloc[0] if f"{ratio_name}_std" in df_agg.columns else None
            trend_val = df_agg[f"{ratio_name}_trend"].iloc[0] if f"{ratio_name}_trend" in df_agg.columns else None
        else:
            # Calculate from df_ratios
            values = df_ratios[ratio_name].dropna()
            if not values.empty:
                mean_val = values.mean()
                std_val = values.std()
                # Simple trend calculation (linear regression slope)
                if len(values) > 1:
                    years = df_ratios.loc[values.index, 'year']
                    trend_val = np.polyfit(years, values, 1)[0]
                else:
                    trend_val = None
            else:
                mean_val = std_val = trend_val = None

        if pd.notna(mean_val):
            st.markdown(f"• **Mean:** {mean_val:.3f}")
        if pd.notna(std_val):
            st.markdown(f"• **Std Dev:** {std_val:.3f}")
        if pd.notna(trend_val):
            st.markdown(f"• **Trend:** {trend_val:.4f}")

        # Data points count
        valid_points = df_ratios[ratio_name].dropna().shape[0]
        total_years = df_ratios['year'].nunique()
        st.markdown(f"• **Data Points:** {valid_points}/{total_years}")

    with col2:
        st.markdown("**Interpretation:**")

        # Generate interpretation based on stats
        interpretation = _generate_ratio_interpretation(ratio_name, mean_val, std_val, trend_val)
        st.markdown(interpretation)

def _generate_ratio_interpretation(ratio_name: str, mean_val: float, std_val: float, trend_val: float) -> str:
    """Generate interpretation for a ratio"""
    if pd.isna(mean_val):
        return "No sufficient data for interpretation."

    ratio_lower = ratio_name.lower()
    interpretation_parts = []

    # Mean interpretation
    if any(x in ratio_lower for x in ['current_ratio', 'quick_ratio', 'cash_ratio']):
        if mean_val > 2.0:
            interpretation_parts.append("The company maintains **strong liquidity** with comfortable buffer to meet short-term obligations.")
        elif mean_val > 1.5:
            interpretation_parts.append("The company shows **adequate liquidity** to meet short-term obligations.")
        elif mean_val > 1.0:
            interpretation_parts.append("The company has **marginal liquidity** and may face challenges meeting short-term obligations.")
        else:
            interpretation_parts.append("The company has **weak liquidity** and potential difficulty meeting short-term obligations.")

    elif any(x in ratio_lower for x in ['debt_to_equity', 'debt_to_assets']):
        if mean_val < 0.5:
            interpretation_parts.append("The company maintains **conservative leverage** with low debt levels.")
        elif mean_val < 1.0:
            interpretation_parts.append("The company has **moderate leverage** within acceptable ranges.")
        else:
            interpretation_parts.append("The company shows **high leverage** which may increase financial risk.")

    elif any(x in ratio_lower for x in ['roa', 'roe', 'net_profit_margin']):
        if mean_val > 0.10:
            interpretation_parts.append("The company demonstrates **strong profitability** compared to industry standards.")
        elif mean_val > 0.05:
            interpretation_parts.append("The company shows **moderate profitability** with room for improvement.")
        else:
            interpretation_parts.append("The company has **low profitability** and may need operational improvements.")

    elif any(x in ratio_lower for x in ['interest_coverage', 'dscr']):
        if mean_val > 3.0:
            interpretation_parts.append("The company has **excellent coverage** ability for debt obligations.")
        elif mean_val > 2.0:
            interpretation_parts.append("The company maintains **adequate coverage** for debt obligations.")
        else:
            interpretation_parts.append("The company has **weak coverage** and may struggle with debt obligations.")

    elif 'days_' in ratio_lower:
        if 'inventory' in ratio_lower:
            if mean_val < 45:
                interpretation_parts.append("The company shows **efficient inventory management** with quick turnover.")
            elif mean_val < 90:
                interpretation_parts.append("The company has **moderate inventory turnover**.")
            else:
                interpretation_parts.append("The company has **slow inventory turnover** which may tie up capital.")
        elif 'receivable' in ratio_lower:
            if mean_val < 30:
                interpretation_parts.append("The company has **excellent collection efficiency**.")
            elif mean_val < 60:
                interpretation_parts.append("The company shows **good collection efficiency**.")
            else:
                interpretation_parts.append("The company has **slow collection** which may affect cash flow.")

    # Stability interpretation
    if pd.notna(std_val):
        if std_val < 0.05:
            interpretation_parts.append("The metric shows **high stability** over time.")
        elif std_val < 0.15:
            interpretation_parts.append("The metric shows **moderate stability** with some fluctuations.")
        else:
            interpretation_parts.append("The metric shows **high volatility** indicating inconsistency.")

    # Trend interpretation
    if pd.notna(trend_val):
        if trend_val > 0.02:
            interpretation_parts.append("There is a **positive improving trend** over time.")
        elif trend_val < -0.02:
            interpretation_parts.append("There is a **declining trend** that may require attention.")
        else:
            interpretation_parts.append("The metric remains **relatively stable** over time.")

    return " ".join(interpretation_parts) if interpretation_parts else "Metric analysis available."

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