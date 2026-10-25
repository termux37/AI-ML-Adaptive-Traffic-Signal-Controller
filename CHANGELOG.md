# Changelog

All notable changes to the **AI & ML Based Adaptive Traffic Control System** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-10-22

### Added
- **Microscopic Traffic Simulation Engine:**
  - 4-way intersection network (`junction_center`) with dedicated turning bays, 16 controlled link movements, and Krauss car-following physics in Eclipse SUMO.
  - Multi-lane induction loop array (E1 detectors) on all incoming approaches with instantaneous occupancy and velocity polling.
  - Deterministic route generators for `balanced`, `heavy`, `bursty`, `north_south_dominant`, and `unseen_evaluation` scenarios.
- **Deterministic Signal Safety Manager:**
  - Decoupled safety guard with strict finite-state machine transitions.
  - Minimum green time enforcement ($t_{min} = 10.0\text{ s}$) to prevent hunting.
  - Maximum green bounds ($t_{max} = 60.0\text{ s}$) to prevent cross-street vehicle starvation.
  - Non-preemptible yellow clearance ($t_{yellow} = 3.0\text{ s}$) and all-red clearance ($t_{red} = 2.0\text{ s}$) intervals.
  - Conflict matrix preventing simultaneous green indications across opposing movements.
- **Traffic Signal Controllers:**
  - `FixedTimeController`: Pre-timed cyclic schedule with customizable cycle and green split durations.
  - `ActuatedController`: Demand-responsive extension based on detector gap headway ($3.0\text{ s}$) and max-green caps.
  - `MaxPressureController`: Decentralized queue differential feedback controller optimizing network throughput (Varaiya 2013).
  - `DQNController`: PyTorch-backed Deep Q-Network agent trained on a 25-dimensional continuous observation vector.
- **Reinforcement Learning Pipeline:**
  - Standard Gymnasium environment interface (`TrafficSignalEnv`) with step-level TraCI synchronization.
  - Continuous 25-dimensional normalized state vector and 4 discrete action choices.
  - Composite multi-objective reward formulation penalizing queues, waiting times, phase switches, and starvation.
  - Training pipeline with experience replay, target network synchronization, and checkpoint callbacks.
- **Computer Vision Perception Subsystem:**
  - Top-down orthographic camera frame generation.
  - Deep learning object detector powered by Ultralytics YOLOv8n with multi-class vehicle filtering (`car`, `motorcycle`, `bus`, `truck`).
  - Spatial Intersection-over-Union (IoU) vehicle tracking for persistent vehicle identification across frames.
  - Calibrated convex approach polygon ROI mapping with live Mean Absolute Error (MAE) telemetry against TraCI ground truth.
- **Operations Console Dashboard:**
  - 11-page dark operations-console interface built with Streamlit and Plotly.
  - Real-time in-browser simulation animator, live phase diagrams, controller switching, perception inspector, and benchmark analytics.
  - One-click desktop SUMO-GUI launcher.
- **Automated Verification Suite:**
  - 15 unit, integration, and smoke tests in `tests/` verifying safety invariants, gym spaces, and end-to-end TraCI runs.
  - Unified launch scripts (`launch.py`, `launch.bat`, `launch.ps1`).
