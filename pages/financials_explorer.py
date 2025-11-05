import streamlit as st
import pandas as pd
import numpy as np
from utils.charts import ChartGenerator

def show_financials_explorer(data_loader, data, current_firm):
    """Display Financial Statements Explorer page"""
    st.markdown('<div class="main-header"><h1>💰 Financials Explorer</h1></div>', unsafe_allow_html=True)

    df_ratios = data['ratios']
    df_company = data['company_info']
    df_balance = data['balance_sheet']
    df_income = data['income_info']
    df_cash_flow = data['cash_flow']

    if df_ratios is None or df_ratios.empty:
        st.warning("No financial data available")
        return

    chart_gen = ChartGenerator()

    # Key Financial Variables section
    st.markdown("## 📊 Key Financial Variables")
    _display_key_financial_variables(df_ratios, chart_gen)

    st.markdown("---")

    # Full statements sections
    st.markdown("## 📋 Financial Statements")

    # Tabs for different statements
    tab1, tab2, tab3, tab4 = st.tabs(["Company Info", "Balance Sheet", "Income Statement", "Cash Flow"])

    with tab1:
        _display_company_info(df_company)

    with tab2:
        _display_balance_sheet(df_balance, chart_gen)

    with tab3:
        _display_income_statement(df_income, chart_gen)

    with tab4:
        _display_cash_flow_statement(df_cash_flow, chart_gen)

def _display_key_financial_variables(df_ratios: pd.DataFrame, chart_gen):
    """Display key financial variables table"""
    if df_ratios.empty:
        return

    # Define key variables to display
    key_variables = {
        'revenue': 'Net Turnover',
        'total_assets': 'Total Assets',
        'total_equity': 'Capital & Reserves Total',
        'total_liabilities': 'Liabilities',
        'net_profit': 'Profit after Tax',
        'operating_profit': 'Operating Result (Profit)'
    }

    # Get years sorted
    years = sorted(df_ratios['year'].unique())
    if len(years) < 2:
        st.info("Need at least 2 years of data for trend analysis")
        return

    # Create the display table
    display_data = []

    for var_key, var_name in key_variables.items():
        row_data = {'Variable': var_name}

        for year in years:
            year_data = df_ratios[df_ratios['year'] == year]
            if not year_data.empty and var_key in year_data.columns:
                value = year_data[var_key].iloc[0]
                if pd.notna(value):
                    row_data[str(year)] = value
                else:
                    row_data[str(year)] = None
            else:
                row_data[str(year)] = None

        # Calculate trend if we have data
        if len(years) >= 2:
            current_val = row_data.get(str(years[-1]))
            prev_val = row_data.get(str(years[-2]))

            if pd.notna(current_val) and pd.notna(prev_val) and prev_val != 0:
                pct_change = ((current_val - prev_val) / prev_val) * 100
                row_data['Change %'] = pct_change
            else:
                row_data['Change %'] = None

        display_data.append(row_data)

    if display_data:
        df_display = pd.DataFrame(display_data)

        # Display as styled table
        for i, row in df_display.iterrows():
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])

            with col1:
                st.markdown(f"**{row['Variable']}**")

            with col2:
                if len(years) >= 1 and pd.notna(row.get(str(years[-1]))):
                    st.markdown(f"{chart_gen.format_number(row[str(years[-1])], 0)}")
                else:
                    st.markdown("—")

            with col3:
                if len(years) >= 2 and pd.notna(row.get(str(years[-2]))):
                    st.markdown(f"{chart_gen.format_number(row[str(years[-2])], 0)}")
                else:
                    st.markdown("—")

            with col4:
                if pd.notna(row.get('Change %')):
                    change_val = row['Change %']
                    if change_val > 0:
                        st.markdown(f"📈 +{change_val:.1f}%")
                    elif change_val < 0:
                        st.markdown(f"📉 {change_val:.1f}%")
                    else:
                        st.markdown("➡️ 0.0%")
                else:
                    st.markdown("—")

            st.markdown("---")

def _display_company_info(df_company: pd.DataFrame):
    """Display company information"""
    if df_company is None or df_company.empty:
        st.info("No company information available")
        return

    st.markdown('<div class="metric-card">', unsafe_allow_html=True)

    for col in df_company.columns:
        if col != 'firm_id':
            value = df_company[col].iloc[0]
            if pd.notna(value):
                st.markdown(f"**{col.replace('_', ' ').title()}:** {value}")

    st.markdown('</div>', unsafe_allow_html=True)

def _display_balance_sheet(df_balance: pd.DataFrame, chart_gen):
    """Display balance sheet data"""
    if df_balance is None or df_balance.empty:
        st.info("No balance sheet data available")
        return

    st.markdown('<div class="metric-card">', unsafe_allow_html=True)

    # Pivot data to have years as columns
    years = sorted(df_balance['year'].unique())

    # Filter numeric columns
    numeric_cols = df_balance.select_dtypes(include=[np.number]).columns.tolist()
    if 'year' in numeric_cols:
        numeric_cols.remove('year')
    if 'firm_id' in numeric_cols:
        numeric_cols.remove('firm_id')

    # Group by categories (simplified grouping)
    asset_cols = [col for col in numeric_cols if any(x in col.lower() for x in ['asset', 'cash', 'receivable', 'inventory', 'equipment', 'property'])]
    liability_cols = [col for col in numeric_cols if any(x in col.lower() for x in ['liability', 'debt', 'payable', 'loan'])]
    equity_cols = [col for col in numeric_cols if any(x in col.lower() for x in ['equity', 'capital', 'reserve', 'retained'])]

    # Display Assets section
    if asset_cols:
        st.markdown("### 🏦 Assets")
        for col in asset_cols:
            _display_financial_line_item(df_balance, col, years, chart_gen)

    # Display Liabilities section
    if liability_cols:
        st.markdown("### 💳 Liabilities")
        for col in liability_cols:
            _display_financial_line_item(df_balance, col, years, chart_gen)

    # Display Equity section
    if equity_cols:
        st.markdown("### 💰 Equity")
        for col in equity_cols:
            _display_financial_line_item(df_balance, col, years, chart_gen)

    st.markdown('</div>', unsafe_allow_html=True)

def _display_income_statement(df_income: pd.DataFrame, chart_gen):
    """Display income statement data"""
    if df_income is None or df_income.empty:
        st.info("No income statement data available")
        return

    st.markdown('<div class="metric-card">', unsafe_allow_html=True)

    years = sorted(df_income['year'].unique())
    numeric_cols = df_income.select_dtypes(include=[np.number]).columns.tolist()
    if 'year' in numeric_cols:
        numeric_cols.remove('year')
    if 'firm_id' in numeric_cols:
        numeric_cols.remove('firm_id')

    # Sort by typical income statement order
    priority_items = ['revenue', 'sales', 'cost', 'gross', 'operating', 'ebit', 'interest', 'tax', 'net', 'profit']
    sorted_cols = []

    for priority in priority_items:
        matches = [col for col in numeric_cols if priority in col.lower()]
        sorted_cols.extend(matches)
        numeric_cols = [col for col in numeric_cols if col not in matches]

    sorted_cols.extend(numeric_cols)  # Add remaining items

    for col in sorted_cols:
        _display_financial_line_item(df_income, col, years, chart_gen)

    st.markdown('</div>', unsafe_allow_html=True)

def _display_cash_flow_statement(df_cash_flow: pd.DataFrame, chart_gen):
    """Display cash flow statement data"""
    if df_cash_flow is None or df_cash_flow.empty:
        st.info("No cash flow statement data available")
        return

    st.markdown('<div class="metric-card">', unsafe_allow_html=True)

    years = sorted(df_cash_flow['year'].unique())
    numeric_cols = df_cash_flow.select_dtypes(include=[np.number]).columns.tolist()
    if 'year' in numeric_cols:
        numeric_cols.remove('year')
    if 'firm_id' in numeric_cols:
        numeric_cols.remove('firm_id')

    # Group by cash flow categories
    operating_cols = [col for col in numeric_cols if any(x in col.lower() for x in ['operating', 'ocf', 'working'])]
    investing_cols = [col for col in numeric_cols if any(x in col.lower() for x in ['investing', 'icapex', 'capex'])]
    financing_cols = [col for col in numeric_cols if any(x in col.lower() for x in ['financing', 'dividend', 'stock'])]

    # Display Operating Cash Flow
    if operating_cols:
        st.markdown("### 💼 Operating Cash Flow")
        for col in operating_cols:
            _display_financial_line_item(df_cash_flow, col, years, chart_gen)

    # Display Investing Cash Flow
    if investing_cols:
        st.markdown("### 🏗️ Investing Cash Flow")
        for col in investing_cols:
            _display_financial_line_item(df_cash_flow, col, years, chart_gen)

    # Display Financing Cash Flow
    if financing_cols:
        st.markdown("### 💸 Financing Cash Flow")
        for col in financing_cols:
            _display_financial_line_item(df_cash_flow, col, years, chart_gen)

    st.markdown('</div>', unsafe_allow_html=True)

def _display_financial_line_item(df: pd.DataFrame, col_name: str, years: list, chart_gen):
    """Display a single financial line item with trend indicators"""
    col1, col2, col3 = st.columns([3, 1, 1])

    # Display name
    with col1:
        display_name = col_name.replace('_', ' ').title()
        st.markdown(f"**{display_name}**")

    # Get data for years
    year_data = {}
    for year in years:
        year_df = df[df['year'] == year]
        if not year_df.empty and col_name in year_df.columns:
            year_data[year] = year_df[col_name].iloc[0]

    # Display current year value
    with col2:
        if years and years[-1] in year_data:
            current_val = year_data[years[-1]]
            if pd.notna(current_val):
                st.markdown(f"{chart_gen.format_number(current_val, 0)}")
            else:
                st.markdown("—")
        else:
            st.markdown("—")

    # Display trend indicator
    with col3:
        if len(years) >= 2:
            current_val = year_data.get(years[-1])
            prev_val = year_data.get(years[-2])

            if pd.notna(current_val) and pd.notna(prev_val) and prev_val != 0:
                pct_change = ((current_val - prev_val) / prev_val) * 100
                trend_symbol, trend_color = chart_gen.get_trend_indicator(current_val, prev_val)
                st.markdown(f"<span style='color: {trend_color}'>{trend_symbol}</span>", unsafe_allow_html=True)
            else:
                st.markdown("—")
        else:
            st.markdown("—")