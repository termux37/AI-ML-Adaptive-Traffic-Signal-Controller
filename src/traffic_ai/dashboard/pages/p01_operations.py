"""Page 1: Operations Overview - Live realtime simulation telemetry and control center."""

import subprocess
import time
from pathlib import Path
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import cv2

from traffic_ai.config.schemas import ScenarioConfig, ScenarioName, SimulationConfig
from traffic_ai.control.actuated import ActuatedController
from traffic_ai.control.dqn_policy import DQNController
from traffic_ai.control.fixed_time import FixedTimeController
from traffic_ai.control.max_pressure import MaxPressureController
from traffic_ai.control.phase_catalog import PhaseCatalog
from traffic_ai.dashboard.data_access import load_available_runs, load_run_timeseries
from traffic_ai.dashboard.theme import (
    ACCENT_CYAN,
    ACCENT_TEAL,
    CARD_BG,
    STATUS_AMBER,
    STATUS_GREEN,
    STATUS_RED,
    TEXT_MUTED,
    TEXT_PRIMARY,
    get_plotly_layout,
)
from traffic_ai.perception.video_pipeline import VideoPipeline
from traffic_ai.simulation.runner import SimulationRunner
from traffic_ai.simulation.scenario_manager import ScenarioManager


def render_page():
    st.markdown("## 🚦 Operations Overview")
    st.markdown(
        "<span class='badge-sim'>SIMULATION ONLY</span> "
        "<span class='badge-cyan'>SUMO · LIVE REAL-TIME TELEMETRY</span>",
        unsafe_allow_html=True,
    )
    st.write("")

    col_ctrl, col_main = st.columns([1, 2.5])

    with col_ctrl:
        st.markdown("### ⚙️ Simulation Setup")
        scenario_choice = st.selectbox(
            "Traffic Scenario",
            [s.value for s in ScenarioName],
            index=1,
            help="Select reproducible demand profile",
        )
        controller_choice = st.selectbox(
            "Controller",
            ["fixed_time", "actuated", "max_pressure", "dqn"],
            index=2,
            help="Select signal control algorithm",
        )
        sim_duration = st.slider("Duration (seconds)", 30, 300, 90, step=30)
        sim_seed = st.number_input("Random Seed", value=42, step=1)
        sim_speed = st.select_slider(
            "Playback Speed",
            options=["0.5x (Slow)", "1.0x (Real-Time)", "2.0x (Fast)", "Max Speed"],
            value="1.0x (Real-Time)",
            help="Adjust frame rate for in-browser visualizer",
        )

        st.markdown("---")
        st.markdown("### 🎬 Execution Modes")

        start_live = st.button("▶ Start Real-Time Web Simulation", use_container_width=True)

        if st.button("🖥️ Launch Native SUMO-GUI Window", use_container_width=True):
            cmd = [
                "python", "scripts/run_simulation.py",
                "--controller", controller_choice,
                "--scenario", scenario_choice,
                "--seed", str(int(sim_seed)),
                "--duration", str(int(sim_duration)),
                "--gui"
            ]
            subprocess.Popen(cmd)
            st.success("SUMO-GUI Desktop window launched in real-time animation mode!")

        st.markdown("---")
        st.markdown("### 📂 Saved Manifests")
        runs = load_available_runs()
        selected_run = None
        if runs:
            run_ids = [r["run_id"] for r in runs]
            selected_run_id = st.selectbox("Inspect Run Manifest", run_ids, index=0)
            selected_run = next((r for r in runs if r["run_id"] == selected_run_id), None)

    with col_main:
        # Containers for live real-time simulation updates
        live_kpi_placeholder = st.empty()
        live_visual_placeholder = st.empty()
        live_app_placeholder = st.empty()

        if start_live:
            st.info(f"Running Real-Time Simulation: {scenario_choice} | Controller: {controller_choice} | Seed: {sim_seed}")

            # Instantiate selected controller
            if controller_choice == "fixed_time":
                ctrl = FixedTimeController()
            elif controller_choice == "actuated":
                ctrl = ActuatedController()
            elif controller_choice == "max_pressure":
                ctrl = MaxPressureController()
            elif controller_choice == "dqn":
                ctrl = DQNController(model_path="artifacts/models/dqn_best.zip")
            else:
                ctrl = FixedTimeController()

            scenario_cfg = ScenarioManager.get_preset_config(
                ScenarioName(scenario_choice),
                seed=int(sim_seed),
                duration=int(sim_duration),
            )
            sim_cfg = SimulationConfig(gui=False, output_dir="data/runs")
            run_id = f"realtime_{scenario_choice}_{controller_choice}_s{sim_seed}"

            delay_sec = 0.08
            if sim_speed == "0.5x (Slow)":
                delay_sec = 0.20
            elif sim_speed == "1.0x (Real-Time)":
                delay_sec = 0.08
            elif sim_speed == "2.0x (Fast)":
                delay_sec = 0.03
            else:
                delay_sec = 0.001

            pipeline = VideoPipeline(output_video_path=None)

            with SimulationRunner(
                scenario_config=scenario_cfg,
                controller=ctrl,
                simulation_config=sim_cfg,
                run_id=run_id,
            ) as runner:
                runner.start()

                for tick in range(int(sim_duration)):
                    state = runner.step()

                    # Render top-down camera scene with vehicles, signals, stoplines
                    raw_bgr = pipeline.render_virtual_scene(
                        signal_string=state.signal_string,
                        sim_time=state.timestamp,
                    )
                    # Convert BGR to RGB for Streamlit
                    frame_rgb = cv2.cvtColor(raw_bgr, cv2.COLOR_BGR2RGB)

                    # Update live visualization
                    live_visual_placeholder.image(
                        frame_rgb,
                        caption=f"Live Simulation Time: {state.timestamp:0.1f}s | Active Phase: {runner.safety_manager.current_green_id} ({PhaseCatalog.get_phase(runner.safety_manager.current_green_id).name}) | Signal: {state.signal_string}",
                        use_container_width=True,
                    )

                    # Update Live KPI cards
                    with live_kpi_placeholder.container():
                        k1, k2, k3, k4, k5 = st.columns(5)
                        k1.metric("Sim Time", f"{state.timestamp:0.0f} s")
                        k2.metric("Total Queue", f"{state.total_queue} veh")
                        k3.metric("Active Volume", f"{state.total_vehicles} veh")
                        k4.metric("Completed", f"{state.total_completed_vehicles} veh")
                        status_label = "TRANSITION" if state.is_in_transition else "GREEN"
                        k5.metric("Signal Status", status_label)

                    # Update Live Approach Queues
                    with live_app_placeholder.container():
                        st.markdown("#### Approach Demand & Instantaneous Queues")
                        an, asu, ae, aw = st.columns(4)
                        qn = state.approaches.get("north").queue_length if "north" in state.approaches else 0
                        qs = state.approaches.get("south").queue_length if "south" in state.approaches else 0
                        qe = state.approaches.get("east").queue_length if "east" in state.approaches else 0
                        qw = state.approaches.get("west").queue_length if "west" in state.approaches else 0

                        an.markdown(f"<div class='kpi-card'><div class='kpi-label'>North</div><div class='kpi-value'>{qn} veh</div></div>", unsafe_allow_html=True)
                        asu.markdown(f"<div class='kpi-card'><div class='kpi-label'>South</div><div class='kpi-value'>{qs} veh</div></div>", unsafe_allow_html=True)
                        ae.markdown(f"<div class='kpi-card'><div class='kpi-label'>East</div><div class='kpi-value'>{qe} veh</div></div>", unsafe_allow_html=True)
                        aw.markdown(f"<div class='kpi-card'><div class='kpi-label'>West</div><div class='kpi-value'>{qw} veh</div></div>", unsafe_allow_html=True)

                    if delay_sec > 0:
                        time.sleep(delay_sec)

            st.success(f"Real-time simulation completed! Artifacts recorded to data/runs/{run_id}_*")
            st.rerun()

        elif selected_run:
            sm = selected_run.get("summary_metrics", {})
            meta = selected_run.get("metadata", {})

            # Static KPI Strip
            kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
            kpi1.metric("Throughput", f"{sm.get('throughput_vph', 0):.0f} vph")
            kpi2.metric("Avg Queue", f"{sm.get('average_queue_length', 0):.1f} veh")
            kpi3.metric("Max Wait", f"{sm.get('max_wait_time_seconds', 0):.0f} s")
            kpi4.metric("Switches", f"{sm.get('phase_switches_total', 0)}")
            kpi5.metric("Fairness", f"{sm.get('jains_fairness_index', 1.0):.2f}")

            # Approach Summary Cards
            app_queues = sm.get("approach_avg_queues", {})
            st.markdown("#### Approach Queues & Traffic Demand")
            a_n, a_s, a_e, a_w = st.columns(4)
            a_n.markdown(f"<div class='kpi-card'><div class='kpi-label'>North Approach</div><div class='kpi-value'>{app_queues.get('north', 0):.1f} veh</div><div class='kpi-subtext'>Through + Left</div></div>", unsafe_allow_html=True)
            a_s.markdown(f"<div class='kpi-card'><div class='kpi-label'>South Approach</div><div class='kpi-value'>{app_queues.get('south', 0):.1f} veh</div><div class='kpi-subtext'>Through + Left</div></div>", unsafe_allow_html=True)
            a_e.markdown(f"<div class='kpi-card'><div class='kpi-label'>East Approach</div><div class='kpi-value'>{app_queues.get('east', 0):.1f} veh</div><div class='kpi-subtext'>Through + Left</div></div>", unsafe_allow_html=True)
            a_w.markdown(f"<div class='kpi-card'><div class='kpi-label'>West Approach</div><div class='kpi-value'>{app_queues.get('west', 0):.1f} veh</div><div class='kpi-subtext'>Through + Left</div></div>", unsafe_allow_html=True)

            # Time Series Plots
            ts_df = load_run_timeseries(selected_run["run_id"])
            if ts_df is not None and not ts_df.empty:
                st.markdown("#### Real-Time Simulation Progression (Selected Run)")
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=ts_df["timestamp"], y=ts_df["total_queue"], name="Total Queue", line=dict(color=STATUS_AMBER, width=2)))
                fig.add_trace(go.Scatter(x=ts_df["timestamp"], y=ts_df["active_vehicles"], name="Active Vehicles", line=dict(color=ACCENT_CYAN, width=1.5, dash="dot")))
                fig.update_layout(get_plotly_layout(title="Queue and Active Vehicle Trajectory (Empirical Data)"))
                st.plotly_chart(fig, use_container_width=True)

                fig_app = go.Figure()
                fig_app.add_trace(go.Scatter(x=ts_df["timestamp"], y=ts_df["queue_north"], name="North", line=dict(color="#3b82f6")))
                fig_app.add_trace(go.Scatter(x=ts_df["timestamp"], y=ts_df["queue_south"], name="South", line=dict(color="#10b981")))
                fig_app.add_trace(go.Scatter(x=ts_df["timestamp"], y=ts_df["queue_east"], name="East", line=dict(color="#f59e0b")))
                fig_app.add_trace(go.Scatter(x=ts_df["timestamp"], y=ts_df["queue_west"], name="West", line=dict(color="#ec4899")))
                fig_app.update_layout(get_plotly_layout(title="Per-Approach Queue Trajectories"))
                st.plotly_chart(fig_app, use_container_width=True)
        else:
            st.info("Click 'Start Real-Time Web Simulation' or 'Launch Native SUMO-GUI Window' to observe traffic in real time.")
