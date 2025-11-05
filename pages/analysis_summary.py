import streamlit as st
import pandas as pd
from utils.charts import ChartGenerator

def show_analysis_summary(data_loader, data, current_firm):
    """Display Analysis Summary page"""
    st.markdown('<div class="main-header"><h1>📈 Analysis Summary</h1></div>', unsafe_allow_html=True)

    df_credit = data['credit_score']
    if df_credit is None or df_credit.empty:
        st.error("No credit score data available")
        return

    row = df_credit.iloc[0]
    chart_gen = ChartGenerator()

    # Main layout: Top summary section
    col1, col2 = st.columns([1, 1])

    with col1:
        # Final Score, Category, Recommendation
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### Final Credit Score")
        st.markdown(f'<div class="score-display">{row["final_score"]:.1f}</div>', unsafe_allow_html=True)

        col1a, col1b = st.columns(2)
        with col1a:
            st.metric("Category", row['kategori'])
        with col1b:
            st.metric("Recommendation", row['rekomendasi'])
        st.markdown('</div>', unsafe_allow_html=True)

        # Reasoning section
        st.markdown('<div class="metric-card" style="margin-top: 1rem;">', unsafe_allow_html=True)
        st.markdown("### 📝 Reasoning")

        if st.button("📖 Show Full Reasoning", key="reasoning_toggle"):
            st.session_state.show_reasoning = not st.session_state.get('show_reasoning', False)

        if st.session_state.get('show_reasoning', False):
            st.markdown(f"**{row['reasoning']}**")
        else:
            # Show truncated version
            reasoning_preview = row['reasoning'][:200] + "..." if len(row['reasoning']) > 200 else row['reasoning']
            st.markdown(f"*{reasoning_preview}*")
        st.markdown('</div>', unsafe_allow_html=True)

        # GenAI Recommendation (if exists)
        if pd.notna(row.get('genai_recommendation')) and row['genai_recommendation'].strip():
            st.markdown('<div class="genai-recommendation" style="margin-top: 1rem;">', unsafe_allow_html=True)
            st.markdown("### 🤖 AI Recommendation")
            st.markdown(f"*{row['genai_recommendation']}*")
            st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        # Radar Chart
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("### Performance Radar")
        radar_fig = chart_gen.create_radar_chart(df_credit)
        st.plotly_chart(radar_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Middle section: Combined Bar Chart
    st.markdown("---")
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown("### Aspect Score Breakdown")

    contributions_df = data_loader.get_aspect_contributions(df_credit)
    bar_fig = chart_gen.create_aspect_bar_chart(contributions_df)
    st.plotly_chart(bar_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Aspect-by-Aspect breakdown
    st.markdown("---")
    st.markdown("## Detailed Analysis by Aspect")

    aspects = [
        ('Liquidity', 'liquidity_score', 'liquidity_status', 'liquidity_reason', 'liquidity_analysis'),
        ('Solvency', 'solvency_score', 'solvency_status', 'solvency_reason', 'solvency_analysis'),
        ('Profitability', 'profitability_score', 'profitability_status', 'profitability_reason', 'profitability_analysis'),
        ('Activity', 'activity_score', 'activity_status', 'activity_reason', 'activity_analysis'),
        ('Coverage', 'coverage_score', 'coverage_status', 'coverage_reason', 'coverage_analysis'),
        ('Cashflow', 'cashflow_score', 'cashflow_status', 'cashflow_reason', 'cashflow_analysis'),
        ('Structure', 'structure_score', 'structure_status', 'structure_reason', 'structure_analysis')
    ]

    for aspect_name, score_col, status_col, reason_col, analysis_col in aspects:
        with st.container():
            st.markdown(f'<div class="aspect-card">', unsafe_allow_html=True)

            # Header with score and status
            col_header1, col_header2, col_header3 = st.columns([1, 1, 2])

            with col_header1:
                score_value = row[score_col]
                st.markdown(f"### {aspect_name}")
                st.markdown(f'<div class="score-display" style="font-size: 2rem;">{score_value:.1f}</div>', unsafe_allow_html=True)

            with col_header2:
                status_value = row[status_col]
                status_class = f"status-{status_value.lower().replace(' ', '-')}"
                st.markdown(f"### Status")
                st.markdown(f'<span class="{status_class}">{status_value}</span>', unsafe_allow_html=True)
                st.markdown(f"**Weight:** {data_loader.aspect_weights[aspect_name.lower()]*100:.0f}%")

            with col_header3:
                st.markdown("### Key Reason")
                st.markdown(f"*{row[reason_col]}*")

            # Analysis section (collapsible)
            button_key = f"button_{aspect_name.lower()}"
            state_key = f"analysis_{aspect_name.lower()}"

            if st.button(f"📊 View {aspect_name} Analysis", key=button_key):
                st.session_state[state_key] = not st.session_state.get(state_key, False)

            if st.session_state.get(state_key, False):
                st.markdown("---")
                st.markdown("#### Detailed Analysis")
                st.markdown(f"*{row[analysis_col]}*")

                # Add some relevant KPIs if we have ratio data
                if data['ratios'] is not None and not data['ratios'].empty:
                    latest_year = data['ratios']['year'].max()
                    latest_data = data['ratios'][data['ratios']['year'] == latest_year]

                    if not latest_data.empty:
                        st.markdown("**Latest Period Key Metrics:**")
                        cols = st.columns(3)

                        # Show relevant metrics based on aspect
                        if aspect_name.lower() == 'liquidity':
                            metrics = ['current_ratio', 'quick_ratio', 'cash_ratio']
                        elif aspect_name.lower() == 'solvency':
                            metrics = ['debt_to_equity', 'equity_to_assets', 'interest_coverage']
                        elif aspect_name.lower() == 'profitability':
                            metrics = ['roa', 'roe', 'net_profit_margin']
                        elif aspect_name.lower() == 'activity':
                            metrics = ['days_inventory', 'days_receivable', 'asset_turnover']
                        elif aspect_name.lower() == 'coverage':
                            metrics = ['interest_coverage', 'dscr', 'cash_coverage']
                        elif aspect_name.lower() == 'cashflow':
                            metrics = ['ocf_ratio', 'fcf_ratio', 'cash_conversion_cycle']
                        elif aspect_name.lower() == 'structure':
                            metrics = ['equity_to_assets', 'debt_to_assets', 'working_capital_ratio']
                        else:
                            metrics = []

                        for i, metric in enumerate(metrics[:3]):
                            if metric in latest_data.columns:
                                with cols[i]:
                                    value = latest_data[metric].iloc[0]
                                    if pd.notna(value):
                                        st.metric(metric.replace('_', ' ').title(), f"{value:.2f}")

            st.markdown('</div>', unsafe_allow_html=True)