import pandas as pd
import os
from typing import Dict, Optional

class DataLoader:
    """Handles loading and validation of credit analysis data files"""

    def __init__(self, data_path: str = "./data/"):
        self.data_path = data_path
        self.required_credit_columns = [
            'firm_id', 'liquidity_score', 'liquidity_reason', 'liquidity_status',
            'solvency_score', 'solvency_reason', 'solvency_status',
            'profitability_score', 'profitability_reason', 'profitability_status',
            'activity_score', 'activity_reason', 'activity_status',
            'coverage_score', 'coverage_reason', 'coverage_status',
            'cashflow_score', 'cashflow_reason', 'cashflow_status',
            'structure_score', 'structure_reason', 'structure_status',
            'final_score', 'kategori', 'rekomendasi', 'reasoning',
            'liquidity_analysis', 'solvency_analysis', 'profitability_analysis',
            'activity_analysis', 'coverage_analysis', 'cashflow_analysis',
            'structure_analysis', 'genai_recommendation'
        ]

        self.aspect_weights = {
            'liquidity': 0.15,
            'solvency': 0.15,
            'profitability': 0.20,
            'activity': 0.10,
            'coverage': 0.10,
            'cashflow': 0.15,
            'structure': 0.15
        }

        self.aspect_scores = [
            'liquidity_score', 'solvency_score', 'profitability_score',
            'activity_score', 'coverage_score', 'cashflow_score', 'structure_score'
        ]

        self.aspect_statuses = [
            'liquidity_status', 'solvency_status', 'profitability_status',
            'activity_status', 'coverage_status', 'cashflow_status', 'structure_status'
        ]

        self.aspect_reasons = [
            'liquidity_reason', 'solvency_reason', 'profitability_reason',
            'activity_reason', 'coverage_reason', 'cashflow_reason', 'structure_reason'
        ]

        self.aspect_analyses = [
            'liquidity_analysis', 'solvency_analysis', 'profitability_analysis',
            'activity_analysis', 'coverage_analysis', 'cashflow_analysis', 'structure_analysis'
        ]

    def load_data(self) -> Dict[str, Optional[pd.DataFrame]]:
        """Load all required data files"""
        data_files = {
            'credit_score': 'df_credit_score.csv',
            'agg': 'df_agg.csv',
            'ratios': 'df_ratios.csv',
            'company_info': 'company_info_sub.csv',
            'balance_sheet': 'balance_sheet_sub.csv',
            'income_info': 'income_info_sub.csv',
            'cash_flow': 'cash_flow_sub.csv'
        }

        loaded_data = {}

        for key, filename in data_files.items():
            filepath = os.path.join(self.data_path, filename)
            try:
                if os.path.exists(filepath):
                    loaded_data[key] = pd.read_csv(filepath)
                else:
                    print(f"Warning: File {filename} not found at {filepath}")
                    loaded_data[key] = None
            except Exception as e:
                print(f"Error loading {filename}: {str(e)}")
                loaded_data[key] = None

        return loaded_data

    def get_current_firm_id(self, df_credit_score: pd.DataFrame) -> str:
        """Get the current firm_id from credit score data"""
        if df_credit_score is not None and not df_credit_score.empty:
            return str(df_credit_score['firm_id'].iloc[0])
        return "Unknown"

    def validate_credit_data(self, df: pd.DataFrame) -> bool:
        """Basic validation of credit score data"""
        if df is None or df.empty:
            return False
        return all(col in df.columns for col in self.required_credit_columns)

    def get_aspect_contributions(self, df_credit_score: pd.DataFrame) -> pd.DataFrame:
        """Calculate contribution of each aspect to final score"""
        if df_credit_score is None or df_credit_score.empty:
            return pd.DataFrame()

        row = df_credit_score.iloc[0]
        contributions = []

        aspects = ['liquidity', 'solvency', 'profitability', 'activity', 'coverage', 'cashflow', 'structure']

        for aspect in aspects:
            score = row[f'{aspect}_score']
            weight = self.aspect_weights[aspect]
            contribution = score * weight

            contributions.append({
                'aspect': aspect.capitalize(),
                'score': score,
                'weight': weight,
                'contribution': contribution,
                'status': row[f'{aspect}_status'],
                'reason': row[f'{aspect}_reason']
            })

        df_contrib = pd.DataFrame(contributions)
        df_contrib = df_contrib.sort_values('contribution', ascending=False)
        return df_contrib

    def get_key_financial_variables(self, df_ratios: pd.DataFrame, df_balance: pd.DataFrame,
                                   df_income: pd.DataFrame) -> Dict:
        """Extract key financial variables for summary"""
        variables = {}

        if df_ratios is not None and not df_ratios.empty:
            latest_year = df_ratios['year'].max()
            latest_data = df_ratios[df_ratios['year'] == latest_year]

            if not latest_data.empty:
                variables.update({
                    'net_turnover': latest_data.iloc[0].get('revenue', None),
                    'current_ratio': latest_data.iloc[0].get('current_ratio', None),
                    'roa': latest_data.iloc[0].get('roa', None),
                    'debt_to_equity': latest_data.iloc[0].get('debt_to_equity', None)
                })

        return variables