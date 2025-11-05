import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

class ChartGenerator:
    """Generates various charts for the credit analysis dashboard"""

    def __init__(self):
        # Color scheme for status mapping
        self.status_colors = {
            'Strong': '#22c55e',      # green
            'Good': '#84cc16',        # lime
            'Moderate': '#eab308',    # yellow
            'Watch': '#f97316',       # orange
            'Weak': '#ef4444',        # red
            'Poor': '#dc2626'         # dark red
        }

        self.default_color = '#6b7280'  # gray for unknown status

    def create_radar_chart(self, df_credit_score: pd.DataFrame) -> go.Figure:
        """Create radar chart for 7 aspect scores"""
        if df_credit_score is None or df_credit_score.empty:
            return go.Figure()

        row = df_credit_score.iloc[0]
        aspects = ['Liquidity', 'Solvency', 'Profitability', 'Activity', 'Coverage', 'Cashflow', 'Structure']
        scores = [
            row['liquidity_score'], row['solvency_score'], row['profitability_score'],
            row['activity_score'], row['coverage_score'], row['cashflow_score'], row['structure_score']
        ]

        # Close the radar chart
        aspects.append(aspects[0])
        scores.append(scores[0])

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=scores,
            theta=aspects,
            fill='toself',
            name='Scores',
            line_color='#2563eb',
            fillcolor='rgba(37, 99, 235, 0.2)',
            hovertemplate='<b>%{theta}</b><br>Score: %{r:.1f}<extra></extra>'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    ticksuffix=''
                )
            ),
            showlegend=False,
            height=400,
            margin=dict(l=20, r=20, t=20, b=20)
        )

        return fig

    def create_aspect_bar_chart(self, contributions_df: pd.DataFrame) -> go.Figure:
        """Create horizontal bar chart for aspect contributions"""
        if contributions_df.empty:
            return go.Figure()

        # Color bars by status
        colors = [self.status_colors.get(status, self.default_color) for status in contributions_df['status']]

        # Combine weight and contribution data into customdata
        customdata_combined = np.column_stack((
            contributions_df['weight'] * 100,  # Weight as percentage
            contributions_df['contribution']   # Contribution
        ))

        fig = go.Figure(data=[
            go.Bar(
                y=contributions_df['aspect'],
                x=contributions_df['score'],
                orientation='h',
                marker_color=colors,
                text=contributions_df.apply(lambda row: f"{row['score']:.1f} ({row['weight']*100:.0f}%)", axis=1),
                textposition='auto',
                hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}<br>Weight: %{customdata[0]:.0f}%<br>Contribution: %{customdata[1]:.1f}<extra></extra>',
                customdata=customdata_combined
            )
        ])

        fig.update_layout(
            title='Aspect Scores (Sorted by Contribution)',
            xaxis_title='Score (0-100)',
            yaxis_title='',
            height=400,
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(range=[0, 100])
        )

        return fig

    def create_trend_chart(self, df_ratios: pd.DataFrame, metric_name: str) -> go.Figure:
        """Create line chart for ratio trends"""
        if df_ratios is None or df_ratios.empty or metric_name not in df_ratios.columns:
            return go.Figure()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_ratios['year'],
            y=df_ratios[metric_name],
            mode='lines+markers',
            name=metric_name,
            line=dict(color='#2563eb', width=2),
            marker=dict(size=6),
            hovertemplate=f'<b>{metric_name}</b><br>Year: %{{x}}<br>Value: %{{y:.2f}}<extra></extra>'
        ))

        fig.update_layout(
            xaxis_title='Year',
            yaxis_title='Value',
            height=300,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=False
        )

        return fig

    def create_sparkline(self, df_ratios: pd.DataFrame, metric_name: str) -> go.Figure:
        """Create small sparkline for trend visualization"""
        if df_ratios is None or df_ratios.empty or metric_name not in df_ratios.columns:
            return go.Figure()

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=df_ratios['year'],
            y=df_ratios[metric_name],
            mode='lines',
            line=dict(color='#6b7280', width=1),
            showlegend=False,
            hoverinfo='none'
        ))

        # Highlight last point
        if not df_ratios.empty:
            last_point = df_ratios.iloc[-1]
            fig.add_trace(go.Scatter(
                x=[last_point['year']],
                y=[last_point[metric_name]],
                mode='markers',
                marker=dict(color='#2563eb', size=4),
                showlegend=False,
                hoverinfo='none'
            ))

        fig.update_layout(
            height=60,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
        )

        return fig

    def format_number(self, value: float, decimal_places: int = 2) -> str:
        """Format numbers with thousands separator"""
        if pd.isna(value):
            return "N/A"
        try:
            return f"{value:,.{decimal_places}f}"
        except:
            return str(value)

    def get_trend_indicator(self, current: float, previous: float) -> tuple:
        """Get trend indicator and color"""
        if pd.isna(current) or pd.isna(previous):
            return "–", "#6b7280"

        diff = current - previous
        pct_change = (diff / previous) * 100 if previous != 0 else 0

        if diff > 0:
            return f"▲ {abs(diff):.2f} ({abs(pct_change):.1f}%)", "#22c55e"
        elif diff < 0:
            return f"▼ {abs(diff):.2f} ({abs(pct_change):.1f}%)", "#ef4444"
        else:
            return "– 0.00 (0.0%)", "#6b7280"

    def create_multi_line_chart(self, df: pd.DataFrame, x_col: str, y_cols: list, title: str) -> go.Figure:
        """Create a multi-line chart for comparing multiple metrics"""
        if df.empty or not y_cols:
            return go.Figure()

        fig = go.Figure()

        colors = ['#2563eb', '#dc2626', '#16a34a', '#ca8a04', '#9333ea', '#ea580c']

        for i, col in enumerate(y_cols):
            if col in df.columns:
                fig.add_trace(go.Scatter(
                    x=df[x_col],
                    y=df[col],
                    mode='lines+markers',
                    name=col,
                    line=dict(color=colors[i % len(colors)], width=2),
                    marker=dict(size=6),
                    hovertemplate=f'<b>{col}</b><br>{x_col}: %{{x}}<br>Value: %{{y:,.0f}}<extra></extra>'
                ))

        fig.update_layout(
            title=title,
            xaxis_title=x_col.title(),
            yaxis_title='Value',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        return fig

    def create_clustered_bar_chart(self, df: pd.DataFrame, x_col: str, y_cols: list, title: str) -> go.Figure:
        """Create a clustered bar chart for comparing multiple categories"""
        if df.empty or not y_cols:
            return go.Figure()

        fig = go.Figure()

        colors = ['#2563eb', '#dc2626', '#16a34a', '#ca8a04', '#9333ea', '#ea580c']

        for i, col in enumerate(y_cols):
            if col in df.columns:
                fig.add_trace(go.Bar(
                    x=df[x_col],
                    y=df[col],
                    name=col,
                    marker_color=colors[i % len(colors)],
                    hovertemplate=f'<b>{col}</b><br>{x_col}: %{{x}}<br>Value: %{{y:,.0f}}<extra></extra>'
                ))

        fig.update_layout(
            title=title,
            xaxis_title=x_col.title(),
            yaxis_title='Value',
            height=300,
            margin=dict(l=20, r=20, t=40, b=20),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            barmode='group'
        )

        return fig