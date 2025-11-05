import streamlit as st
import pandas as pd
import numpy as np
from utils.charts import ChartGenerator

def show_performance_insight(data_loader, data, current_firm):
    """Display Performance Insight Deck page"""
    st.markdown('<div class="main-header"><h1>🔍 Performance Insight Deck</h1></div>', unsafe_allow_html=True)

    df_agg = data['agg']
    df_ratios = data['ratios']
    df_company = data['company_info']

    if df_agg is None or df_agg.empty:
        st.warning("No aggregated data available")
        return

    chart_gen = ChartGenerator()

    # Layout: Company info, metrics table, and detail panel
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 🏢 Company Info")
        st.markdown(f"**Firm ID:** {current_firm}")

        if df_company is not None and not df_company.empty:
            # Show available company information
            for col in df_company.columns:
                if col != 'firm_id' and pd.notna(df_company[col].iloc[0]):
                    st.markdown(f"**{col.replace('_', ' ').title()}:** {df_company[col].iloc[0]}")

        if df_ratios is not None and not df_ratios.empty:
            years = df_ratios['year'].sort_values().unique()
            st.markdown(f"**Analysis Period:** {years[0]} - {years[-1]} ({len(years)} years)")

        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📊 Aggregated Metrics")

        # Create metrics table
        metrics_data = []

        # Process df_agg columns
        for col in df_agg.columns:
            if col != 'firm_id' and any(suffix in col for suffix in ['_mean', '_std', '_trend']):
                base_metric = col.replace('_mean', '').replace('_std', '').replace('_trend', '')

                # Skip if we've already processed this metric
                if any(d['metric'] == base_metric for d in metrics_data):
                    continue

                mean_val = df_agg[f"{base_metric}_mean"].iloc[0] if f"{base_metric}_mean" in df_agg.columns else None
                std_val = df_agg[f"{base_metric}_std"].iloc[0] if f"{base_metric}_std" in df_agg.columns else None
                trend_val = df_agg[f"{base_metric}_trend"].iloc[0] if f"{base_metric}_trend" in df_agg.columns else None

                # Generate interpretation
                mean_interpret = _interpret_mean(base_metric, mean_val)
                std_interpret = _interpret_std(std_val)
                trend_interpret = _interpret_trend(trend_val)

                combined_interpret = f"{mean_interpret}. {std_interpret}. {trend_interpret}."

                metrics_data.append({
                    'metric': base_metric,
                    'mean': f"{mean_val:.3f}" if pd.notna(mean_val) else "N/A",
                    'std': f"{std_val:.3f}" if pd.notna(std_val) else "N/A",
                    'trend': f"{trend_val:.3f}" if pd.notna(trend_val) else "N/A",
                    'interpretation': combined_interpret
                })

        if metrics_data:
            metrics_df = pd.DataFrame(metrics_data)

            # Add search functionality
            search_term = st.text_input("🔍 Search metrics...", placeholder="Type metric name...")

            if search_term:
                filtered_df = metrics_df[metrics_df['metric'].str.contains(search_term, case=False)]
            else:
                filtered_df = metrics_df

            # Display metrics table
            for _, row in filtered_df.iterrows():
                with st.expander(f"**{row['metric'].replace('_', ' ').title()}**"):
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Mean", row['mean'])
                    with col_b:
                        st.metric("Std Dev", row['std'])
                    with col_c:
                        st.metric("Trend", row['trend'])
                    st.markdown(f"**Interpretation:** {row['interpretation']}")
        else:
            st.info("No aggregated metrics available")

        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### 📈 Metric Detail")

        # Show detail for selected metric (if any)
        if 'selected_metric' in st.session_state and df_ratios is not None:
            metric = st.session_state.selected_metric

            st.markdown(f"**{metric.replace('_', ' ').title()}**")

            # Get values from df_agg
            mean_val = df_agg[f"{metric}_mean"].iloc[0] if f"{metric}_mean" in df_agg.columns else None
            std_val = df_agg[f"{metric}_std"].iloc[0] if f"{metric}_std" in df_agg.columns else None
            trend_val = df_agg[f"{metric}_trend"].iloc[0] if f"{metric}_trend" in df_agg.columns else None

            # Display numeric cards
            if pd.notna(mean_val):
                st.markdown(f"**Mean:** {mean_val:.3f}")
            if pd.notna(std_val):
                st.markdown(f"**Std Dev:** {std_val:.3f}")
            if pd.notna(trend_val):
                st.markdown(f"**Trend:** {trend_val:.3f}")

            # Interpretation
            mean_interpret = _interpret_mean(metric, mean_val)
            std_interpret = _interpret_std(std_val)
            trend_interpret = _interpret_trend(trend_val)

            st.markdown("---")
            st.markdown("**Interpretation:**")
            st.markdown(f"• {mean_interpret}")
            st.markdown(f"• {std_interpret}")
            st.markdown(f"• {trend_interpret}")

            # Trend chart
            if metric in df_ratios.columns:
                st.markdown("---")
                st.markdown("**Historical Trend:**")
                trend_fig = chart_gen.create_trend_chart(df_ratios, metric)
                st.plotly_chart(trend_fig, use_container_width=True)
        else:
            st.info("Select a metric from the table to view details")

        st.markdown('</div>', unsafe_allow_html=True)

    # Store selected metric in session state
    if st.session_state.get('selected_metric') and metrics_data:
        selected_exists = any(d['metric'] == st.session_state.selected_metric for d in metrics_data)
        if not selected_exists:
            st.session_state.selected_metric = None

def _interpret_mean(metric: str, value: float) -> str:
    """Interpret mean value based on metric type"""
    if pd.isna(value):
        return "No data available"

    metric_lower = metric.lower()

    # Profitability metrics
    if any(x in metric_lower for x in ['roa', 'roe', 'net_profit_margin', 'gross_margin']):
        if value > 0.15:
            return "Excellent profitability"
        elif value > 0.10:
            return "Good profitability"
        elif value > 0.05:
            return "Moderate profitability"
        else:
            return "Low profitability"

    # Liquidity ratios
    elif any(x in metric_lower for x in ['current_ratio', 'quick_ratio', 'cash_ratio']):
        if value > 2.0:
            return "Very strong liquidity"
        elif value > 1.5:
            return "Strong liquidity"
        elif value > 1.0:
            return "Adequate liquidity"
        else:
            return "Weak liquidity"

    # Leverage/Solvency metrics
    elif any(x in metric_lower for x in ['debt_to_equity', 'debt_to_assets']):
        if value < 0.3:
            return "Very low leverage"
        elif value < 0.6:
            return "Moderate leverage"
        elif value < 1.0:
            return "High leverage"
        else:
            return "Very high leverage"

    # Efficiency ratios
    elif any(x in metric_lower for x in ['asset_turnover', 'inventory_turnover']):
        if value > 1.5:
            return "Excellent efficiency"
        elif value > 1.0:
            return "Good efficiency"
        elif value > 0.5:
            return "Moderate efficiency"
        else:
            return "Low efficiency"

    # Coverage ratios
    elif any(x in metric_lower for x in ['interest_coverage', 'dscr']):
        if value > 3.0:
            return "Very strong coverage"
        elif value > 2.0:
            return "Strong coverage"
        elif value > 1.5:
            return "Adequate coverage"
        else:
            return "Weak coverage"

    # Days metrics
    elif any(x in metric_lower for x in ['days_inventory', 'days_receivable', 'days_payable']):
        if metric_lower == 'days_inventory':
            if value < 30:
                return "Very efficient inventory management"
            elif value < 60:
                return "Good inventory management"
            elif value < 90:
                return "Moderate inventory management"
            else:
                return "Slow inventory turnover"
        elif metric_lower == 'days_receivable':
            if value < 30:
                return "Very efficient collection"
            elif value < 45:
                return "Good collection"
            elif value < 60:
                return "Moderate collection"
            else:
                return "Slow collection"
        else:
            return f"Average of {value:.1f} days"

    else:
        return f"Average value of {value:.3f}"

def _interpret_std(value: float) -> str:
    """Interpret standard deviation"""
    if pd.isna(value):
        return "No volatility data"

    if value < 0.05:
        return "Very stable performance"
    elif value < 0.10:
        return "Stable performance"
    elif value < 0.20:
        return "Moderate volatility"
    else:
        return "High volatility"

def _interpret_trend(value: float) -> str:
    """Interpret trend"""
    if pd.isna(value):
        return "No clear trend"

    if value > 0.05:
        return "Strong improving trend"
    elif value > 0.02:
        return "Improving trend"
    elif value > -0.02:
        return "Stable trend"
    elif value > -0.05:
        return "Deteriorating trend"
    else:
        return "Strong deteriorating trend"