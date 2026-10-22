"""Page 5: Scenario Lab - Demand configuration and synthetic route generation."""

from pathlib import Path
import streamlit as st
from traffic_ai.config.schemas import ScenarioConfig, ScenarioName, VehicleClassMix
from traffic_ai.simulation.scenario_manager import ScenarioManager


def render_page():
    st.markdown("## 🧪 Scenario Lab")
    st.markdown(
        "<span class='badge-sim'>SIMULATION ONLY</span> "
        "<span class='badge-cyan'>7 PRESET BENCHMARKS · REPRODUCIBLE DEMAND</span>",
        unsafe_allow_html=True,
    )
    st.write("")

    preset = st.selectbox(
        "Select Scenario Preset",
        [s.value for s in ScenarioName],
        index=1,
    )

    cfg = ScenarioManager.get_preset_config(ScenarioName(preset))

    col_params, col_summary = st.columns([1.5, 1])

    with col_params:
        st.markdown("### 🎚️ Arrival Rates & Demand Rates (vph)")
        c1, c2 = st.columns(2)
        with c1:
            rate_n = st.number_input("North Approach (vph)", value=float(cfg.north_arrival_rate_vph), step=50.0)
            rate_s = st.number_input("South Approach (vph)", value=float(cfg.south_arrival_rate_vph), step=50.0)
        with c2:
            rate_e = st.number_input("East Approach (vph)", value=float(cfg.east_arrival_rate_vph), step=50.0)
            rate_w = st.number_input("West Approach (vph)", value=float(cfg.west_arrival_rate_vph), step=50.0)

        st.markdown("### ⏱️ Runtime & Seed Configuration")
        c3, c4 = st.columns(2)
        with c3:
            duration = st.number_input("Duration (seconds)", value=int(cfg.duration_seconds), step=300)
            warmup = st.number_input("Warm-up Interval (seconds)", value=int(cfg.warmup_seconds), step=50)
        with c4:
            seed = st.number_input("Deterministic Random Seed", value=int(cfg.seed), step=1)

        st.markdown("### 🚚 Vehicle Class Mix")
        mix_p, mix_b, mix_t, mix_m = st.columns(4)
        with mix_p:
            v_p = st.slider("Passenger", 0.0, 1.0, float(cfg.vehicle_mix.passenger), step=0.05)
        with mix_b:
            v_b = st.slider("Bus", 0.0, 1.0, float(cfg.vehicle_mix.bus), step=0.05)
        with mix_t:
            v_t = st.slider("Truck", 0.0, 1.0, float(cfg.vehicle_mix.truck), step=0.05)
        with mix_m:
            v_m = st.slider("Motorcycle", 0.0, 1.0, float(cfg.vehicle_mix.motorcycle), step=0.05)

        total_v = v_p + v_b + v_t + v_m
        if abs(total_v - 1.0) > 0.01:
            st.warning(f"Vehicle class mix sums to {total_v:.2f} (should sum to 1.0). Will be normalized upon generation.")

        if st.button("💾 Generate & Compile Scenario Routes", use_container_width=True):
            custom_cfg = ScenarioConfig(
                name=ScenarioName(preset),
                seed=int(seed),
                duration_seconds=int(duration),
                warmup_seconds=int(warmup),
                north_arrival_rate_vph=float(rate_n),
                south_arrival_rate_vph=float(rate_s),
                east_arrival_rate_vph=float(rate_e),
                west_arrival_rate_vph=float(rate_w),
                vehicle_mix=VehicleClassMix(passenger=v_p, bus=v_b, truck=v_t, motorcycle=v_m),
            )
            out_file = Path("simulation/routes") / f"{preset}_seed{seed}_{duration}s.rou.xml"
            with st.spinner("Generating routes XML with deterministic seeds..."):
                ScenarioManager.generate_routes_file(custom_cfg, out_file)
            st.success(f"Generated route artifact: {out_file}")

    with col_summary:
        st.markdown("### 📋 Scenario Specifications")
        total_arrival = rate_n + rate_s + rate_e + rate_w
        st.markdown(
            f"""
            <div class='kpi-card'>
                <div class='kpi-label'>Total Network Inflow</div>
                <div class='kpi-value'>{total_arrival:.0f} vph</div>
                <div class='kpi-subtext'>Aggregated across 4 approaches</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("### 📐 Turning Movements")
        st.markdown(
            """
            • <b>Straight Through:</b> 65% of demand<br>
            • <b>Right Turn:</b> 20% of demand<br>
            • <b>Left Turn:</b> 15% of demand (Exclusive phase protected)<br>
            """,
            unsafe_allow_html=True,
        )

        st.info("ℹ️ All demand generations strictly use reproducible pseudo-random generators seeded by Python's `random.Random(seed)`. Different seeds allow testing generalization without training data contamination.")
