# Module 08: Scripts & Master Launchers

## 1. Unified Master Launch Orchestrator

To start the project with a single command, Adaptive Traffic Control System provides a unified launch orchestrator available in three execution formats:
- **Python Master Script:** `launch.py`
- **Windows Batch Launcher:** `launch.bat`
- **PowerShell Script:** `launch.ps1`

### 1.1 Ordered 6-Task Execution Pipeline
When initiated, `launch.py` executes the following sequence:

```
[START]
   |
   v
[Task 1: Environment & System Audit]
• Checks Python >= 3.10, SUMO_HOME, TraCI, PyTorch, YOLO, OpenCV
• Runs 60-second headless SUMO smoke test
   | (Pass)
   v
[Task 2: Network Verification & Scenario Demand Generation]
• Compiles intersection.net.xml if missing using netconvert
• Generates baseline route demand for balanced, ns_dominant, bursty
   | (Pass)
   v
[Task 3: Automated Pytest Test Suite]
• Executes 15 unit, integration, and safety tests
   | (Pass)
   v
[Task 4: Model Checkpoints & Vision Pipeline Artifacts]
• Verifies dqn_best.zip exists (trains 1000 steps if missing)
• Verifies perception_demo.mp4 exists (generates 30s clip if missing)
   | (Pass)
   v
[Task 5: Pre-Computed Multi-Controller Benchmarks]
• Verifies benchmark_results.csv exists (runs evaluation if missing)
   | (Pass)
   v
[Task 6: Launch Streamlit Operations Console]
• Spawns Streamlit on http://localhost:8501
• Automatically opens default web browser
```

### 1.2 Master Launcher Command Options

| Command | Action Performed |
| :--- | :--- |
| `python launch.py` | Runs full 6-task sequence and opens operations dashboard in web browser. |
| `launch.bat` | Windows batch launcher for double-clicking in File Explorer or running in CMD. |
| `.\launch.ps1` | Native PowerShell master launcher with colorized console formatting. |
| `python launch.py --gui` | Runs checks and launches desktop SUMO-GUI with real-time vehicle animation. |
| `python launch.py --test-only` | Runs environment audit and test suite only, then exits with code 0. |
| `python launch.py --skip-tests` | Skips test suite execution for faster dashboard launch. |
| `python launch.py --no-browser` | Launches dashboard server without opening the web browser automatically. |

---

## 2. Standalone CLI Utility Scripts

Every subsystem can be invoked independently from the command line:

### 2.1 Automated Smoke Test (`scripts/check_environment.py`)
```powershell
python scripts/check_environment.py
```
- Audits Python 3.12, SUMO 1.27.1, `SUMO_HOME`, TraCI, PyTorch, Gymnasium, YOLO, and OpenCV.
- Executes a 60-second headless simulation test.
- Returns exit code `0` on success, `1` on failure.

### 2.2 Route Scenario Generator (`scripts/generate_scenario.py`)
```powershell
python scripts/generate_scenario.py --scenario balanced --seed 42 --duration 3600
```
- Synthesizes vehicle arrivals according to specified arrival rates and random seed.
- Generates valid SUMO XML route file in `simulation/routes/`.

### 2.3 Standalone Simulation Runner (`scripts/run_simulation.py`)
```powershell
# Headless run
python scripts/run_simulation.py --controller max_pressure --scenario north_south_dominant --duration 180

# Native desktop GUI window with real-time animation
python scripts/run_simulation.py --controller dqn --scenario balanced --duration 180 --gui
```
- Executes closed-loop simulation with the specified controller.
- Prints summary KPIs (throughput, queue, delay, fairness).
- Automatically saves CSV time-series and JSON run manifest to `data/runs/`.

### 2.4 DQN Reinforcement Learning Training (`scripts/train_agent.py`)
```powershell
python scripts/train_agent.py --timesteps 5000 --seed 42 --scenario balanced --device cpu
```
- Trains Stable-Baselines3 DQN policy over `TrafficSignalEnv`.
- Logs progress telemetry to `artifacts/models/training_progress.json`.
- Saves validated policy checkpoint to `artifacts/models/dqn_best.zip`.

### 2.5 Multi-Controller Benchmarking (`scripts/evaluate_agent.py`)
```powershell
python scripts/evaluate_agent.py --duration 180 --seeds 101 202
```
- Executes full-factorial comparison across Fixed-Time, Actuated, Max-Pressure, and DQN.
- Exports results to `data/processed/benchmark_results.csv` and `data/processed/benchmark_results.json`.
- Prints formatted comparison summary table to console.

### 2.6 Perception Demo Video Generator (`scripts/make_demo_video.py`)
```powershell
python scripts/make_demo_video.py --seconds 30 --fps 10.0 --output artifacts/videos/perception_demo.mp4
```
- Renders virtual intersection camera frames tick-by-tick.
- Runs YOLOv8n object detection, spatial IoU tracking, and approach ROI assignment.
- Encodes annotated frames with HUD telemetry into an `.mp4` video.

---

## 3. Desktop Real-Time Animation Mode (`gui-settings.cfg.xml`)
When running simulations with `--gui`, SUMO-GUI uses the configuration defined in `simulation/gui-settings.cfg.xml`:
```xml
<viewsettings>
    <viewport zoom="800" x="250" y="250"/>
    <delay value="100"/>
</viewsettings>
```
- `zoom="800"` auto-centers on the intersection coordinates $(250, 250)$m upon opening.
- `delay="100"` adds 100 milliseconds of wall-clock delay between simulation steps, enabling real-time human observation of car-following behavior, lane queues, and signal phase changes.
