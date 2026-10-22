# AI & ML Based Adaptive Traffic Control System - Architecture Specification

## 1. System Overview
**AI & ML Based Adaptive Traffic Control System** is an end-to-end, research-grade virtual platform demonstrating adaptive traffic signal control through microscopic simulation, computer vision, and reinforcement learning.

```
+-----------------------------------------------------------------------------------+
|                           ADAPTIVE TRAFFIC OPERATIONS CONSOLE                               |
|          Streamlit Multipage Dashboard (Dark Operations Console Theme)            |
+-----------------------------------------------------------------------------------+
         |                                    ^                       ^
         | Commands & Scenario Selection      | Visualizations        | Logs & Artifacts
         v                                    |                       |
+-----------------------------------------------------------------------------------+
|                           SIMULATION RUNNER ORCHESTRATOR                          |
|                     (src/traffic_ai/simulation/runner.py)                         |
+-----------------------------------------------------------------------------------+
         |                                  |                        ^
         | TraCI Commands                   | Sensing                | Ground Truth
         v                                  v                        |
+----------------------+        +------------------------+  +-----------------------+
|  SUMO Microscopic    |        | Virtual Camera Render  |  | Ground Truth Adapter  |
|  Simulation Engine   |        | (cv2 + 800x800 Canvas) |  | (Direct TraCI Queries)|
| (Krauss Car-Following|        +------------------------+  +-----------------------+
|  Intersection Net)   |                    |                            |
+----------------------+                    v                            v
         ^                      +------------------------+  +-----------------------+
         | Actuation            | YOLOv8n Perception     |  | Multimodal State      |
         | Signal State         | & IoU Vehicle Tracker  |  | Builder (25-dim obs)  |
         |                      +------------------------+  +-----------------------+
         |                                  |                            |
         |                                  +------------+---------------+
         |                                               |
+------------------------------------+                   v
|   Deterministic Safety Manager     | <----+   +-----------------------------------+
| (Min/Max Green, Clearance Guards)  |      |---| Signal Controller                 |
+------------------------------------+          | (Fixed-Time, Actuated,            |
                                                |  Max-Pressure, DQN)               |
                                                +-----------------------------------+
```

## 2. Directory Hierarchy and Modular Responsibilities
- `src/traffic_ai/config/`: Pydantic data contracts (`ScenarioConfig`, `SafetyConfig`, `ControllerConfig`, `SimulationConfig`).
- `src/traffic_ai/simulation/`: SUMO execution lifecycle (`runner.py`), route demand generator (`scenario_manager.py`), and TraCI bindings.
- `src/traffic_ai/control/`: Traffic controllers (`fixed_time.py`, `actuated.py`, `max_pressure.py`, `dqn_policy.py`), phase catalog (`phase_catalog.py`), and the deterministic safety guard (`safety_manager.py`).
- `src/traffic_ai/perception/`: Computer vision subsystem:
  - `detector.py`: YOLOv8n inference and vehicle class filtering.
  - `tracker.py`: Spatial IoU tracking and ID persistence.
  - `camera_calibration.py`: Polygon approach ROI coordinate mapping.
  - `density_estimator.py`: Mean absolute count error calculation vs ground truth.
  - `video_pipeline.py`: Virtual camera scene rendering and `.mp4` video recording.
- `src/traffic_ai/metrics/`: Step-by-step metrics collector (`collector.py`), computing throughput, queue lengths, delays, and Jain's fairness index.
- `src/traffic_ai/training/`: Gymnasium environment (`environment.py`), training pipeline (`train_dqn.py`), and progress telemetry callback (`callbacks.py`).
- `src/traffic_ai/dashboard/`: Multipage Streamlit user interface conforming to the dark operations-console design system.

## 3. Data Flow & Execution Lifecycle
1. **Scenario Initialization:** The `ScenarioManager` loads or generates deterministic route files based on configured vehicle arrival rates and random seeds.
2. **Simulation Step:** TraCI steps the SUMO engine by $dt = 1.0$ second.
3. **Observation Construction:**
   - In `ground_truth` mode, exact halting vehicle counts and queues are read directly from TraCI edges.
   - In `vision` mode, the top-down scene is rendered, detected by YOLO, and mapped to approach polygons.
   - Values are normalized into a continuous 25-dimensional observation vector.
4. **Action Proposal:** The active controller inspects the observation and proposes a target green phase $a \in \{0, 1, 2, 3\}$.
5. **Safety Validation:** The `DeterministicSafetyManager` verifies minimum green duration (10s), enforces maximum green (60s), and initiates yellow (3s) and all-red (2s) clearance sequences.
6. **Actuation:** The validated signal state string is committed to SUMO via `traci.trafficlight.setRedYellowGreenState`.
7. **Telemetry Logging:** `MetricsCollector` records queue, speed, waiting time, and completed trips, saving CSV time-series and JSON manifests upon completion.
