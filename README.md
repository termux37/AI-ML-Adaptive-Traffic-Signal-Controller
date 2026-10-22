# AI & ML Based Adaptive Traffic Control System

**Virtual Research & Operations Platform for Intelligent Traffic Signal Control**

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![SUMO 1.27.1](https://img.shields.io/badge/SUMO-1.27.1-green.svg)](https://eclipse.dev/sumo/)
[![Tests Passing](https://img.shields.io/badge/Tests-15%20Passed-brightgreen.svg)]()
[![Platform: Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> ⚠️ **DISCLAIMER:**  
> This system is an academic simulation and virtual research demonstration. It operates entirely within the Eclipse SUMO microscopic simulation environment and is **NOT certified for real-world physical traffic control or physical municipal infrastructure**.

---

## 🚦 System Highlights
- **Microscopic Traffic Simulation:** High-fidelity 4-way intersection (`junction_center`) with 2 incoming and 2 outgoing lanes per approach, dedicated turn bays, Krauss car-following physics, and induction loop detectors.
- **Deterministic Signal Safety Manager:** Decoupled safety guard that prevents conflicting greens, strictly enforces minimum green (10s), maximum green (60s), yellow clearance (3s), and all-red clearance intervals (2s).
- **Four Distinct Control Regimes:**
  1. *Fixed-Time:* Standard pre-timed cyclic baseline (90s cycle).
  2. *Vehicle-Actuated:* Demand-responsive extension with gap-out threshold (3.0s) and max-green bounds.
  3. *Max-Pressure:* Optimal decentralized queue differential heuristic (Varaiya 2013 / PressLight KDD 2019).
  4. *Deep Q-Network (DQN):* Deep reinforcement learning policy (Stable-Baselines3 MlpPolicy) trained over a normalized 25-dimensional observation space.
- **Virtual-Camera Perception Pipeline:** Top-down virtual camera scene rendering with Ultralytics YOLOv8n object detection, multi-class vehicle identification (car, bus, truck, motorcycle), spatial IoU tracking, calibrated approach ROI polygon mapping, and live MAE error telemetry vs SUMO ground truth.
- **Operations Console Dashboard:** A mature, high-density dark operations-console interface built with Streamlit and Plotly across 11 fully functional pages.
- **Zero Fabricated Metrics:** Every number, chart, training curve, and benchmark result is produced directly by real simulation runs.

---

## 📋 System Prerequisites
- **Operating System:** Windows 10 / 11 (x64)
- **Python:** 3.10 – 3.12 (Tested on Python 3.12.10)
- **SUMO:** Eclipse SUMO >= 1.20 (Tested on SUMO 1.27.1 with `SUMO_HOME` configured)
- **RAM:** 16 GB system memory
- **GPU (Optional):** NVIDIA GPU supported; defaults to CPU for fast TraCI simulation IPC

---

## ⚡ One-Click Master Launchers

To execute all setup, verification, testing, and benchmarking tasks in sequence and launch the platform:

### Option A: Python Master Launcher (Recommended)
```powershell
python launch.py
```
*Executes environment check, network verification, automated test suite (15 tests), artifact validation, and opens the Operations Console in your browser.*

### Option B: Windows Batch Launcher
Double-click [`launch.bat`](launch.bat) or run from Command Prompt:
```cmd
launch.bat
```

### Option C: Windows PowerShell Launcher
```powershell
.\launch.ps1
```

### Option D: Real-Time Desktop SUMO-GUI Animation
To watch microscopic vehicle physics, lane changes, and signals animated in desktop SUMO-GUI:
```powershell
python launch.py --gui
```

---

## ⚡ Manual Quickstart

### 1. Run Automated Environment Smoke Test
```powershell
python scripts/check_environment.py
```

### 2. Launch the Operations Console Dashboard
```powershell
streamlit run app.py
```
*Open `http://localhost:8501` in your browser.*

---

## 🛠️ CLI Operations & Reproducibility Commands

### Run Full Test Suite (15 Tests)
```powershell
python -m pytest tests/ -v
```

### Train DQN Reinforcement Learning Agent
```powershell
$env:PYTHONPATH = "src"
python scripts/train_agent.py --timesteps 3000 --seed 42 --scenario balanced --device cpu
```

### Run Multi-Controller Benchmark Comparison
```powershell
$env:PYTHONPATH = "src"
python scripts/evaluate_agent.py --duration 180 --seeds 101 202
```

### Generate Perception Demo Video
```powershell
$env:PYTHONPATH = "src"
python scripts/make_demo_video.py --seconds 30 --fps 10.0 --output artifacts/videos/perception_demo.mp4
```

### Run Standalone Simulation Run
```powershell
$env:PYTHONPATH = "src"
python scripts/run_simulation.py --controller max_pressure --scenario north_south_dominant --duration 120
```

---

## 📊 Measured Benchmark Results (Excerpt)

Evaluated under identical synthetic demand seeds ($seed = 101$):

| Scenario | Controller | Throughput (vph) | Avg Queue (veh) | Avg Wait (s) | Fairness Index |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Balanced** | Fixed-Time | 840.0 | 7.77 | 126.3 | 0.84 |
| | Vehicle-Actuated | 900.0 | 7.38 | 124.7 | 0.73 |
| | **Max-Pressure** | **1,080.0** | **3.93** | **70.7** | 0.58 |
| | DQN Policy | 60.0 | 18.63 | 449.5 | 0.78 |
| **North-South Dominant** | Fixed-Time | 360.0 | 11.78 | 199.0 | 0.50 |
| | Vehicle-Actuated | 660.0 | 7.83 | 109.1 | 0.58 |
| | **Max-Pressure** | **1,080.0** | **2.67** | **36.9** | 0.43 |
| | **DQN Policy** | 840.0 | 7.93 | 107.2 | **0.88** |

*Note: In the directional imbalance scenario (`north_south_dominant`), DQN achieved 840 vph (+133% over Fixed-Time baseline) while attaining the highest cross-approach fairness index (0.88).*

---

## 📁 Repository Structure
```text
ai_ml_project/
├── app.py                          # Streamlit operations console entry point
├── pyproject.toml                  # Project packaging and pytest settings
├── README.md                       # Master project guide
├── LICENSE                         # MIT License
├── .gitignore                      # Git ignore rules for Python, SUMO, PyTorch
├── .env.example                    # Environment variable template
├── launch.py                       # Unified master launcher (Python)
├── launch.bat                      # One-click Windows batch launcher
├── launch.ps1                      # Windows PowerShell launcher
├── configs/
│   ├── app.yaml                    # Dashboard settings
│   ├── simulation.yaml             # SUMO network & runtime config
│   ├── perception.yaml             # YOLO & ROI config
│   ├── rl.yaml                     # DQN hyperparameters & reward weights
│   └── experiments.yaml            # Benchmark definitions
├── simulation/
│   ├── network/                    # Nodes, edges, connections, net.xml, detectors
│   ├── routes/                     # Generated route demand profiles
│   ├── scenario.sumocfg            # SUMO simulation configuration
│   └── gui-settings.cfg.xml        # Viewport zoom and animation delay settings
├── src/traffic_ai/
│   ├── config/schemas.py           # Pydantic data contracts
│   ├── simulation/                 # TraCI runner & scenario manager
│   ├── control/                    # Safety manager, phase catalog & controllers
│   ├── perception/                 # YOLO detector, tracker, calibration, pipeline
│   ├── state/                      # Ground truth adapter & observation schemas
│   ├── metrics/                    # Metrics collector & manifest builder
│   ├── training/                   # Gymnasium env, DQN training & callbacks
│   ├── experiments/                # Batch benchmark runner
│   ├── dashboard/                  # Multi-page dashboard modules & dark theme
│   └── utils/                      # Structured logging & diagnostics
├── scripts/
│   ├── check_environment.py        # Automated smoke test script
│   ├── generate_scenario.py        # Route generator CLI
│   ├── run_simulation.py           # Simulation runner CLI
│   ├── train_agent.py              # DQN training CLI
│   ├── evaluate_agent.py           # Benchmark evaluation CLI
│   └── make_demo_video.py          # Perception demo video generator
└── tests/
    ├── unit/                       # Unit tests (safety, env, perception)
    ├── integration/                # End-to-end simulation tests
    └── smoke/                      # Automated smoke check tests
```
