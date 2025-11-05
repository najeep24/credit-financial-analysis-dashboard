#!/usr/bin/env python3
"""
Simple test script to validate the customdata fix in charts.py
"""
import sys
import os
import pandas as pd
import numpy as np

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_chart_creation():
    """Test that the chart creation works without customdata2 error"""
    try:
        # Import the fixed ChartGenerator
        from utils.charts import ChartGenerator

        # Create test data similar to what would be used
        test_data = pd.DataFrame({
            'aspect': ['Liquidity', 'Profitability', 'Solvency'],
            'score': [85.5, 72.3, 68.9],
            'weight': [0.25, 0.35, 0.40],
            'contribution': [21.4, 25.3, 27.6],
            'status': ['Strong', 'Good', 'Moderate']
        })

        # Create chart generator and attempt to create bar chart
        chart_gen = ChartGenerator()
        fig = chart_gen.create_aspect_bar_chart(test_data)

        print("✅ Chart creation successful!")
        print(f"   - Chart has {len(fig.data)} traces")
        print(f"   - Customdata shape: {fig.data[0].customdata.shape}")
        print(f"   - Customdata sample: {fig.data[0].customdata[0]}")

        # Test hovertemplate format
        hovertemplate = fig.data[0].hovertemplate
        if 'customdata[0]' in hovertemplate and 'customdata[1]' in hovertemplate:
            print("✅ Hovertemplate uses correct customdata indexing")
        else:
            print("❌ Hovertemplate doesn't use correct customdata indexing")
            return False

        return True

    except Exception as e:
        print(f"❌ Error creating chart: {e}")
        return False

if __name__ == "__main__":
    success = test_chart_creation()
    sys.exit(0 if success else 1)