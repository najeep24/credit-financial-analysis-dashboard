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
    _display_key_financial_variables(data, chart_gen)

    st.markdown("---")

    # Financial Charts section
    st.markdown("## 📈 Financial Trends Analysis")
    _display_financial_charts(data, chart_gen)

    st.markdown("---")

    # Full statements sections
    st.markdown("## 📋 Financial Statements")

    # Tabs for different statements (without Company Info tab)
    tab1, tab2, tab3 = st.tabs(["Balance Sheet", "Income Statement", "Cash Flow"])

    with tab1:
        st.markdown("### Financial Statements")
        st.markdown("**Company Information**")
        _display_company_info(df_company)
        st.markdown("---")
        _display_balance_sheet(df_balance, chart_gen)

    with tab2:
        st.markdown("### Financial Statements")
        st.markdown("**Company Information**")
        _display_company_info(df_company)
        st.markdown("---")
        _display_income_statement(df_income, chart_gen)

    with tab3:
        st.markdown("### Financial Statements")
        st.markdown("**Company Information**")
        _display_company_info(df_company)
        st.markdown("---")
        _display_cash_flow_statement(df_cash_flow, chart_gen)

def _display_key_financial_variables(data: dict, chart_gen):
    """Display key financial variables table with observation years as columns"""
    df_income = data['income_info']
    df_balance = data['balance_sheet']

    if df_income is None or df_balance is None or df_income.empty or df_balance.empty:
        st.warning("No financial data available for key variables")
        return

    # Get observation years
    years_income = sorted(df_income['year'].unique()) if 'year' in df_income.columns else []
    years_balance = sorted(df_balance['year'].unique()) if 'year' in df_balance.columns else []
    observation_years = sorted(list(set(years_income + years_balance)))

    if len(observation_years) == 0:
        st.warning("No year data available")
        return

    # Define key variables mapping and calculations
    key_variables = {
        'Net Turnover': {'source': 'income', 'field': 'revenue'},
        'Non-Current Assets Total': {
            'source': 'balance',
            'calc': lambda df, year: (
                df[df['year'] == year]['ppe_net'].iloc[0] +
                df[df['year'] == year]['other_noncurrent_assets'].iloc[0]
            ) if not df[df['year'] == year].empty and
                pd.notna(df[df['year'] == year]['ppe_net'].iloc[0]) and
                pd.notna(df[df['year'] == year]['other_noncurrent_assets'].iloc[0]) else None
        },
        'Capital and Reserves Total': {'source': 'balance', 'field': 'equity_end'},
        'Liabilities': {'source': 'balance', 'field': 'total_liabilities'},
        'Profit after Tax': {'source': 'income', 'field': 'net_income'},
        'Operating Result': {'source': 'income', 'field': 'ebit'}
    }

    # Create DataFrame with years as columns
    df_display_data = []

    for var_name, var_config in key_variables.items():
        row = {'Variable': var_name}

        for year in observation_years:
            value = None

            if var_config['source'] == 'income':
                year_data = df_income[df_income['year'] == year]
                if not year_data.empty and var_config['field'] in year_data.columns:
                    value = year_data[var_config['field']].iloc[0]

            elif var_config['source'] == 'balance':
                if 'calc' in var_config:
                    # Use calculated field
                    value = var_config['calc'](df_balance, year)
                else:
                    # Use direct field
                    year_data = df_balance[df_balance['year'] == year]
                    if not year_data.empty and var_config['field'] in year_data.columns:
                        value = year_data[var_config['field']].iloc[0]

            row[str(year)] = value

  
        df_display_data.append(row)

    # Convert to DataFrame and display
    df_key_vars = pd.DataFrame(df_display_data)

    # Display as formatted table
    st.markdown("### Key Financial Variables Overview")

    # Create columns: Variable + observation years (no change column)
    num_years = len(observation_years)
    col_widths = [3] + [1.5] * num_years  # Variable column + year columns

    # Headers
    cols = st.columns(col_widths)
    with cols[0]:
        st.markdown("**Variable**")

    for i, year in enumerate(observation_years):
        with cols[i + 1]:
            st.markdown(f"**{year}**")

    st.markdown("---")

    # Data rows with deltas below values
    for _, row in df_key_vars.iterrows():
        # First row: Variable name and values
        cols = st.columns(col_widths)

        with cols[0]:
            st.markdown(f"**{row['Variable']}**")

        for i, year in enumerate(observation_years):
            with cols[i + 1]:
                value = row.get(str(year))
                if pd.notna(value):
                    st.markdown(f"{chart_gen.format_number(value, 0)}")
                else:
                    st.markdown("—")

        # Second row: Empty for variable name, delta indicators below values
        cols = st.columns(col_widths)
        with cols[0]:
            st.markdown("&nbsp;")  # Placeholder under variable name

        for i, year in enumerate(observation_years):
            with cols[i + 1]:
                if i == 0:
                    st.markdown("—")  # First year has no delta
                else:
                    prev_year = observation_years[i - 1]
                    current_val = row.get(str(year))
                    prev_val = row.get(str(prev_year))

                    if pd.notna(current_val) and pd.notna(prev_val) and prev_val != 0:
                        delta = ((current_val - prev_val) / prev_val) * 100
                        if delta > 0:
                            st.markdown(f"<small style='color:green'>↑ +{delta:.1f}%</small>", unsafe_allow_html=True)
                        elif delta < 0:
                            st.markdown(f"<small style='color:red'>↓ {abs(delta):.1f}%</small>", unsafe_allow_html=True)
                        else:
                            st.markdown("<small>→ 0.0%</small>", unsafe_allow_html=True)
                    else:
                        st.markdown("—")

        st.markdown("---")

def _display_financial_charts(data: dict, chart_gen):
    """Display financial trend charts"""
    df_income = data['income_info']
    df_balance = data['balance_sheet']

    if df_income is None or df_balance is None or df_income.empty or df_balance.empty:
        st.warning("No financial data available for charts")
        return

    # Get observation years
    years_income = sorted(df_income['year'].unique()) if 'year' in df_income.columns else []
    years_balance = sorted(df_balance['year'].unique()) if 'year' in df_balance.columns else []
    observation_years = sorted(list(set(years_income + years_balance)))

    if len(observation_years) < 2:
        st.info("Need at least 2 years of data for trend charts")
        return

    # Chart 1: Net Turnover vs Operating Result
    st.markdown("#### 📊 Revenue vs Operating Performance")
    col1, col2 = st.columns(2)

    with col1:
        # Line chart: Net Turnover vs Operating Result
        chart1_data = []
        for year in observation_years:
            revenue_val = None
            ebit_val = None

            year_income = df_income[df_income['year'] == year]
            if not year_income.empty:
                if 'revenue' in year_income.columns:
                    revenue_val = year_income['revenue'].iloc[0]
                if 'ebit' in year_income.columns:
                    ebit_val = year_income['ebit'].iloc[0]

            if pd.notna(revenue_val):
                chart1_data.append({
                    'Year': year,
                    'Net Turnover': revenue_val,
                    'Operating Result': ebit_val if pd.notna(ebit_val) else 0
                })

        if chart1_data:
            df_chart1 = pd.DataFrame(chart1_data)
            fig1 = chart_gen.create_multi_line_chart(
                df_chart1,
                x_col='Year',
                y_cols=['Net Turnover', 'Operating Result'],
                title='Net Turnover vs Operating Result Trend'
            )
            st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Line chart: Liabilities vs Total Receivables
        chart2_data = []
        for year in observation_years:
            liabilities_val = None
            receivables_val = None

            year_balance = df_balance[df_balance['year'] == year]
            if not year_balance.empty:
                if 'total_liabilities' in year_balance.columns:
                    liabilities_val = year_balance['total_liabilities'].iloc[0]
                if 'receivables' in year_balance.columns:
                    receivables_val = year_balance['receivables'].iloc[0]

            if pd.notna(liabilities_val):
                chart2_data.append({
                    'Year': year,
                    'Liabilities': liabilities_val,
                    'Total Receivables': receivables_val if pd.notna(receivables_val) else 0
                })

        if chart2_data:
            df_chart2 = pd.DataFrame(chart2_data)
            fig2 = chart_gen.create_multi_line_chart(
                df_chart2,
                x_col='Year',
                y_cols=['Liabilities', 'Total Receivables'],
                title='Liabilities vs Total Receivables Trend'
            )
            st.plotly_chart(fig2, use_container_width=True)

    # Chart 3: Non-Current Assets vs Current Assets (Clustered Bar Chart)
    st.markdown("#### 🏗️ Asset Structure Analysis")
    chart3_data = []

    for year in observation_years:
        non_current_assets = 0
        current_assets = 0

        year_balance = df_balance[df_balance['year'] == year]
        if not year_balance.empty:
            # Non-current assets
            ppe_net = year_balance['ppe_net'].iloc[0] if 'ppe_net' in year_balance.columns else 0
            other_noncurrent = year_balance['other_noncurrent_assets'].iloc[0] if 'other_noncurrent_assets' in year_balance.columns else 0
            non_current_assets = (ppe_net if pd.notna(ppe_net) else 0) + (other_noncurrent if pd.notna(other_noncurrent) else 0)

            # Current assets
            cash = year_balance['cash'].iloc[0] if 'cash' in year_balance.columns else 0
            receivables = year_balance['receivables'].iloc[0] if 'receivables' in year_balance.columns else 0
            inventory = year_balance['inventory'].iloc[0] if 'inventory' in year_balance.columns else 0
            other_current = year_balance['other_current_assets'].iloc[0] if 'other_current_assets' in year_balance.columns else 0
            current_assets = (
                (cash if pd.notna(cash) else 0) +
                (receivables if pd.notna(receivables) else 0) +
                (inventory if pd.notna(inventory) else 0) +
                (other_current if pd.notna(other_current) else 0)
            )

        chart3_data.append({
            'Year': year,
            'Non-Current Assets': non_current_assets,
            'Current Assets': current_assets
        })

    if chart3_data:
        df_chart3 = pd.DataFrame(chart3_data)
        fig3 = chart_gen.create_clustered_bar_chart(
            df_chart3,
            x_col='Year',
            y_cols=['Non-Current Assets', 'Current Assets'],
            title='Non-Current vs Current Assets Comparison'
        )
        st.plotly_chart(fig3, use_container_width=True)

def _display_company_info(df_company: pd.DataFrame):
    """Display company information with improved hierarchical layout"""
    if df_company is None or df_company.empty:
        st.info("No company information available")
        return

    st.markdown('<div class="metric-card" style="padding: 1.5rem;">', unsafe_allow_html=True)

    # Group information by category for better hierarchy
    company_info = {}
    for col in df_company.columns:
        if col != 'firm_id':
            value = df_company[col].iloc[0]
            if pd.notna(value):
                company_info[col] = value

    if company_info:
        # Primary company identification (top priority)
        primary_info = []
        if 'company_name' in company_info:
            primary_info.append(f"**{company_info['company_name']}**")
        if 'ticker_symbol' in company_info:
            primary_info.append(f"({company_info['ticker_symbol']})")

        if primary_info:
            st.markdown("### " + " ".join(primary_info))
            st.markdown("")

        # Core business information
        business_info = []
        if 'sector' in company_info:
            business_info.append(f"**Sector:** {company_info['sector']}")
        if 'industry' in company_info:
            business_info.append(f"**Industry:** {company_info['industry']}")
        if 'business_description' in company_info:
            business_info.append(f"**Description:** {company_info['business_description']}")

        if business_info:
            for info in business_info:
                st.markdown(info)
            st.markdown("")

        # Financial information
        financial_info = []
        if 'market_cap' in company_info:
            financial_info.append(f"**Market Cap:** {company_info['market_cap']}")
        if 'revenue' in company_info:
            financial_info.append(f"**Revenue:** {company_info['revenue']}")
        if 'employees' in company_info:
            financial_info.append(f"**Employees:** {company_info['employees']}")

        if financial_info:
            cols = st.columns(len(financial_info))
            for i, info in enumerate(financial_info):
                with cols[i]:
                    st.markdown(f"<div style='text-align: center; padding: 0.5rem; background-color: #f0f2f6; border-radius: 0.5rem;'>{info}</div>", unsafe_allow_html=True)
            st.markdown("")

        # Additional information
        additional_info = []
        remaining_keys = [k for k in company_info.keys() if k not in ['company_name', 'ticker_symbol', 'sector', 'industry', 'business_description', 'market_cap', 'revenue', 'employees']]

        for key in remaining_keys:
            additional_info.append(f"**{key.replace('_', ' ').title()}:** {company_info[key]}")

        if additional_info:
            with st.expander("Additional Information", expanded=False):
                for info in additional_info:
                    st.markdown(info)

    st.markdown('</div>', unsafe_allow_html=True)

def _display_balance_sheet(df_balance: pd.DataFrame, chart_gen):
    """Display balance sheet data with observation years as columns and delta percentages"""
    if df_balance is None or df_balance.empty:
        st.info("No balance sheet data available")
        return

    st.markdown('<div class="metric-card">', unsafe_allow_html=True)

    # Get observation years
    observation_years = sorted(df_balance['year'].unique())
    if len(observation_years) == 0:
        st.warning("No year data available")
        return

    # Filter numeric columns
    numeric_cols = df_balance.select_dtypes(include=[np.number]).columns.tolist()
    if 'year' in numeric_cols:
        numeric_cols.remove('year')
    if 'firm_id' in numeric_cols:
        numeric_cols.remove('firm_id')

    # Define exact variable order according to guidelines
    balance_sheet_variables = [
        'cash', 'receivables', 'inventory', 'other_current_assets', 'total_current_assets',
        'ppe_gross', 'accum_depreciation', 'ppe_net', 'other_noncurrent_assets', 'total_assets',
        'payables', 'other_current_liabilities', 'current_debt', 'total_current_liabilities',
        'long_term_debt', 'total_liabilities', 'equity_begin', 'dividends', 'equity_injection',
        'equity_end', 'total_liabilities_and_equity'
    ]

    # Create data structure for display using exact variable order
    balance_data = {}

    for var_name in balance_sheet_variables:
        if var_name in numeric_cols:
            display_name = var_name.replace('_', ' ').title()
            balance_data[display_name] = {}

            for year in observation_years:
                year_data = df_balance[df_balance['year'] == year]
                if not year_data.empty and var_name in year_data.columns:
                    value = year_data[var_name].iloc[0]
                    balance_data[display_name][str(year)] = value if pd.notna(value) else None
                else:
                    balance_data[display_name][str(year)] = None

    # Create column layout: Item + years (no change column)
    num_years = len(observation_years)
    col_widths = [3] + [1.2] * num_years  # Item column + year columns

    if balance_data:
        # Headers
        cols = st.columns(col_widths)
        with cols[0]:
            st.markdown("**Item**")
        for i, year in enumerate(observation_years):
            with cols[i + 1]:
                st.markdown(f"**{year}**")
        st.markdown("---")

        # Data rows with deltas below values (in specified order)
        for item_name, item_data in balance_data.items():
            # First row: Item name and values
            cols = st.columns(col_widths)

            with cols[0]:
                st.markdown(f"**{item_name}**")

            for i, year in enumerate(observation_years):
                with cols[i + 1]:
                    value = item_data.get(str(year))
                    if pd.notna(value):
                        st.markdown(f"{chart_gen.format_number(value, 0)}")
                    else:
                        st.markdown("—")

            # Second row: Empty for item name, delta indicators below values
            cols = st.columns(col_widths)
            with cols[0]:
                st.markdown("&nbsp;")  # Placeholder under item name

            for i, year in enumerate(observation_years):
                with cols[i + 1]:
                    if i == 0:
                        st.markdown("—")  # First year has no delta
                    else:
                        prev_year = observation_years[i - 1]
                        current_val = item_data.get(str(year))
                        prev_val = item_data.get(str(prev_year))

                        if pd.notna(current_val) and pd.notna(prev_val) and prev_val != 0:
                            delta = ((current_val - prev_val) / prev_val) * 100
                            if delta > 0:
                                st.markdown(f"<small style='color:green'>↑ +{delta:.1f}%</small>", unsafe_allow_html=True)
                            elif delta < 0:
                                st.markdown(f"<small style='color:red'>↓ {abs(delta):.1f}%</small>", unsafe_allow_html=True)
                            else:
                                st.markdown("<small>→ 0.0%</small>", unsafe_allow_html=True)
                        else:
                            st.markdown("—")

            st.markdown("---")

    st.markdown('</div>', unsafe_allow_html=True)

def _display_income_statement(df_income: pd.DataFrame, chart_gen):
    """Display income statement data with observation years as columns and delta percentages"""
    if df_income is None or df_income.empty:
        st.info("No income statement data available")
        return

    st.markdown('<div class="metric-card">', unsafe_allow_html=True)

    # Get observation years
    observation_years = sorted(df_income['year'].unique())
    if len(observation_years) == 0:
        st.warning("No year data available")
        return

    # Filter numeric columns
    numeric_cols = df_income.select_dtypes(include=[np.number]).columns.tolist()
    if 'year' in numeric_cols:
        numeric_cols.remove('year')
    if 'firm_id' in numeric_cols:
        numeric_cols.remove('firm_id')

    # Define exact variable order according to guidelines
    income_statement_variables = [
        'revenue', 'cogs', 'gross_profit', 'opex', 'ebitda', 'depreciation',
        'ebit', 'interest_expense', 'ebt', 'tax', 'net_income'
    ]

    # Create data structure for display using exact variable order
    income_data = {}

    for var_name in income_statement_variables:
        if var_name in numeric_cols:
            display_name = var_name.replace('_', ' ').title()
            income_data[display_name] = {}

            for year in observation_years:
                year_data = df_income[df_income['year'] == year]
                if not year_data.empty and var_name in year_data.columns:
                    value = year_data[var_name].iloc[0]
                    income_data[display_name][str(year)] = value if pd.notna(value) else None
                else:
                    income_data[display_name][str(year)] = None

    # Create column layout: Item + years (no change column)
    num_years = len(observation_years)
    col_widths = [3] + [1.2] * num_years  # Item column + year columns

    if income_data:
        # Headers
        cols = st.columns(col_widths)
        with cols[0]:
            st.markdown("**Item**")
        for i, year in enumerate(observation_years):
            with cols[i + 1]:
                st.markdown(f"**{year}**")
        st.markdown("---")

        # Data rows with deltas below values (in specified order)
        for item_name, item_data in income_data.items():
            # First row: Item name and values
            cols = st.columns(col_widths)

            with cols[0]:
                st.markdown(f"**{item_name}**")

            for i, year in enumerate(observation_years):
                with cols[i + 1]:
                    value = item_data.get(str(year))
                    if pd.notna(value):
                        st.markdown(f"{chart_gen.format_number(value, 0)}")
                    else:
                        st.markdown("—")

            # Second row: Empty for item name, delta indicators below values
            cols = st.columns(col_widths)
            with cols[0]:
                st.markdown("&nbsp;")  # Placeholder under item name

            for i, year in enumerate(observation_years):
                with cols[i + 1]:
                    if i == 0:
                        st.markdown("—")  # First year has no delta
                    else:
                        prev_year = observation_years[i - 1]
                        current_val = item_data.get(str(year))
                        prev_val = item_data.get(str(prev_year))

                        if pd.notna(current_val) and pd.notna(prev_val) and prev_val != 0:
                            delta = ((current_val - prev_val) / prev_val) * 100
                            if delta > 0:
                                st.markdown(f"<small style='color:green'>↑ +{delta:.1f}%</small>", unsafe_allow_html=True)
                            elif delta < 0:
                                st.markdown(f"<small style='color:red'>↓ {abs(delta):.1f}%</small>", unsafe_allow_html=True)
                            else:
                                st.markdown("<small>→ 0.0%</small>", unsafe_allow_html=True)
                        else:
                            st.markdown("—")

            st.markdown("---")

    st.markdown('</div>', unsafe_allow_html=True)

def _display_cash_flow_statement(df_cash_flow: pd.DataFrame, chart_gen):
    """Display cash flow statement data with observation years as columns and delta percentages"""
    if df_cash_flow is None or df_cash_flow.empty:
        st.info("No cash flow statement data available")
        return

    st.markdown('<div class="metric-card">', unsafe_allow_html=True)

    # Get observation years
    observation_years = sorted(df_cash_flow['year'].unique())
    if len(observation_years) == 0:
        st.warning("No year data available")
        return

    # Filter numeric columns
    numeric_cols = df_cash_flow.select_dtypes(include=[np.number]).columns.tolist()
    if 'year' in numeric_cols:
        numeric_cols.remove('year')
    if 'firm_id' in numeric_cols:
        numeric_cols.remove('firm_id')

    # Define exact variable order according to guidelines
    cash_flow_variables = [
        'net_income', 'depreciation', 'change_receivables', 'change_inventory', 'change_payables',
        'cash_flow_operations', 'capex', 'asset_disposal_proceeds', 'cash_flow_investing',
        'change_long_term_debt', 'change_current_debt', 'equity_injection', 'dividends_paid',
        'cash_flow_financing', 'net_cash_flow', 'cash_beginning', 'cash_ending'
    ]

    # Create column layout: Item + years (no change column)
    num_years = len(observation_years)
    col_widths = [3] + [1.2] * num_years  # Item column + year columns

    # Create data structure for display using exact variable order
    cash_flow_data = {}

    for var_name in cash_flow_variables:
        if var_name in numeric_cols:
            display_name = var_name.replace('_', ' ').title()
            cash_flow_data[display_name] = {}

            for year in observation_years:
                year_data = df_cash_flow[df_cash_flow['year'] == year]
                if not year_data.empty and var_name in year_data.columns:
                    value = year_data[var_name].iloc[0]
                    cash_flow_data[display_name][str(year)] = value if pd.notna(value) else None
                else:
                    cash_flow_data[display_name][str(year)] = None

    if cash_flow_data:
        # Headers
        cols = st.columns(col_widths)
        with cols[0]:
            st.markdown("**Item**")
        for i, year in enumerate(observation_years):
            with cols[i + 1]:
                st.markdown(f"**{year}**")
        st.markdown("---")

        # Data rows with deltas below values (in specified order)
        for item_name, item_data in cash_flow_data.items():
            # First row: Item name and values
            cols = st.columns(col_widths)

            with cols[0]:
                st.markdown(f"**{item_name}**")

            for i, year in enumerate(observation_years):
                with cols[i + 1]:
                    value = item_data.get(str(year))
                    if pd.notna(value):
                        st.markdown(f"{chart_gen.format_number(value, 0)}")
                    else:
                        st.markdown("—")

            # Second row: Empty for item name, delta indicators below values
            cols = st.columns(col_widths)
            with cols[0]:
                st.markdown("&nbsp;")  # Placeholder under item name

            for i, year in enumerate(observation_years):
                with cols[i + 1]:
                    if i == 0:
                        st.markdown("—")  # First year has no delta
                    else:
                        prev_year = observation_years[i - 1]
                        current_val = item_data.get(str(year))
                        prev_val = item_data.get(str(prev_year))

                        if pd.notna(current_val) and pd.notna(prev_val) and prev_val != 0:
                            delta = ((current_val - prev_val) / prev_val) * 100
                            if delta > 0:
                                st.markdown(f"<small style='color:green'>↑ +{delta:.1f}%</small>", unsafe_allow_html=True)
                            elif delta < 0:
                                st.markdown(f"<small style='color:red'>↓ {abs(delta):.1f}%</small>", unsafe_allow_html=True)
                            else:
                                st.markdown("<small>→ 0.0%</small>", unsafe_allow_html=True)
                        else:
                            st.markdown("—")

            st.markdown("---")

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