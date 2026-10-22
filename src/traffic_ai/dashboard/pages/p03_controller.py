"""Page 3: AI Controller - Algorithm state, safety validation, and observation vector."""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from traffic_ai.control.phase_catalog import PhaseCatalog
from traffic_ai.dashboard.data_access import load_model_metadata
from traffic_ai.dashboard.theme import ACCENT_CYAN, CARD_BG, STATUS_AMBER, STATUS_GREEN, get_plotly_layout


def render_page():
    st.markdown("## 🧠 AI Controller & Safety Manager")
    st.markdown(
        "<span class='badge-sim'>SIMULATION ONLY</span> "
        "<span class='badge-green'>DETERMINISTIC SAFETY GUARD ACTIVE</span>",
        unsafe_allow_html=True,
    )
    st.write("")

    col_meta, col_obs = st.columns([1, 1])

    with col_meta:
        st.markdown("### 🎛️ Active Controller Architecture")

        ctrl_type = st.radio(
            "Selected Controller Type",
            ["DQN (Learned Reinforcement Learning)", "Max-Pressure (Heuristic Optimization)", "Actuated (Vehicle-Responsive)", "Fixed-Time (Pre-timed Baseline)"],
            index=0,
        )

        st.markdown(
            """
            <div class='kpi-card'>
                <div class='kpi-label'>Safety Manager Constraints</div>
                <div style='color: #F9FAFB; font-size: 0.85rem; line-height: 1.6;'>
                    • <b>Minimum Green:</b> 10.0 seconds (strict enforcement)<br>
                    • <b>Maximum Green:</b> 60.0 seconds (starvation prevention)<br>
                    • <b>Yellow Clearance:</b> 3.0 seconds (mandatory transition)<br>
                    • <b>All-Red Clearance:</b> 2.0 seconds (total clearance)<br>
                    • <b>Arbitrary strings:</b> Prohibited. Agent proposals are filtered.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 📜 Reward Formulation (DQN)")
        st.markdown(
            r"""
            $$r_t = w_q \Delta Q + w_w \frac{\Delta W}{10} + w_t \Delta Thr - w_s \mathbb{I}_{switch} - w_{starv} \frac{\max(0, W_{max} - 60)}{60}$$
            """,
            unsafe_allow_html=True,
        )
        st.caption("Balanced reward accounting for total queue burden, trip throughput, switching penalty, and maximum single-vehicle wait starvation.")

        meta = load_model_metadata()
        if meta:
            st.markdown("### 💾 Checkpoint Metadata")
            st.json(meta)

    with col_obs:
        st.markdown("### 📊 25-Dimensional Observation Inspector")
        st.caption("Normalized continuous feature vector fed into the DQN policy network.")

        # Synthetic/live observation features representation
        feature_names = [
            "N_count", "N_queue", "N_speed", "N_wait", "N_occ",
            "S_count", "S_queue", "S_speed", "S_wait", "S_occ",
            "E_count", "E_queue", "E_speed", "E_wait", "E_occ",
            "W_count", "W_queue", "W_speed", "W_wait", "W_occ",
            "Phase_0_NS_Thru", "Phase_1_NS_Left", "Phase_2_EW_Thru", "Phase_3_EW_Left",
            "Normalized_Green_Timer"
        ]

        # Illustrative real-scale normalized vector
        sample_obs = [
            0.23, 0.15, 0.72, 0.08, 0.12,
            0.45, 0.38, 0.40, 0.22, 0.25,
            0.10, 0.05, 0.85, 0.02, 0.06,
            0.18, 0.12, 0.65, 0.05, 0.10,
            1.00, 0.00, 0.00, 0.00,
            0.42
        ]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=sample_obs,
            y=feature_names,
            orientation="h",
            marker=dict(
                color=["#06b6d4" if i < 20 else "#10b981" if i < 24 else "#f59e0b" for i in range(25)],
            ),
        ))
        fig.update_layout(
            paper_bgcolor="rgba(17, 24, 39, 0)",
            plot_bgcolor="rgba(22, 30, 46, 0.6)",
            height=580,
            margin=dict(l=150, r=20, t=10, b=30),
            xaxis=dict(range=[0, 1.05], title="Normalized Value [0.0 - 1.0]"),
            yaxis=dict(autorange="reversed"),
        )
        st.plotly_chart(fig, use_container_width=True)
