# AI & ML Based Adaptive Traffic Control System - Master Technical Documentation

Welcome to the comprehensive technical documentation for **AI & ML Based Adaptive Traffic Control System**, an engineering and research platform for AI-driven adaptive traffic signal control operating within Eclipse SUMO.

This directory contains modular reference manuals detailing system architecture, simulation mechanics, safety guarantees, machine learning formulations, computer vision pipelines, and testing procedures.

---

## 📚 Documentation Index

| Module | Title | Primary Focus & Contents |
| :---: | :--- | :--- |
| [**Module 01**](01_SYSTEM_OVERVIEW_AND_ARCHITECTURE.md) | **System Overview & Architecture** | Platform vision, high-level architecture diagram, directory layout, modular responsibilities, and data flow. |
| [**Module 02**](02_SIMULATION_AND_NETWORK_MODULE.md) | **Simulation & Road Network** | SUMO microscopic modeling, 4-way intersection geometry, 16 link movements, induction loops, and demand generation. |
| [**Module 03**](03_DETERMINISTIC_SAFETY_MANAGER.md) | **Deterministic Safety Manager** | Policy decoupling, clearance intervals (yellow 3s, red 2s), min/max green guards, conflict matrix, and fail-safes. |
| [**Module 04**](04_CONTROLLER_REGIMES_AND_ALGORITHMS.md) | **Controller Regimes & Algorithms** | Fixed-Time, Vehicle-Actuated, Max-Pressure (KDD 2019), and Deep Q-Network (DQN) with 25-dim state & reward formulas. |
| [**Module 05**](05_VIRTUAL_CAMERA_AND_YOLO_PERCEPTION.md) | **Virtual Camera & YOLO Perception** | Top-down scene rendering, YOLOv8n object detection, spatial IoU tracking, approach polygon calibration, and MAE error telemetry. |
| [**Module 06**](06_METRICS_ANALYTICS_AND_BENCHMARKING.md) | **Metrics, Analytics & Benchmarking** | Mathematical formulas, units, warmup exclusion, run manifest JSON schema, and empirical multi-controller benchmark results. |
| [**Module 07**](07_OPERATIONS_CONSOLE_DASHBOARD.md) | **Operations Console Dashboard** | Streamlit dark operations theme, in-browser real-time streaming, and detailed walkthrough of all 11 dashboard pages. |
| [**Module 08**](08_SCRIPTS_AND_LAUNCHERS.md) | **Scripts & Master Launchers** | Single-launch orchestrators (`launch.py`, `launch.bat`, `launch.ps1`), standalone CLI tools, and desktop SUMO-GUI animation mode. |
| [**Module 09**](09_TESTING_AND_VERIFICATION.md) | **Testing & Verification Suite** | Pytest test suite breakdown (15 tests: unit, integration, safety, smoke), quality gates, and verified terminal execution evidence. |

---

## 🧭 Role-Based Reading Paths

### For Software Architects & System Engineers
1. [Module 01: System Overview & Architecture](01_SYSTEM_OVERVIEW_AND_ARCHITECTURE.md)
2. [Module 03: Deterministic Safety Manager](03_DETERMINISTIC_SAFETY_MANAGER.md)
3. [Module 08: Scripts & Master Launchers](08_SCRIPTS_AND_LAUNCHERS.md)

### For Traffic Engineers & Simulation Specialists
1. [Module 02: Simulation & Road Network](02_SIMULATION_AND_NETWORK_MODULE.md)
2. [Module 03: Deterministic Safety Manager](03_DETERMINISTIC_SAFETY_MANAGER.md)
3. [Module 04: Controller Regimes & Algorithms](04_CONTROLLER_REGIMES_AND_ALGORITHMS.md)
4. [Module 06: Metrics, Analytics & Benchmarking](06_METRICS_ANALYTICS_AND_BENCHMARKING.md)

### For AI/ML & Computer Vision Engineers
1. [Module 04: Controller Regimes & Algorithms (DQN & Max-Pressure)](04_CONTROLLER_REGIMES_AND_ALGORITHMS.md)
2. [Module 05: Virtual Camera & YOLO Perception](05_VIRTUAL_CAMERA_AND_YOLO_PERCEPTION.md)
3. [Module 06: Metrics, Analytics & Benchmarking](06_METRICS_ANALYTICS_AND_BENCHMARKING.md)

### For QA Engineers & Operators
1. [Module 07: Operations Console Dashboard](07_OPERATIONS_CONSOLE_DASHBOARD.md)
2. [Module 08: Scripts & Master Launchers](08_SCRIPTS_AND_LAUNCHERS.md)
3. [Module 09: Testing & Verification Suite](09_TESTING_AND_VERIFICATION.md)

---

## ⚡ Quick Verification Commands
```powershell
# Run full automated test suite (15 tests)
python -m pytest tests/ -v

# Run system audit and launch operations console
python launch.py

# Launch desktop real-time SUMO-GUI animation
python launch.py --gui
```
