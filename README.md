# Credit Financial Risk Analysis System

A comprehensive end-to-end credit risk assessment system that transforms raw financial data into actionable credit decisions. This project combines automated data processing, explainable AI, and interactive dashboarding to provide financial institutions with fast, consistent, and transparent credit analysis capabilities.

## 🎯 Project Overview

This system addresses the critical need for automated, explainable, and reliable credit risk assessment in financial lending. It provides a complete pipeline from raw financial data to credit decisions, featuring:

- **Automated Data Processing**: Handles missing values, validates data integrity, and calculates 25+ financial ratios
- **Explainable Credit Scoring**: 7-aspect scoring framework with quantitative reasoning and AI-powered insights
- **Interactive Dashboard**: Professional Streamlit interface for credit analysts and decision-makers
- **Regulatory Compliance**: Complete audit trail and documented decision rationale

## 📊 System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Raw Data      │───▶│  Data Processing  │───▶│ Credit Analysis │
│                 │    │                  │    │                 │
│ • Company Info  │    │ • Data Cleaning  │    │ • Ratio Calc    │
│ • Financial Stmts│   │ • Validation     │    │ • Trend Analysis│
│ • Historical Data│   │ • Transformation │    │ • Scoring       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Dashboard     │◀───│   AI Insights    │◀───│ Credit Decisions│
│                 │    │                  │    │                 │
│ • Visualizations│    │ • Gemini API      │    │ • Classification │
│ • Reports       │    │ • Professional   │    │ • Recommendations│
│ • Export        │    │   Analysis       │    │ • Risk Assessment│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Streamlit
- Processed credit analysis data (see Data Requirements below)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd credit-financial-risk-analysis

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run app.py
```

### Access Points
- **Dashboard**: http://localhost:8501
- **Analysis Notebooks**: `/notebooks/` directory
- **Documentation**: See below for detailed reports

## 📁 Project Structure

```
credit-financial-risk-analysis/
├── 📊 notebooks/                          # Data analysis notebooks
│   ├── credit_financial_cleaning_analysis.ipynb
│   └── credit_financial_risk_data_transformation.ipynb
├── 🖥️ dashboard/                          # Streamlit application
│   ├── app.py                            # Main application
│   ├── requirements.txt                  # Dependencies
│   ├── utils/                            # Utility modules
│   │   ├── data_loader.py               # Data loading & validation
│   │   └── charts.py                    # Chart generation
│   └── pages/                            # Dashboard pages
│       ├── analysis_summary.py           # Main credit overview
│       ├── performance_insight.py        # Metrics deep-dive
│       ├── ratio_explorer.py             # Financial ratios
│       └── financials_explorer.py        # Raw statements
├── 📄 documentation/                      # Project documentation
│   ├── problem_definition.md             # Project background & solution
│   ├── data_catalogue.md                 # Variable definitions
│   ├── data-cleaning-report.md           # Cleaning process
│   ├── data-transformation-report.md     # Transformation pipeline
│   └── dashboard-credit-financial-risk.md # Dashboard documentation
├── 📁 data/                              # Data files (external)
│   ├── df_credit_score.csv               # Final credit scores
│   ├── df_agg.csv                        # Aggregated metrics
│   ├── df_ratios.csv                     # Yearly ratios
│   └── [supporting files]                # Additional datasets
└── 📋 README.md                          # This file
```

## 📚 Documentation Navigation

### 🎯 [Problem Definition](problem_definition.md)
**Project Background & Solution Framework**
- Industry challenges in credit assessment
- Comprehensive problem analysis
- Proposed solution methodology
- Success metrics and business impact

### 📋 [Data Catalogue](data_catalogue.md)
**Complete Variable Reference**
- Raw data file structures
- Variable definitions and business meanings
- Data relationships and dependencies
- Industry context and usage guidelines

### 🧹 [Data Cleaning Report](data-cleaning-report.md)
**Data Quality Enhancement Process**
- Initial data quality assessment
- Cleaning methodology and rules applied
- Validation and quality assurance
- Final dataset quality metrics

### 🔄 [Data Transformation Report](data-transformation-report.md)
**Financial Analysis Pipeline**
- Ratio calculation methodology
- Multi-year aggregation framework
- Credit scoring algorithms
- AI enrichment integration

### 📊 [Dashboard Documentation](dashboard-credit-financial-risk.md)
**Interactive Analysis Interface**
- Complete feature documentation
- User interface design principles
- Technical architecture details
- Deployment and operations guide

## 🔬 Analysis Notebooks

### Data Processing Pipeline
1. **[Data Cleaning](notebooks/credit_financial_cleaning_analysis.ipynb)**
   - Raw data validation and quality assessment
   - Missing value handling and data reconstruction
   - Logical consistency checks and validation

2. **[Data Transformation](notebooks/credit_financial_risk_data_transformation.ipynb)**
   - Financial ratio calculations (25+ ratios)
   - Multi-year trend analysis
   - Credit scoring and classification
   - AI-powered insights generation

## 🎛️ Dashboard Features

### 📈 Analysis Summary
- **Comprehensive Credit Overview**: Final scores, categories, and recommendations
- **Interactive Visualizations**: Radar charts and contribution analysis
- **AI-Powered Insights**: Professional analyst explanations
- **Detailed Aspect Breakdown**: 7-aspect scoring with reasoning

### 🔍 Performance Insight Deck
- **Advanced Metrics Exploration**: Searchable aggregated metrics
- **Trend Analysis**: Historical performance patterns
- **Rule-Based Interpretations**: Automated metric explanations
- **Comparative Analysis**: Industry benchmarking

### 🧮 Ratio Explorer
- **Comprehensive Ratio Coverage**: 25+ financial ratios
- **Category Organization**: Liquidity, Solvency, Profitability, Activity, Coverage, Cash Flow
- **Historical Trends**: Multi-year performance visualization
- **Professional Interpretations**: Industry-standard analysis

### 💰 Financial Statements
- **Raw Data Access**: Complete financial statement exploration
- **Trend Analysis**: Year-over-year performance changes
- **Company Context**: Demographic and operational information
- **Cross-Statement Analysis**: Integrated financial view

## ⚙️ Technical Features

### Credit Scoring Framework
- **7-Aspect Assessment**: Liquidity, Solvency, Profitability, Activity, Coverage, Cash Flow, Structure
- **Multi-Dimensional Analysis**: Current position + Trend + Stability
- **Explainable Methodology**: Quantitative reasoning for all scores
- **AI Enhancement**: Professional insights via Gemini API

### Data Processing Capabilities
- **Automated Cleaning**: Handles missing values and inconsistencies
- **Vectorized Calculations**: High-performance ratio computations
- **Quality Assurance**: Comprehensive validation and error handling
- **Audit Trail**: Complete documentation of all transformations

### Dashboard Technology
- **Modern Interface**: Streamlit-based responsive design
- **Interactive Visualizations**: Plotly charts with professional styling
- **Real-time Analysis**: Dynamic calculations and filtering
- **Export Capabilities**: Professional report generation

## 📊 Data Requirements

### Core Processed Files
- `df_credit_score.csv` - Final credit assessment results
- `df_agg.csv` - Aggregated financial metrics with trends
- `df_ratios.csv` - Yearly financial ratios
- `company_info_sub.csv` - Company demographic data
- `balance_sheet_sub.csv` - Balance sheet history
- `income_info_sub.csv` - Income statement history
- `cash_flow_sub.csv` - Cash flow statement history

### Data Quality Standards
- Minimum 3 years of historical data per company
- Complete financial statement coverage
- Validated mathematical relationships
- Consistent formatting and units

## 🎯 Business Impact

### Operational Benefits
- **80% Reduction** in analysis time per application
- **3-4x Increase** in processing capacity
- **Consistent Application** of credit standards across all analysts
- **Complete Documentation** for regulatory compliance

### Quality Improvements
- **7-Aspect Coverage** prevents analytical blind spots
- **Explainable AI** provides transparent decision rationale
- **Trend Analysis** identifies emerging risks early
- **Standardized Methodology** ensures consistent evaluation

### Strategic Value
- **Faster Decision-Making** improves customer experience
- **Better Risk Assessment** reduces credit losses
- **Regulatory Compliance** ensures audit readiness
- **Scalable Platform** supports business growth

## 🔒 Security & Compliance

### Data Protection
- Secure data handling practices
- Audit trail for all calculations and decisions
- User access control and authentication
- Data encryption and privacy protection

### Regulatory Alignment
- SOX compliance considerations
- Basel III risk assessment standards
- Complete documentation for audit purposes
- Transparent decision-making processes

## 🚀 Future Enhancements

### Advanced Analytics
- Machine learning integration for predictive modeling
- Portfolio-level analysis and aggregation
- Stress testing and scenario analysis
- Real-time risk monitoring capabilities

### System Extensions
- Multi-company comparison features
- API integration with core banking systems
- Mobile application development
- Enterprise-scale deployment options

## 📞 Support & Contact

### Documentation Issues
- Report documentation problems via GitHub issues
- Request additional documentation sections
- Suggest improvements to clarity and completeness

### Technical Support
- Review notebooks for detailed methodology understanding
- Check data requirements for compatibility
- Consult individual documentation files for specific questions

---

## 🏁 Getting Started Checklist

1. **Review Documentation**: Start with [Problem Definition](problem_definition.md)
2. **Understand Data**: Review [Data Catalogue](data_catalogue.md)
3. **Learn Process**: Study [Data Cleaning](data-cleaning-report.md) and [Transformation](data-transformation-report.md) reports
4. **Explore Dashboard**: Read [Dashboard Documentation](dashboard-credit-financial-risk.md)
5. **Install System**: Follow installation instructions above
6. **Prepare Data**: Ensure all required data files are available
7. **Launch Dashboard**: Run `streamlit run app.py` and explore features

**Transform your credit analysis process from manual, time-consuming work to efficient, data-driven decision-making with our comprehensive credit risk assessment system.**