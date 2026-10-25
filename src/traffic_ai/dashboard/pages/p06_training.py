"""Page 6: Training Center - DQN training execution, convergence monitoring, and telemetry."""

from pathlib import Path
import streamlit as st
import plotly.graph_objects as go
from traffic_ai.dashboard.data_access import load_model_metadata, load_training_progress
from traffic_ai.dashboard.theme import ACCENT_CYAN, CARD_BG, STATUS_AMBER, STATUS_GREEN, get_plotly_layout
from traffic_ai.training.train_dqn import train_dqn
from traffic_ai.config.schemas import ScenarioName


def render_page():
    st.markdown("## 🏋️ Reinforcement Learning Training Center")
    st.markdown(
        "<span class='badge-sim'>SIMULATION ONLY</span> "
        "<span class='badge-cyan'>STABLE-BASELINES3 DQN · REAL TRAINING RUNS</span>",
        unsafe_allow_html=True,
    )
    st.write("")

    col_launch, col_curves = st.columns([1, 2])

    with col_launch:
        st.markdown("### 🚀 Launch DQN Training")
        train_timesteps = st.number_input("Target Timesteps", value=2000, min_value=200, max_value=50000, step=500)
        train_seed = st.number_input("Training Seed", value=42, step=1)
        train_scenario = st.selectbox("Training Demand Profile", [s.value for s in ScenarioName], index=1)
        train_device = st.selectbox("Compute Device", ["cpu", "cuda"], index=0, help="CPU is recommended for fast TraCI simulation IPC")

        if st.button("🔥 Start Training Run", use_container_width=True):
            with st.spinner(f"Training DQN agent for {train_timesteps} timesteps..."):
                best_path = train_dqn(
                    total_timesteps=int(train_timesteps),
                    seed=int(train_seed),
                    scenario_name=ScenarioName(train_scenario),
                    device=train_device,
                )
                st.success(f"Training complete! Saved to: {best_path}")
                st.rerun()

        st.markdown("---")
        prog = load_training_progress()
        st.markdown("### 📈 Live Training Status")
        st.markdown(
            f"""
            <div class='kpi-card'>
                <div class='kpi-label'>Status</div>
                <div class='kpi-value'>{prog.get('status', 'IDLE')}</div>
                <div class='kpi-subtext'>{prog.get('timesteps_completed', 0)} / {prog.get('total_timesteps', 0)} Timesteps</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.metric("Latest Reward", f"{prog.get('latest_reward', 0.0):.1f}")
        st.metric("Rolling Reward (10-ep)", f"{prog.get('rolling_reward', 0.0):.1f}")

    with col_curves:
        st.markdown("### 📉 Real Training Convergence Curves")
        history = prog.get("history", {})
        timesteps = history.get("timesteps", [])
        rewards = history.get("rewards", [])
        rolling = history.get("rolling_rewards", [])

        if timesteps and rewards:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=timesteps, y=rewards,
                name="Episode Return",
                mode="markers+lines",
                marker=dict(size=5, color="#06b6d4"),
                line=dict(width=1, dash="dot"),
            ))
            if rolling:
                fig.add_trace(go.Scatter(
                    x=timesteps, y=rolling,
                    name="Rolling Average Return",
                    line=dict(color="#10b981", width=2.5),
                ))
            fig.update_layout(get_plotly_layout(title="Empirical DQN Training Curves (Real Telemetry)"))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No training history recorded yet. Launch a training run above to view live convergence curves.")

        # Hyperparameters summary
        meta = load_model_metadata()
        if meta:
            st.markdown("#### Hyperparameter Configuration")
            hparams = meta.get("hyperparameters", {})
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.caption(f"**LR:** {hparams.get('learning_rate')}")
            with c2:
                st.caption(f"**Batch:** {hparams.get('batch_size')}")
            with c3:
                st.caption(f"**Gamma:** {hparams.get('gamma')}")
            with c4:
                st.caption(f"**Buffer:** {hparams.get('buffer_size')}")
