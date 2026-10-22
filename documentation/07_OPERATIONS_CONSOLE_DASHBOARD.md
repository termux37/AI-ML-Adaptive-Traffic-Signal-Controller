# Module 07: Operations Console Dashboard Specification

## 1. Design System & User Interface Architecture
The Adaptive Traffic Control System Operations Console is built using **Streamlit 1.63.0** and **Plotly 7.0.0**, engineered to provide the visual density, restrained typography, and functional responsiveness of a mature, mission-critical traffic operations center.

### 1.1 Color Palette & Theme Tokens (`theme.py`)
- **Primary Canvas Background:** `#0B0F19` (Deep Obsidian / Graphite)
- **Panel & Sidebar Background:** `#111827` (Dark Navy Slate)
- **Card & Component Background:** `#161E2E` (Elevated Panel)
- **Borders & Dividers:** `#1F2937` (Subtle Slate Gray)
- **Primary Text:** `#F9FAFB` (High-contrast Off-White)
- **Muted Text / Labels:** `#9CA3AF` (Muted Slate)
- **Interactive Accent:** `#06B6D4` (Restrained Cyan / Teal)
- **State Badges:**
  - Verified Safe / Active: `#10B981` (Emerald Green)
  - Warning / Transition: `#F59E0B` (Amber)
  - Safety Alert / Conflict Interception: `#EF4444` (Coral Red)
  - Simulation Badge: `#94a3b8` on `#1e293b`

---

## 2. Global Shell & Persistent Elements (`app.py`)
- **Header Treatment:** Compact corporate wordmark: `Adaptive Traffic Control System | TRAFFIC` with subtitle `Simulation · Perception · Control`.
- **Persistent Disclaimer:** Mandatory `SIMULATION ONLY` and `SUMO v1.27.1` badges displayed in the sidebar.
- **Sensory Observation Mode Selector:**
  - `Ground Truth (Direct TraCI)`: Reads exact simulator state.
  - `Vision (YOLO Pipeline)`: Feeds perception estimates into decision loop.
  - `Hybrid (Vision + Ground Truth)`: Vision state paired with ground-truth validation.
- **Sidebar Navigation:** Radio menu providing direct access to all 11 pages without page reloads.

---

## 3. Detailed Page Specifications

### Page 1: Operations Overview (`p01_operations.py`)
- **Dual Real-Time Simulation Execution:**
  1. *In-Browser Real-Time Web Streamer:* Clicking `▶ Start Real-Time Web Simulation` advances TraCI tick-by-tick, rendering the top-down canvas with moving vehicle glyphs, animated signal heads, and live updating KPI cards.
  2. *Desktop SUMO-GUI Window:* Clicking `🖥️ Launch Native SUMO-GUI Window` spawns `sumo-gui` with real-time animated car-following physics in a separate window.
- **Core KPI Strip:** Real-time Throughput (vph), Average Queue (veh), Maximum Wait (s), Phase Switches, and Jain's Fairness Index.
- **Approach Demand Cards:** Displays instantaneous queues and vehicle volumes for North, South, East, and West approaches.
- **Historical Trajectory Charts:** Interactive Plotly curves displaying total queue evolution and active vehicle volume over time.

### Page 2: Live Intersection (`p02_intersection.py`)
- **Top-Down Schematic:** Interactive vector diagram showing roads, yellow center division lines, solid white stop lines, and signal heads.
- **Induction Loop Markers:** Plots the spatial locations of `det_stop_*` (stopline loops at 230m) and `det_adv_*` (advance arrival loops at 120m).
- **Approach Inspector:** Displays approach length (250m), incoming lanes (2), outgoing lanes (2), lane width (3.2m), and speed limits (50 km/h).
- **Movement Allocation:** Explicit documentation of through and turning movements per lane.

### Page 3: AI Controller (`p03_controller.py`)
- **Controller Selector:** Fixed-Time, Actuated, Max-Pressure, or DQN.
- **Observation Inspector:** Visualizes the 25-dimensional normalized continuous state vector as an interactive horizontal bar chart.
- **Safety Constraints Audit:** Displays minimum green (10s), maximum green (60s), yellow clearance (3s), and all-red clearance (2s) rules.
- **Reward Formulation:** Displays KaTeX-rendered mathematical equation and weight justifications.
- **Model Metadata:** Displays active checkpoint architecture, device, and hyperparameters.

### Page 4: Camera & Perception (`p04_perception.py`)
- **Embedded Video Player:** Plays recorded simulation video processed by YOLOv8n (`artifacts/videos/perception_demo.mp4`).
- **Telemetry HUD:** Measured inference latency (36.8 ms) and frame processing rate (27.2 FPS).
- **Perception vs Ground Truth:** Grouped bar chart comparing visual count estimates against SUMO ground truth for all 4 approaches.
- **MAE History & Diagnostics:** Displays average Mean Absolute Error (0.25 vehicles) and target vehicle classes.
- **Scientific Limitation Disclosure:** Explains perspective occlusion and geometric ROI calibration.

### Page 5: Scenario Lab (`p05_scenario_lab.py`)
- **7 Preset Cards:** Low, Balanced, Heavy, NS Dominant, EW Dominant, Bursty, and Unseen Evaluation.
- **Dynamic Demand Editor:** Number inputs for North, South, East, and West arrival rates (vph).
- **Runtime Parameters:** Duration, warm-up interval, and deterministic random seed.
- **Vehicle Class Mix Sliders:** Adjusts Passenger, Bus, Truck, and Motorcycle proportions with validation warnings if the sum departs from 1.0.
- **Route Compiler:** Clicking `💾 Generate & Compile Scenario Routes` invokes `ScenarioManager` and saves reproducible `.rou.xml` files.

### Page 6: Training Center (`p06_training.py`)
- **Interactive Training Launcher:** Configure total timesteps, random seed, training scenario, and compute device (CPU/CUDA).
- **Live Status Card:** Displays training status (`RUNNING`, `COMPLETED`), completed timesteps, and latest episode return.
- **Empirical Convergence Curves:** Plotly chart displaying raw episode returns and rolling 10-episode mean rewards reading directly from `artifacts/models/training_progress.json`.

### Page 7: Experiments & Benchmarking (`p07_benchmarks.py`)
- **One-Click Benchmark Suite:** Clicking `🚀 Run Full Benchmark Suite` executes all 4 controllers on identical seeds and scenarios.
- **Scenario Filter:** Dropdown to filter results by scenario preset (`balanced`, `north_south_dominant`, etc.).
- **Comparative Charts:** Side-by-side Plotly bar charts comparing Throughput (vph) and Average Queue Length.
- **Baseline Improvement Table:** Computes relative percentage improvements vs Fixed-Time baseline.
- **Artifact Downloads:** Direct export of benchmark results as `.csv` or `.json`.

### Page 8: Analytics & Reports (`p08_analytics.py`)
- **Multi-Dimensional Radar Chart:** 5-axis polar chart comparing Fixed-Time, Actuated, Max-Pressure, and DQN across Throughput, Queue Clearance, Delay Minimization, Starvation Guard, and Switching Stability.
- **Standard Metric Definitions:** Information cards explaining calculation formulas and units.
- **Formal Technical Report Generator:** One-click markdown technical report preview and download button.

### Page 9: Model Registry (`p09_registry.py`)
- **Checkpoint Table:** Lists all `.zip` models in `artifacts/models/`, file sizes, modification timestamps, and validation badges (`⭐ BEST VALIDATED`).
- **Architecture Viewer:** Documents PyTorch network layers, hidden unit counts (`[128, 128]`), and parameter sizes.
- **Hyperparameter Inspector:** Full JSON view of training settings.

### Page 10: System Health & Diagnostics (`p10_system_health.py`)
- **Host System Diagnostics:** Audits SUMO binary paths, `SUMO_HOME`, TraCI versions, host GPU status, and Python runtime.
- **Key Dependencies List:** Verified versions of Gymnasium, Stable-Baselines3, Streamlit, Plotly, Pandas, Scipy, and Pytest.
- **Live Log Viewer:** Dropdown to select and inspect rotating log files from `data/runs/`.

### Page 11: Documentation & About (`p11_documentation.py`)
- **Tabs:** System Architecture, Controller Formulations, and Research Foundation.
- **Peer-Reviewed Bibliography:** Formal citations for PressLight (KDD 2019), SUMO (ITSC 2018), Stable-Baselines3 (JMLR 2021), and YOLOv8.
- **Persistent Legal Disclaimer:** Discloses that Adaptive Traffic Control System is an academic research demonstration not certified for physical road hardware.
