"""AI & ML Based Adaptive Traffic Control System - Primary Dashboard Entry Point."""

import os
import sys
from pathlib import Path

# Ensure 'src' is on Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st
from traffic_ai.dashboard.theme import apply_theme
from traffic_ai.dashboard.pages import (
    p01_operations,
    p02_intersection,
    p03_controller,
    p04_perception,
    p05_scenario_lab,
    p06_training,
    p07_benchmarks,
    p08_analytics,
    p09_registry,
    p10_system_health,
    p11_documentation,
)

# Configure Streamlit page
st.set_page_config(
    page_title="AI & ML Based Adaptive Traffic Control System",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply operations-console dark theme
apply_theme()

# Global Sidebar Header
st.sidebar.markdown(
    """
    <div style='padding: 8px 0px 16px 0px; border-bottom: 1px solid #1F2937; margin-bottom: 16px;'>
        <div style='font-size: 1.05rem; font-weight: 800; color: #F9FAFB; letter-spacing: -0.02em;'>
            ADAPTIVE <span style='color: #06B6D4;'>|</span> TRAFFIC AI
        </div>
        <div style='font-size: 0.70rem; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;'>
            Simulation · Perception · Control
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Observation Mode Selector
obs_mode = st.sidebar.selectbox(
    "Observation Mode",
    ["Ground Truth (Direct TraCI)", "Vision (YOLO Pipeline)", "Hybrid (Vision + Ground Truth)"],
    index=0,
    help="Select source of sensory data for controller decisions",
)

st.sidebar.markdown(
    "<div style='margin-bottom: 16px;'><span class='badge-sim'>SIMULATION ONLY</span> "
    "<span class='badge-cyan'>SUMO v1.27.1</span></div>",
    unsafe_allow_html=True,
)

# Navigation Menu
nav_options = [
    "1. Operations Overview",
    "2. Live Intersection",
    "3. AI Controller",
    "4. Camera & Perception",
    "5. Scenario Lab",
    "6. Training Center",
    "7. Experiments & Benchmarking",
    "8. Analytics & Reports",
    "9. Model Registry",
    "10. System Health & Diagnostics",
    "11. Documentation & About",
]

selected_page = st.sidebar.radio("Navigation", nav_options, index=0)

st.sidebar.markdown("---")
st.sidebar.caption("AI & ML Based Adaptive Traffic Control System")

# Page Dispatcher
if selected_page.startswith("1."):
    p01_operations.render_page()
elif selected_page.startswith("2."):
    p02_intersection.render_page()
elif selected_page.startswith("3."):
    p03_controller.render_page()
elif selected_page.startswith("4."):
    p04_perception.render_page()
elif selected_page.startswith("5."):
    p05_scenario_lab.py if False else p05_scenario_lab.render_page()
elif selected_page.startswith("6."):
    p06_training.render_page()
elif selected_page.startswith("7."):
    p07_benchmarks.render_page()
elif selected_page.startswith("8."):
    p08_analytics.render_page()
elif selected_page.startswith("9."):
    p09_registry.render_page()
elif selected_page.startswith("10."):
    p10_system_health.render_page()
elif selected_page.startswith("11."):
    p11_documentation.render_page()
