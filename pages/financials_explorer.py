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

    # Display company info above tabs
    st.markdown("### 🏢 Company Information")
    _display_company_info(df_company)

    with tab1:
        _display_balance_sheet(df_balance, chart_gen)

    with tab2:
        _display_income_statement(df_income, chart_gen)

    with tab3:
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

        # Calculate YoY change percentage
        if len(observation_years) >= 2:
            current_val = row.get(str(observation_years[-1]))
            prev_val = row.get(str(observation_years[-2]))

            if pd.notna(current_val) and pd.notna(prev_val) and prev_val != 0:
                change_pct = ((current_val - prev_val) / prev_val) * 100
                row['Change %'] = change_pct
            else:
                row['Change %'] = None

        df_display_data.append(row)

    # Convert to DataFrame and display
    df_key_vars = pd.DataFrame(df_display_data)

    # Display as formatted table
    st.markdown("### Key Financial Variables Overview")

    # Create columns: Variable + observation years + change %
    num_years = len(observation_years)
    col_widths = [3] + [1.5] * num_years + [1]  # Variable column + year columns + change column

    cols = st.columns(col_widths)

    # Headers
    with cols[0]:
        st.markdown("**Variable**")

    for i, year in enumerate(observation_years):
        with cols[i + 1]:
            st.markdown(f"**{year}**")

    with cols[-1]:
        st.markdown("**Change %**")

    st.markdown("---")

    # Data rows
    for _, row in df_key_vars.iterrows():
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

        with cols[-1]:
            change_pct = row.get('Change %')
            if pd.notna(change_pct):
                if change_pct > 0:
                    st.markdown(f"📈 +{change_pct:.1f}%")
                elif change_pct < 0:
                    st.markdown(f"📉 {change_pct:.1f}%")
                else:
                    st.markdown("➡️ 0.0%")
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

    # Sort columns logically
    priority_items = {
        'Assets': ['cash', 'receivable', 'inventory', 'other_current', 'current_assets', 'ppe_net', 'other_noncurrent', 'non_current_assets', 'total_assets'],
        'Liabilities': ['short_term_debt', 'accounts_payable', 'other_current_liabilities', 'current_liabilities', 'long_term_debt', 'total_liabilities'],
        'Equity': ['equity_end', 'capital', 'reserves', 'retained_earnings', 'total_equity']
    }

    # Create data structure for display
    balance_data = {}

    for col in numeric_cols:
        display_name = col.replace('_', ' ').title()
        balance_data[display_name] = {}

        for year in observation_years:
            year_data = df_balance[df_balance['year'] == year]
            if not year_data.empty and col in year_data.columns:
                value = year_data[col].iloc[0]
                balance_data[display_name][str(year)] = value if pd.notna(value) else None
            else:
                balance_data[display_name][str(year)] = None

        # Calculate YoY change percentages
        if len(observation_years) >= 2:
            current_val = balance_data[display_name].get(str(observation_years[-1]))
            prev_val = balance_data[display_name].get(str(observation_years[-2]))

            if pd.notna(current_val) and pd.notna(prev_val) and prev_val != 0:
                change_pct = ((current_val - prev_val) / prev_val) * 100
                balance_data[display_name]['Change %'] = change_pct
            else:
                balance_data[display_name]['Change %'] = None

    # Create column layout: Item + years + change %
    num_years = len(observation_years)
    col_widths = [3] + [1.2] * num_years + [1]  # Item column + year columns + change column

    # Display by categories
    for category, keywords in priority_items.items():
        category_items = {}

        # Find items that match category keywords
        for display_name in balance_data.keys():
            if any(keyword in display_name.lower() for keyword in keywords):
                category_items[display_name] = balance_data[display_name]

        if category_items:
            st.markdown(f"### 📊 {category}")

            # Headers
            cols = st.columns(col_widths)
            with cols[0]:
                st.markdown("**Item**")
            for i, year in enumerate(observation_years):
                with cols[i + 1]:
                    st.markdown(f"**{year}**")
            with cols[-1]:
                st.markdown("**Change %**")
            st.markdown("---")

            # Data rows
            for item_name, item_data in category_items.items():
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

                with cols[-1]:
                    change_pct = item_data.get('Change %')
                    if pd.notna(change_pct):
                        if change_pct > 0:
                            st.markdown(f"📈 +{change_pct:.1f}%")
                        elif change_pct < 0:
                            st.markdown(f"📉 {change_pct:.1f}%")
                        else:
                            st.markdown("➡️ 0.0%")
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

    # Sort by typical income statement order
    priority_order = [
        'revenue', 'sales', 'turnover',
        'cost', 'cogs', 'cost_of_goods',
        'gross', 'gross_profit', 'gross_margin',
        'operating', 'ebit', 'operating_income',
        'interest', 'interest_expense', 'interest_income',
        'tax', 'tax_expense',
        'net', 'net_income', 'profit', 'earnings'
    ]

    # Create data structure for display
    income_data = {}

    # Sort columns by priority
    sorted_cols = []
    for priority in priority_order:
        matches = [col for col in numeric_cols if priority in col.lower()]
        sorted_cols.extend(matches)

    # Add remaining columns
    remaining_cols = [col for col in numeric_cols if col not in sorted_cols]
    sorted_cols.extend(remaining_cols)

    for col in sorted_cols:
        display_name = col.replace('_', ' ').title()
        income_data[display_name] = {}

        for year in observation_years:
            year_data = df_income[df_income['year'] == year]
            if not year_data.empty and col in year_data.columns:
                value = year_data[col].iloc[0]
                income_data[display_name][str(year)] = value if pd.notna(value) else None
            else:
                income_data[display_name][str(year)] = None

        # Calculate YoY change percentages
        if len(observation_years) >= 2:
            current_val = income_data[display_name].get(str(observation_years[-1]))
            prev_val = income_data[display_name].get(str(observation_years[-2]))

            if pd.notna(current_val) and pd.notna(prev_val) and prev_val != 0:
                change_pct = ((current_val - prev_val) / prev_val) * 100
                income_data[display_name]['Change %'] = change_pct
            else:
                income_data[display_name]['Change %'] = None

    # Create column layout: Item + years + change %
    num_years = len(observation_years)
    col_widths = [3] + [1.2] * num_years + [1]  # Item column + year columns + change column

    # Headers
    cols = st.columns(col_widths)
    with cols[0]:
        st.markdown("**Item**")
    for i, year in enumerate(observation_years):
        with cols[i + 1]:
            st.markdown(f"**{year}**")
    with cols[-1]:
        st.markdown("**Change %**")
    st.markdown("---")

    # Data rows
    for item_name, item_data in income_data.items():
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

        with cols[-1]:
            change_pct = item_data.get('Change %')
            if pd.notna(change_pct):
                if change_pct > 0:
                    st.markdown(f"📈 +{change_pct:.1f}%")
                elif change_pct < 0:
                    st.markdown(f"📉 {change_pct:.1f}%")
                else:
                    st.markdown("➡️ 0.0%")
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

    # Group by cash flow categories
    operating_cols = [col for col in numeric_cols if any(x in col.lower() for x in ['operating', 'ocf', 'working'])]
    investing_cols = [col for col in numeric_cols if any(x in col.lower() for x in ['investing', 'icapex', 'capex'])]
    financing_cols = [col for col in numeric_cols if any(x in col.lower() for x in ['financing', 'dividend', 'stock'])]

    # Create column layout: Item + years + change %
    num_years = len(observation_years)
    col_widths = [3] + [1.2] * num_years + [1]  # Item column + year columns + change column

    # Helper function to display a category
    def _display_cash_flow_category(category_name, cols_list):
        if not cols_list:
            return

        st.markdown(f"### 📊 {category_name}")

        # Headers
        cols = st.columns(col_widths)
        with cols[0]:
            st.markdown("**Item**")
        for i, year in enumerate(observation_years):
            with cols[i + 1]:
                st.markdown(f"**{year}**")
        with cols[-1]:
            st.markdown("**Change %**")
        st.markdown("---")

        # Data rows
        for col in cols_list:
            display_name = col.replace('_', ' ').title()
            item_data = {}

            for year in observation_years:
                year_data = df_cash_flow[df_cash_flow['year'] == year]
                if not year_data.empty and col in year_data.columns:
                    value = year_data[col].iloc[0]
                    item_data[str(year)] = value if pd.notna(value) else None
                else:
                    item_data[str(year)] = None

            # Calculate YoY change percentages
            if len(observation_years) >= 2:
                current_val = item_data.get(str(observation_years[-1]))
                prev_val = item_data.get(str(observation_years[-2]))

                if pd.notna(current_val) and pd.notna(prev_val) and prev_val != 0:
                    change_pct = ((current_val - prev_val) / prev_val) * 100
                    item_data['Change %'] = change_pct
                else:
                    item_data['Change %'] = None

            # Display row
            cols = st.columns(col_widths)

            with cols[0]:
                st.markdown(f"**{display_name}**")

            for i, year in enumerate(observation_years):
                with cols[i + 1]:
                    value = item_data.get(str(year))
                    if pd.notna(value):
                        st.markdown(f"{chart_gen.format_number(value, 0)}")
                    else:
                        st.markdown("—")

            with cols[-1]:
                change_pct = item_data.get('Change %')
                if pd.notna(change_pct):
                    if change_pct > 0:
                        st.markdown(f"📈 +{change_pct:.1f}%")
                    elif change_pct < 0:
                        st.markdown(f"📉 {change_pct:.1f}%")
                    else:
                        st.markdown("➡️ 0.0%")
                else:
                    st.markdown("—")

            st.markdown("---")

    # Display Operating Cash Flow
    _display_cash_flow_category("Operating Cash Flow", operating_cols)

    # Display Investing Cash Flow
    _display_cash_flow_category("Investing Cash Flow", investing_cols)

    # Display Financing Cash Flow
    _display_cash_flow_category("Financing Cash Flow", financing_cols)

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