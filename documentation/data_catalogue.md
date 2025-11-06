# Data Catalogue

## Overview

This catalogue provides detailed information about all variables in the raw financial datasets used for credit analysis. The data consists of four main files containing company information and financial statements.

## Data Files Structure

### 1. Company Information (`company_info.csv`)
Basic company demographic and operational data.

| Column Name | Data Type | Description | Example Values |
|-------------|-----------|-------------|----------------|
| **firm_id** | String | Unique identifier for each company (Primary Key) | F000001, F000002 |
| **sector** | String | Industry sector classification | Jasa, Retail, Konstruksi, Manufaktur, F&B |
| **region** | String | Geographic region of operation | Kalimantan, Jawa, Sumatera, Papua_Maluku, Sulawesi, Bali_NusaTenggara |
| **start_year** | Integer | Year when company was established or started operations | 1990, 2000, 2021 |

### 2. Income Statement (`income_statement.csv`)
Comprehensive income and expense data reflecting company profitability.

| Column Name | Data Type | Description | Business Meaning |
|-------------|-----------|-------------|------------------|
| **firm_id** | String | Foreign key linking to company information | Company identifier |
| **year** | Integer | Fiscal year of the financial data | 2018, 2019, 2020, 2021, 2022 |
| **revenue** | Float | Total sales revenue from primary business operations | Top-line sales figure |
| **cogs** | Float | Cost of Goods Sold - direct costs of producing goods | Cost of materials and labor |
| **gross_profit** | Float | Revenue minus Cost of Goods Sold | Profit after direct costs |
| **opex** | Float | Operating Expenses - selling, general & administrative costs | Day-to-day business expenses |
| **ebitda** | Float | Earnings Before Interest, Taxes, Depreciation & Amortization | Operating cash flow proxy |
| **depreciation** | Float | Depreciation expense - allocation of asset costs | Non-cash expense for asset wear |
| **ebit** | Float | Earnings Before Interest and Taxes | Operating profitability |
| **interest_expense** | Float | Interest paid on debt obligations | Cost of borrowing |
| **ebt** | Float | Earnings Before Tax | Pre-tax profitability |
| **tax** | Float | Income tax expense | Government tax burden |
| **net_income** | Float | Net Income/Loss - bottom-line profit | Final profit after all expenses |

### 3. Balance Sheet (`balance_sheet.csv`)
Snapshot of company's financial position at specific points in time.

| Column Name | Data Type | Description | Business Meaning |
|-------------|-----------|-------------|------------------|
| **firm_id** | String | Foreign key linking to company information | Company identifier |
| **year** | Integer | Fiscal year end date | Financial reporting period |
| **cash** | Float | Cash and cash equivalents | Most liquid assets |
| **receivables** | Float | Accounts receivable - money owed by customers | Credit sales to customers |
| **inventory** | Float | Inventory - goods held for sale | Raw materials and finished goods |
| **other_current_assets** | Float | Other current assets not classified elsewhere | Short-term assets |
| **total_current_assets** | Float | Total current assets (cash + receivables + inventory + other) | Assets convertible to cash within 1 year |
| **ppe_gross** | Float | Property, Plant & Equipment at gross value | Fixed assets before depreciation |
| **accum_depreciation** | Float | Accumulated depreciation on PPE | Total depreciation to date |
| **ppe_net** | Float | Net Property, Plant & Equipment (gross - accumulated) | Fixed assets at net value |
| **other_noncurrent_assets** | Float | Other non-current assets | Long-term assets |
| **total_assets** | Float | Total assets (current + non-current) | Company's total resources |
| **payables** | Float | Accounts payable - money owed to suppliers | Credit from suppliers |
| **other_current_liabilities** | Float | Other current liabilities | Short-term obligations |
| **current_debt** | Float | Current portion of long-term debt | Debt due within 1 year |
| **total_current_liabilities** | Float | Total current liabilities | Obligations due within 1 year |
| **long_term_debt** | Float | Long-term debt obligations | Debt due beyond 1 year |
| **total_liabilities** | Float | Total liabilities (current + long-term) | Total obligations |
| **equity_begin** | Float | Shareholders' equity at beginning of period | Opening equity balance |
| **dividends** | Float | Dividends paid to shareholders | Profit distribution |
| **equity_injection** | Float | Additional equity invested by owners | Capital contributions |
| **equity_end** | Float | Shareholders' equity at end of period | Closing equity balance |
| **total_liabilities_and_equity** | Float | Total liabilities and equity | Balance sheet total (should equal total assets) |

### 4. Cash Flow Statement (`cash_flow_statement.csv`)
Detailed cash movement analysis showing sources and uses of cash.

| Column Name | Data Type | Description | Business Meaning |
|-------------|-----------|-------------|------------------|
| **firm_id** | String | Foreign key linking to company information | Company identifier |
| **year** | Integer | Fiscal year of cash flow data | Cash flow reporting period |
| **net_income** | Float | Net income from income statement | Starting point for cash flow |
| **depreciation** | Float | Depreciation expense (non-cash adjustment) | Add-back to net income |
| **change_receivables** | Float | Change in accounts receivable | Working capital impact |
| **change_inventory** | Float | Change in inventory levels | Working capital impact |
| **change_payables** | Float | Change in accounts payable | Working capital impact |
| **cash_flow_operations** | Float | Net cash flow from operating activities | Cash generated from core business |
| **capex** | Float | Capital expenditures - spending on fixed assets | Investment in property, plant, equipment |
| **asset_disposal_proceeds** | Float | Proceeds from selling assets | Cash from asset sales |
| **cash_flow_investing** | Float | Net cash flow from investing activities | Cash used for investments |
| **change_long_term_debt** | Float | Change in long-term debt | Financing activities |
| **change_current_debt** | Float | Change in current debt | Short-term borrowing changes |
| **equity_injection** | Float | Equity capital raised | Owner investments |
| **dividends_paid** | Float | Dividends actually paid in cash | Cash outflows to shareholders |
| **cash_flow_financing** | Float | Net cash flow from financing activities | Cash from/used for financing |
| **net_cash_flow** | Float | Net change in cash (operations + investing + financing) | Overall cash movement |
| **cash_beginning** | Float | Cash balance at beginning of period | Opening cash position |
| **cash_ending** | Float | Cash balance at end of period | Closing cash position |

## Data Relationships

### Primary Key-Foreign Key Relationships
- **firm_id** serves as the primary key in `company_info.csv` and foreign key in all other files
- **year** provides temporal dimension across all financial statement files
- Each combination of (firm_id, year) represents a unique financial reporting period

### Logical Data Flow
1. **Company Information** provides static company demographics
2. **Income Statement** shows performance over the year (flow statement)
3. **Balance Sheet** provides position snapshot at year-end (stock statement)
4. **Cash Flow Statement** explains cash movements during the year (reconciliation)

## Business Context and Usage

### Credit Analysis Relevance

**Liquidity Assessment Variables:**
- Current assets, current liabilities, cash, receivables
- Used to calculate current ratio, quick ratio, cash ratio

**Solvency Analysis Variables:**
- Total debt, total assets, equity, long-term obligations
- Used to calculate debt-to-equity, debt-to-assets ratios

**Profitability Metrics:**
- Revenue, expenses, net income, margins
- Used to assess earnings power and sustainability

**Operational Efficiency:**
- Inventory levels, receivables, payables
- Used to calculate working capital cycles

**Cash Flow Quality:**
- Operating cash flow vs. net income
- Used to assess earnings quality

### Data Quality Considerations

**Completeness:**
- All files should have complete (firm_id, year) combinations
- Missing values may occur in specific financial line items

**Consistency:**
- Balance sheet equation: Assets = Liabilities + Equity
- Cash flow reconciliation: Beginning cash + Net change = Ending cash
- Income statement and retained earnings relationship

**Temporal Consistency:**
- Year-over-year data should show logical progression
- Large year-to-year changes may indicate data quality issues

## Industry Standards for Variables

**Revenue Recognition:**
- Should represent gross sales before returns and allowances
- Consistent with company's revenue recognition policies

**Asset Valuation:**
- PPE at historical cost less accumulated depreciation
- Inventory at lower of cost or market value

**Debt Classification:**
- Current debt: obligations due within 12 months
- Long-term debt: obligations due beyond 12 months

**Equity Presentation:**
- Beginning equity + Net Income - Dividends + Equity Injection = Ending Equity

## Data Usage Guidelines

**Analysis Scope:**
- Minimum 3 years of data required for trend analysis
- Maximum 5 years recommended for current assessment
- Outlier years should be investigated and potentially excluded

**Ratio Calculations:**
- All financial ratios derived from these raw variables
- Industry comparisons require sector-specific benchmarks
- Trend analysis requires consistent year-over-year data

**Quality Validation:**
- Verify balance sheet equation balance
- Check cash flow statement reconciliation
- Validate income statement arithmetic
- Cross-check related variables across statements