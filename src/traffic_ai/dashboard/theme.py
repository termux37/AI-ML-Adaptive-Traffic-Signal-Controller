"""Custom dark operations-console design system and styling."""

import streamlit as st
import plotly.graph_objects as go
import plotly.io as pio

# Color Palette: Deep graphite / operations console
DARK_BG = "#0B0F19"
PANEL_BG = "#111827"
CARD_BG = "#161E2E"
BORDER_COL = "#1F2937"
TEXT_PRIMARY = "#F9FAFB"
TEXT_MUTED = "#9CA3AF"
ACCENT_CYAN = "#06B6D4"
ACCENT_TEAL = "#14B8A6"
STATUS_GREEN = "#10B981"
STATUS_AMBER = "#F59E0B"
STATUS_RED = "#EF4444"


def apply_theme():
    """Injects high-density dark theme CSS into the Streamlit app."""
    custom_css = f"""
    <style>
        /* Base page styling */
        .stApp {{
            background-color: {DARK_BG};
            color: {TEXT_PRIMARY};
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background-color: {PANEL_BG};
            border-right: 1px solid {BORDER_COL};
        }}
        
        /* Metric cards */
        [data-testid="stMetricValue"] {{
            color: {ACCENT_CYAN} !important;
            font-size: 1.6rem !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }}
        [data-testid="stMetricLabel"] {{
            color: {TEXT_MUTED} !important;
            font-size: 0.78rem !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }}
        
        /* Custom KPI Card */
        .kpi-card {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER_COL};
            border-radius: 6px;
            padding: 12px 16px;
            margin-bottom: 8px;
        }}
        .kpi-label {{
            color: {TEXT_MUTED};
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
            margin-bottom: 4px;
        }}
        .kpi-value {{
            color: {TEXT_PRIMARY};
            font-size: 1.4rem;
            font-weight: 700;
        }}
        .kpi-subtext {{
            color: {ACCENT_CYAN};
            font-size: 0.75rem;
            font-weight: 500;
            margin-top: 2px;
        }}
        
        /* Status Badges */
        .badge-sim {{
            background-color: #1e293b;
            color: #94a3b8;
            border: 1px solid #334155;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            display: inline-block;
        }}
        .badge-green {{
            background-color: rgba(16, 185, 129, 0.15);
            color: {STATUS_GREEN};
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            display: inline-block;
        }}
        .badge-amber {{
            background-color: rgba(245, 158, 11, 0.15);
            color: {STATUS_AMBER};
            border: 1px solid rgba(245, 158, 11, 0.3);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            display: inline-block;
        }}
        .badge-cyan {{
            background-color: rgba(6, 182, 212, 0.15);
            color: {ACCENT_CYAN};
            border: 1px solid rgba(6, 182, 212, 0.3);
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: 600;
            display: inline-block;
        }}

        /* Buttons */
        .stButton>button {{
            background-color: #1F2937;
            color: {TEXT_PRIMARY};
            border: 1px solid {BORDER_COL};
            border-radius: 4px;
            font-weight: 600;
            font-size: 0.85rem;
            transition: all 0.15s ease-in-out;
        }}
        .stButton>button:hover {{
            background-color: #374151;
            border-color: {ACCENT_CYAN};
            color: {ACCENT_CYAN};
        }}

        /* Header styling */
        h1, h2, h3, h4 {{
            color: {TEXT_PRIMARY} !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }}
        h1 {{ font-size: 1.6rem !important; }}
        h2 {{ font-size: 1.3rem !important; }}
        h3 {{ font-size: 1.1rem !important; }}
        
        /* Table / Dataframe styling */
        .stDataFrame {{
            background-color: {CARD_BG};
            border: 1px solid {BORDER_COL};
            border-radius: 6px;
        }}
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def get_plotly_layout(title: str = "", height: int = 320) -> dict:
    """Standardized Plotly dark layout conforming to operations console theme."""
    return dict(
        title=dict(
            text=title,
            font=dict(size=14, color=TEXT_PRIMARY, family="sans-serif"),
            x=0.01,
            y=0.96,
        ),
        paper_bgcolor="rgba(17, 24, 39, 0)",
        plot_bgcolor="rgba(22, 30, 46, 0.6)",
        font=dict(color=TEXT_MUTED, size=11),
        margin=dict(l=40, r=20, t=35, b=35),
        height=height,
        hovermode="x unified",
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(31, 41, 55, 0.8)",
            linecolor=BORDER_COL,
            tickfont=dict(size=10, color=TEXT_MUTED),
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(31, 41, 55, 0.8)",
            linecolor=BORDER_COL,
            tickfont=dict(size=10, color=TEXT_MUTED),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10, color=TEXT_MUTED),
        ),
    )
