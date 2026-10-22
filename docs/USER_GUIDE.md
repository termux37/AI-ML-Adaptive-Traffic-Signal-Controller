# AI & ML Based Adaptive Traffic Control System - User Guide & Walkthrough

## 1. Quickstart Installation & Launch
```powershell
# 1. Clone or open workspace
cd c:\ai_ml_project

# 2. Run automated environment smoke test
python scripts/check_environment.py

# 3. Launch operations dashboard
streamlit run app.py
```
Open browser at `http://localhost:8501`.

---

## 2. Dashboard Pages Walkthrough

### Page 1: Operations Overview
- **Central KPI Strip:** Shows real-time Throughput, Average Queue, Maximum Wait Time, Phase Switches, and Jain's Fairness Index.
- **Approach Demand Cards:** Displays live queues for North, South, East, and West approaches.
- **Simulation Control Panel:**
  - Select scenario preset (e.g. `balanced`, `north_south_dominant`, `bursty`).
  - Select active controller (`fixed_time`, `actuated`, `max_pressure`, `dqn`).
  - Adjust simulation duration and seed, then click **▶ Run Simulation**.
- **Interactive Trajectory Plots:** Displays live queue progression and active vehicle volume over simulated time.

### Page 2: Live Intersection
- **Top-Down Schematic:** Interactive visual diagram of the 4-way junction, lane assignments, stop lines, induction loop detectors, and traffic light heads.
- **Approach Inspector:** View geometry details (lane width 3.2m, length 250m, speed limit 50 km/h).

### Page 3: AI Controller
- **Observation Inspector:** Visualizes the 25-dimensional normalized continuous observation vector fed to the neural network.
- **Safety Constraints Panel:** Inspects Minimum Green (10s), Maximum Green (60s), Yellow (3s), and All-Red (2s) rules.
- **Model Metadata:** Displays active checkpoint parameters and network layer specifications.

### Page 4: Camera & Perception
- **Video Preview:** Plays the recorded virtual camera perception demonstration (`artifacts/videos/perception_demo.mp4`).
- **Telemetry HUD:** Displays measured FPS (27.2 FPS) and neural network latency (36.8 ms).
- **Perception vs Ground Truth:** Bar chart comparing YOLO-estimated vehicle counts against SUMO ground-truth counts.

### Page 5: Scenario Lab
- **Preset Selector:** Choose between Low, Balanced, Heavy, NS Dominant, EW Dominant, Bursty, or Unseen Evaluation.
- **Parameter Sliders:** Customize hourly arrival rates, turning movements, and vehicle class distributions (Passenger, Bus, Truck, Motorcycle).
- **Compile Button:** Generates reproducible XML route files with deterministic seeds.

### Page 6: Training Center
- **DQN Training:** Configure target timesteps (e.g., 2000), seed, and compute device (CPU/CUDA), then click **Start Training Run**.
- **Convergence Curves:** Inspect real episode returns and rolling 10-episode mean rewards.

### Page 7: Experiments & Benchmarking
- **Full Benchmark Suite:** Runs all 4 controllers on identical seeds and scenarios.
- **Comparison Table & Charts:** Direct comparison of throughput, queue minimization, and fairness.
- **Export Options:** Download benchmark results as `.csv` or `.json`.

### Page 8: Analytics & Reports
- **Spider / Radar Chart:** Compares the 4 controllers across Throughput, Queue Clearance, Delay Minimization, Starvation Guard, and Switching Stability.
- **Technical Report Preview & Download:** One-click generation of technical evaluation Markdown reports.

### Page 9: Model Registry
- Lists saved checkpoint artifacts (`.zip`), file size, architecture details, and verification status.

### Page 10: System Health & Diagnostics
- Audits SUMO binary paths, `SUMO_HOME`, TraCI versions, host GPU status, and displays live system logs.

### Page 11: Documentation & About
- Architectural flowcharts, mathematical formulations, research bibliography, and disclaimers.
