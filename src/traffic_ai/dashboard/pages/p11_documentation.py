"""Page 11: Documentation & About - Architectural guide, research bibliography, and disclosures."""

import streamlit as st


def render_page():
    st.markdown("## 📚 Documentation & Technical Reference")
    st.markdown(
        "<span class='badge-sim'>SIMULATION ONLY</span> "
        "<span class='badge-cyan'>AI & ML BASED ADAPTIVE TRAFFIC CONTROL SYSTEM</span>",
        unsafe_allow_html=True,
    )
    st.write("")

    st.markdown(
        """
        > ⚠️ **MANDATORY LEGAL & TECHNICAL DISCLAIMER**  
        > **This project is an academic simulation and virtual research platform.**  
        > It is entirely virtual and operates within the Eclipse SUMO microscopic simulation environment.  
        > It is **NOT certified for real-world physical traffic control**, physical road hardware, or live municipal infrastructure.
        """
    )

    t1, t2, t3 = st.tabs(["System Architecture", "Controller Formulations", "Research Foundation"])

    with t1:
        st.markdown(
            """
            ### System Architecture & Main Data Flow
            1. **Scenario Manager:** Loads or generates reproducible vehicle route files (`.rou.xml`) with explicit seeds across 7 benchmark scenarios.
            2. **Microscopic Simulation (SUMO & TraCI):** Executes vehicle kinematics, car-following (Krauss model), and physical detector actuations.
            3. **Ground-Truth & Perception Layers:**
               - `ground_truth`: Extracts exact vehicle positions, speeds, queues, and waiting times directly via TraCI.
               - `vision`: Processes rendered virtual camera frames through YOLOv8n object detection and spatial IoU tracking.
            4. **Observation Builder:** Scales and normalizes continuous features into a 25-dimensional observation vector.
            5. **Signal Controller (DQN / Heuristic / Baseline):** Evaluates observations and proposes discrete target green phase actions.
            6. **Deterministic Safety Manager:** Enforces minimum green (10s), maximum green (60s), yellow transitions (3s), and all-red clearance intervals (2s).
            7. **Metrics Collector:** Computes delay, throughput, queue trajectories, phase switches, and Jain's fairness index, exporting run manifests.
            """
        )

    with t2:
        st.markdown(
            """
            ### Controller Regimes
            - **Fixed-Time Controller:** Implements static cycle timing (default 90 seconds) with predetermined green splits across the 4 phases.
            - **Vehicle-Actuated Controller:** Dynamically extends green phases when approaching vehicles are detected within a 3.0s gap threshold, terminating on gap-out or max-green.
            - **Max-Pressure Controller:** Formulated following Varaiya (2013) and PressLight (KDD 2019):
              $$P(p) = \\sum_{l \\in In(p)} Q(l) - \\sum_{m \\in Out(p)} Q(m)$$
              Selects the phase maximizing downstream vehicle pressure differential.
            - **Deep Q-Network (DQN) Controller:** Deep RL agent with an MLP [128, 128] policy trained to optimize a composite reward balancing queue reduction, throughput bonus, switching stability, and starvation prevention.
            """
        )

    with t3:
        st.markdown(
            """
            ### Peer-Reviewed Research Foundation & Bibliography
            1. **PressLight: Learning Max Pressure Control to Coordinate Traffic Signals in Arterial Networks**  
               *Wei et al., ACM SIGKDD International Conference on Knowledge Discovery & Data Mining (KDD 2019).*  
               *Significance:* Establishes theoretical link between Max-Pressure queue differentials and RL state/reward design.
            2. **Microscopic Traffic Simulation using SUMO**  
               *Lopez et al., IEEE Intelligent Transportation Systems Conference (ITSC 2018).*  
               *Significance:* Validates microscopic TraCI vehicle actuation and lane kinematics.
            3. **Stable-Baselines3: Reliable Reinforcement Learning Implementations**  
               *Raffin et al., Journal of Machine Learning Research (JMLR 2021).*  
               *Significance:* Provides verified DQN and replay buffer implementation.
            4. **Ultralytics YOLOv8: Real-Time Object Detection Architecture**  
               *Jocher et al., 2023.*  
               *Significance:* Computer vision inference for multi-class vehicle detection.
            """
        )
