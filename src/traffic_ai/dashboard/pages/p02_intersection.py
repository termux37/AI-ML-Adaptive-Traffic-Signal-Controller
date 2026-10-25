"""Page 2: Live Intersection - Physical and topological junction geometry inspector."""

import streamlit as st
import plotly.graph_objects as go
from traffic_ai.control.phase_catalog import PhaseCatalog
from traffic_ai.dashboard.theme import ACCENT_CYAN, CARD_BG, get_plotly_layout


def render_page():
    st.markdown("## 🗺️ Live Intersection Topology")
    st.markdown(
        "<span class='badge-sim'>SIMULATION ONLY</span> "
        "<span class='badge-cyan'>JUNCTION ID: junction_center · 4-WAY CONFIG</span>",
        unsafe_allow_html=True,
    )
    st.write("")

    col_view, col_info = st.columns([2, 1])

    with col_view:
        st.markdown("### Top-Down Junction Schematic")

        # Interactive schematic diagram using Plotly
        fig = go.Figure()

        # Draw roads
        # North-South road (x from -15 to +15, y from -120 to +120)
        fig.add_shape(type="rect", x0=-15, x1=15, y0=-120, y1=120, fillcolor="#1f242d", line=dict(color="#374151", width=2))
        # East-West road (x from -120 to +120, y from -15 to +15)
        fig.add_shape(type="rect", x0=-120, x1=120, y0=-15, y1=15, fillcolor="#1f242d", line=dict(color="#374151", width=2))

        # Center intersection area
        fig.add_shape(type="rect", x0=-15, x1=15, y0=-15, y1=15, fillcolor="#282f3c", line=dict(color="#4b5563", width=1, dash="dot"))

        # Yellow center division lines
        fig.add_shape(type="line", x0=0, x1=0, y0=15, y1=120, line=dict(color="#f59e0b", width=2, dash="dash"))
        fig.add_shape(type="line", x0=0, x1=0, y0=-120, y1=-15, line=dict(color="#f59e0b", width=2, dash="dash"))
        fig.add_shape(type="line", x0=-120, x1=-15, y0=0, y1=0, line=dict(color="#f59e0b", width=2, dash="dash"))
        fig.add_shape(type="line", x0=15, x1=120, y0=0, y1=0, line=dict(color="#f59e0b", width=2, dash="dash"))

        # Stop lines (Solid White)
        fig.add_shape(type="line", x0=-15, x1=0, y0=15, y1=15, line=dict(color="#ffffff", width=3))   # North stop
        fig.add_shape(type="line", x0=0, x1=15, y0=-15, y1=-15, line=dict(color="#ffffff", width=3)) # South stop
        fig.add_shape(type="line", x0=15, x1=15, y0=0, y1=15, line=dict(color="#ffffff", width=3))   # East stop
        fig.add_shape(type="line", x0=-15, x1=-15, y0=-15, y1=0, line=dict(color="#ffffff", width=3)) # West stop

        # Detectors (Stopline & Advance)
        det_x = [-7.5, -7.5, 7.5, 7.5, 25, 60, -25, -60]
        det_y = [25, 60, -25, -60, 7.5, 7.5, -7.5, -7.5]
        det_labels = [
            "det_stop_n", "det_adv_n", "det_stop_s", "det_adv_s",
            "det_stop_e", "det_adv_e", "det_stop_w", "det_adv_w"
        ]

        fig.add_trace(go.Scatter(
            x=det_x, y=det_y, mode="markers+text",
            marker=dict(size=9, color="#06b6d4", symbol="square"),
            text=det_labels, textposition="top center",
            name="Induction Loops",
        ))

        # Signal head markers
        fig.add_trace(go.Scatter(
            x=[-18, 18, 18, -18],
            y=[18, -18, 18, -18],
            mode="markers+text",
            marker=dict(size=14, color="#10b981", line=dict(color="#ffffff", width=1.5)),
            text=["TLS North", "TLS South", "TLS East", "TLS West"],
            textposition="bottom center",
            name="Signal Heads",
        ))

        fig.update_layout(
            paper_bgcolor="rgba(17, 24, 39, 0)",
            plot_bgcolor="rgba(22, 30, 46, 0.6)",
            xaxis=dict(range=[-130, 130], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[-130, 130], showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x"),
            height=500,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

        st.plotly_chart(fig, use_container_width=True)

    with col_info:
        st.markdown("### 🔍 Approach Inspector")
        app_selected = st.selectbox("Inspect Approach", ["North (edge_n2c)", "South (edge_s2c)", "East (edge_e2c)", "West (edge_w2c)"])

        st.markdown(
            """
            <div class='kpi-card'>
                <div class='kpi-label'>Geometry Specifications</div>
                <div style='color: #F9FAFB; font-size: 0.85rem; line-height: 1.6;'>
                    • <b>Approach Length:</b> 250.0 meters<br>
                    • <b>Number of Incoming Lanes:</b> 2<br>
                    • <b>Number of Outgoing Lanes:</b> 2<br>
                    • <b>Lane Width:</b> 3.20 meters<br>
                    • <b>Speed Limit:</b> 50 km/h (13.89 m/s)<br>
                    • <b>Stopline Position:</b> 239.60 m from entry<br>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 🔀 Movement Allocation")
        st.markdown(
            """
            • <b>Lane 0 (Outer / Right):</b> Through Movement + Protected Right Turn<br>
            • <b>Lane 1 (Inner / Left):</b> Through Movement + Protected Left Turn<br>
            • <b>Right Turn Policy:</b> Compatible with through traffic<br>
            • <b>Left Turn Policy:</b> Exclusive protected phase (no permissive conflicts)
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 🔒 Conflict Prevention")
        st.info("The Deterministic Safety Manager maintains an explicit zero-conflict matrix. Simultaneous greens for conflicting directions (e.g. NS and EW) are impossible by construction.")
