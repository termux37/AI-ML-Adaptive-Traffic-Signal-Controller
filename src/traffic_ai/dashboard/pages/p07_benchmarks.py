"""Page 7: Experiments & Benchmarking - Multi-controller empirical evaluation."""

import json
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from traffic_ai.dashboard.data_access import load_benchmark_data
from traffic_ai.dashboard.theme import ACCENT_CYAN, CARD_BG, STATUS_AMBER, STATUS_GREEN, get_plotly_layout
from traffic_ai.experiments.runner import BenchmarkRunner
from traffic_ai.config.schemas import ScenarioName


def render_page():
    st.markdown("## 📊 Experiments & Benchmarking")
    st.markdown(
        "<span class='badge-sim'>SIMULATION ONLY</span> "
        "<span class='badge-cyan'>EMPIRICAL COMPARISON · IDENTICAL SEEDS</span>",
        unsafe_allow_html=True,
    )
    st.write("")

    col_btn1, col_btn2 = st.columns([1, 3])
    with col_btn1:
        if st.button("🚀 Run Full Benchmark Suite", use_container_width=True):
            with st.spinner("Executing benchmark across all controllers and scenarios..."):
                runner = BenchmarkRunner()
                runner.run_benchmark(
                    scenarios=[ScenarioName.BALANCED, ScenarioName.NORTH_SOUTH_DOMINANT],
                    controllers=["fixed_time", "actuated", "max_pressure", "dqn"],
                    seeds=[101],
                    duration_seconds=90,
                )
                st.success("Benchmark completed and cached!")
                st.rerun()

    df = load_benchmark_data()

    if df is not None and not df.empty:
        # Filter controls
        scenarios = df["scenario"].unique().tolist()
        selected_scenario = st.selectbox("Filter by Demand Scenario", scenarios, index=0)
        filtered_df = df[df["scenario"] == selected_scenario]

        st.markdown(f"### 📋 Benchmark Results for `{selected_scenario}`")
        st.dataframe(filtered_df, use_container_width=True)

        # Comparative Plotly Charts
        ch1, ch2 = st.columns(2)

        with ch1:
            fig_thr = go.Figure()
            fig_thr.add_trace(go.Bar(
                x=filtered_df["controller"],
                y=filtered_df["throughput_vph"],
                marker_color=["#94a3b8", "#38bdf8", "#34d399", "#a78bfa"],
            ))
            fig_thr.update_layout(get_plotly_layout(title="Throughput (Vehicles / Hour) - Higher is Better", height=300))
            st.plotly_chart(fig_thr, use_container_width=True)

        with ch2:
            fig_q = go.Figure()
            fig_q.add_trace(go.Bar(
                x=filtered_df["controller"],
                y=filtered_df["average_queue"],
                marker_color=["#f87171", "#fbbf24", "#34d399", "#818cf8"],
            ))
            fig_q.update_layout(get_plotly_layout(title="Average Queue Length (Vehicles) - Lower is Better", height=300))
            st.plotly_chart(fig_q, use_container_width=True)

        # Baseline Relative Improvement Table
        st.markdown("### 📈 Relative Improvement vs Fixed-Time Baseline")
        fixed_time_row = filtered_df[filtered_df["controller"] == "fixed_time"]
        if not fixed_time_row.empty:
            base_thr = fixed_time_row["throughput_vph"].iloc[0]
            base_q = fixed_time_row["average_queue"].iloc[0]
            base_wait = fixed_time_row["average_wait_s"].iloc[0]

            improvements = []
            for _, r in filtered_df.iterrows():
                ctrl = r["controller"]
                # For throughput: (proposed - baseline) / baseline * 100
                thr_imp = round(((r["throughput_vph"] - base_thr) / base_thr) * 100.0, 1) if base_thr > 0 else 0.0
                # For queue: (baseline - proposed) / baseline * 100
                q_imp = round(((base_q - r["average_queue"]) / base_q) * 100.0, 1) if base_q > 0 else 0.0
                # For wait: (baseline - proposed) / baseline * 100
                w_imp = round(((base_wait - r["average_wait_s"]) / base_wait) * 100.0, 1) if base_wait > 0 else 0.0

                improvements.append({
                    "Controller": ctrl,
                    "Throughput Improvement (%)": f"{thr_imp:+.1f}%",
                    "Queue Reduction (%)": f"{q_imp:+.1f}%",
                    "Waiting Time Reduction (%)": f"{w_imp:+.1f}%",
                    "Fairness Index": f"{r['fairness_index']:.2f}",
                })

            st.dataframe(pd.DataFrame(improvements), use_container_width=True)

        # Export Buttons
        c_exp1, c_exp2 = st.columns(2)
        with c_exp1:
            csv_bytes = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Benchmark CSV", data=csv_bytes, file_name=f"benchmark_{selected_scenario}.csv", mime="text/csv")
        with c_exp2:
            json_bytes = filtered_df.to_json(orient="records", indent=2).encode("utf-8")
            st.download_button("📥 Download Benchmark JSON", data=json_bytes, file_name=f"benchmark_{selected_scenario}.json", mime="application/json")
    else:
        st.info("No benchmark dataset loaded. Click 'Run Full Benchmark Suite' above.")
