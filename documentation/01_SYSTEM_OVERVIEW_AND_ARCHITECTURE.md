# Module 01: System Overview & Architecture

## 1. System Vision & Purpose
**AI & ML Based Adaptive Traffic Control System** is an end-to-end virtual research and decision-support platform designed to model, analyze, and optimize urban traffic signal control using reinforcement learning and computer vision.

Operating within the Eclipse SUMO (Simulation of Urban MObility) microscopic simulation suite, the system models high-fidelity vehicle kinematics, car-following physics, and detector actuations while decoupling the learning policy from deterministic safety invariants.

### Key Capabilities
- **Microscopic Traffic Simulation:** A single controlled 4-way intersection (`junction_center`) with dedicated turning bays and multi-class traffic.
- **Deterministic Signal Safety:** Strict clearance intervals (yellow 3s, all-red 2s), minimum green (10s), and maximum green (60s) preventing conflicts and starvation.
- **Four Control Regimes:** Fixed-Time, Vehicle-Actuated, Max-Pressure (PressLight KDD 2019), and Deep Q-Network (DQN).
- **Virtual-Camera Perception Pipeline:** YOLOv8n object detection, spatial IoU tracking, approach polygon ROI assignment, and live ground-truth comparison.
- **Operations Console Dashboard:** An 11-page dark operations-console interface with real-time in-browser streaming and desktop GUI animation.
- **Empirical Ground-Truth Guarantee:** Every displayed metric, convergence curve, and benchmark result is computed from real simulation data.

---

## 2. High-Level Architecture Diagram

```
+-----------------------------------------------------------------------------------------+
|                                    USER INTERFACE                                       |
|                  Streamlit Multipage Operations Console (11 Pages)                      |
|           • Real-Time Web Streamer       • Interactive Plotly Analytics                 |
|           • Scenario Generator Lab       • Checkpoint & Model Registry                  |
+-----------------------------------------------------------------------------------------+
                                      |                     ^
                     Configuration    |                     | Real Telemetry &
                     & Run Triggers   |                     | CSV/JSON Manifests
                                      v                     |
+-----------------------------------------------------------------------------------------+
|                              SIMULATION RUNNER ORCHESTRATOR                             |
|                        (src/traffic_ai/simulation/runner.py)                            |
+-----------------------------------------------------------------------------------------+
             |                               |                               ^
             | Command Execution             | Frame Rendering               | Ground Truth
             v                               v                               |
+------------------------+      +-------------------------+      +------------------------+
|      Eclipse SUMO      |      |   Virtual Camera Render |      |  Ground Truth Adapter  |
|   Microscopic Engine   |      |  (cv2 800x800 Canvas)   |      | (Direct TraCI Queries) |
| (Krauss Car-Following) |      +-------------------------+      +------------------------+
+------------------------+                   |                               |
             ^                               v                               v
             | Actuation        +-------------------------+      +------------------------+
             | State String     |   YOLOv8n Object Det.   |      |   25-Dimensional       |
             |                  |  & Spatial IoU Tracker  |      |   Observation Builder  |
             |                  +-------------------------+      +------------------------+
             |                               |                               |
             |                               +---------------+---------------+
             |                                               |
+----------------------------+                               v
| Deterministic Safety Guard | <---------------- +----------------------------------------+
| • Minimum Green (10.0s)    |   Action Proposal | Signal Controller                      |
| • Maximum Green (60.0s)    |   (0, 1, 2, 3)    | • Fixed-Time      • Max-Pressure       |
| • Yellow (3.0s) & Red (2.0s|                   | • Vehicle-Actuated • DQN Policy        |
+----------------------------+                   +----------------------------------------+
```

---

## 3. Directory Layout & Module Responsibilities

| Path | Purpose & Responsibilities |
| :--- | :--- |
| `src/traffic_ai/config/` | Pydantic data contracts (`ScenarioConfig`, `SafetyConfig`, `ControllerConfig`, `SimulationConfig`). |
| `src/traffic_ai/simulation/` | SUMO lifecycle orchestration (`runner.py`), route compilation (`scenario_manager.py`), and TraCI IPC. |
| `src/traffic_ai/control/` | Controllers (`fixed_time.py`, `actuated.py`, `max_pressure.py`, `dqn_policy.py`), phase catalog, and deterministic safety manager. |
| `src/traffic_ai/perception/` | Computer vision subsystem: YOLOv8n detector, spatial tracker, calibration, density estimator, and video pipeline. |
| `src/traffic_ai/state/` | Structured data models (`ApproachState`, `TrafficState`), ground truth extractor, and multimodal observation builders. |
| `src/traffic_ai/metrics/` | Time-series collector, KPI aggregator, CSV timeseries logger, and JSON run manifest generator. |
| `src/traffic_ai/training/` | Gymnasium environment (`environment.py`), training pipeline (`train_dqn.py`), and progress callbacks (`callbacks.py`). |
| `src/traffic_ai/experiments/` | Batch benchmarking engine (`runner.py`) comparing controllers across identical scenarios and seeds. |
| `src/traffic_ai/dashboard/` | Operations console Streamlit modules, dark theme styling (`theme.py`), and data access layer (`data_access.py`). |
| `src/traffic_ai/utils/` | Rotating structured logging, filesystem path resolvers, and system diagnostic routines. |
| `scripts/` | Standalone CLI entry points for environment checks, scenario generation, simulation execution, training, benchmarking, and video rendering. |
| `simulation/` | XML network geometry (`.nod.xml`, `.edg.xml`, `.con.xml`, `.tll.xml`), compiled `.net.xml`, detector definitions, and SUMO configuration. |
| `artifacts/` | Saved neural network weights (`dqn_best.zip`), progress telemetry, and rendered `.mp4` perception videos. |
| `data/` | Structured run manifests, time-series logs (`data/runs/`), and processed benchmark datasets (`data/processed/`). |
| `tests/` | Comprehensive test suite covering unit tests, integration tests, and environment smoke checks. |
