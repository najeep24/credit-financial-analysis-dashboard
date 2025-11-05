import streamlit as st
import pandas as pd
from utils.data_loader import DataLoader
from utils.charts import ChartGenerator

# Page imports
from pages.analysis_summary import show_analysis_summary
from pages.ratio_explorer import show_ratio_explorer
from pages.financials_explorer import show_financials_explorer

# Configure page
st.set_page_config(
    page_title="Credit Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1e40af 0%, #3b82f6 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        margin-bottom: 1rem;
    }

    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .status-strong { color: #22c55e; font-weight: 600; }
    .status-moderate { color: #eab308; font-weight: 600; }
    .status-watch { color: #f97316; font-weight: 600; }
    .status-weak { color: #ef4444; font-weight: 600; }

    .aspect-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e5e7eb;
        margin-bottom: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .score-display {
        font-size: 3rem;
        font-weight: bold;
        color: #1e40af;
    }

    .recommendation-box {
        background: #f0f9ff;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 0.25rem;
    }

    .genai-recommendation {
        background: #f0fdf4;
        border-left: 4px solid #22c55e;
        padding: 1rem;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

def load_data():
    """Load data and store in session state"""
    if 'data_loaded' not in st.session_state:
        with st.spinner("Loading data..."):
            data_loader = DataLoader()
            data = data_loader.load_data()

            # Check if main data file exists
            if data['credit_score'] is None:
                st.error("❌ Dataset tidak ditemukan. Pastikan file berada di folder yang benar.")
                st.stop()

            # Store in session state
            st.session_state.data_loader = data_loader
            st.session_state.data = data
            st.session_state.current_firm = data_loader.get_current_firm_id(data['credit_score'])
            st.session_state.data_loaded = True

def main():
    """Main application"""
    # Load data
    load_data()

    # Get data from session state
    data_loader = st.session_state.data_loader
    data = st.session_state.data
    current_firm = st.session_state.current_firm

    # Sidebar
    with st.sidebar:
        st.title("📊 Credit Analysis Dashboard")

        # Firm selector (though we only have one)
        if data['credit_score'] is not None:
            st.info(f"📁 Current Firm: **{current_firm}**")

        st.markdown("---")

        # Navigation
        page = st.selectbox(
            "Navigate to:",
            [
                "📈 Analysis Summary",
                "🧮 Sub-Ratio Explorer",
                "💰 Financial Statements"
            ],
            index=0
        )

    # Main content
    if page == "📈 Analysis Summary":
        show_analysis_summary(data_loader, data, current_firm)
    elif page == "🧮 Sub-Ratio Explorer":
        show_ratio_explorer(data_loader, data, current_firm)
    elif page == "💰 Financial Statements":
        show_financials_explorer(data_loader, data, current_firm)

if __name__ == "__main__":
    main()