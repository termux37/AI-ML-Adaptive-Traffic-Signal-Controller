"""Automated smoke test and environment verification script."""

import os
import sys
from pathlib import Path

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def check_prerequisites() -> bool:
    print("=" * 60)
    print("Adaptive Traffic Control System - Environment Smoke Test")
    print("=" * 60)

    all_passed = True

    # 1. Check Python version
    py_ver = sys.version_info
    print(f"[CHECK] Python version: {py_ver.major}.{py_ver.minor}.{py_ver.micro}")
    if py_ver < (3, 10):
        print("  [FAIL] Python >= 3.10 required.")
        all_passed = False
    else:
        print("  [PASS] Python version compatible.")

    # 2. Check SUMO and SUMO_HOME
    sumo_home = os.environ.get("SUMO_HOME")
    print(f"[CHECK] SUMO_HOME: {sumo_home}")
    if not sumo_home or not Path(sumo_home).exists():
        print("  [FAIL] SUMO_HOME not configured or does not exist.")
        all_passed = False
    else:
        print("  [PASS] SUMO_HOME verified.")

    # 3. Check TraCI and SUMO binaries
    try:
        import traci
        import sumolib
        print(f"  [PASS] TraCI version {traci.__version__} & sumolib {sumolib.__version__} imported.")
    except Exception as e:
        print(f"  [FAIL] Error importing TraCI/sumolib: {e}")
        all_passed = False

    # 4. Check ML / CV packages
    try:
        import torch
        import gymnasium
        import stable_baselines3
        import ultralytics
        import cv2
        import streamlit
        import plotly
        import pandas
        import numpy
        print("  [PASS] All PyTorch, Gymnasium, Stable-Baselines3, YOLO, OpenCV, and Streamlit packages imported.")
    except Exception as e:
        print(f"  [FAIL] Missing ML package: {e}")
        all_passed = False

    # 5. Execute 60-second headless simulation smoke run
    print("\n[SMOKE RUN] Executing 60-second headless SUMO simulation...")
    try:
        from traffic_ai.config.schemas import ScenarioConfig, ScenarioName, SimulationConfig
        from traffic_ai.control.fixed_time import FixedTimeController
        from traffic_ai.simulation.runner import SimulationRunner

        cfg = ScenarioConfig(name=ScenarioName.BALANCED, seed=42, duration_seconds=60, warmup_seconds=10)
        sim_cfg = SimulationConfig(gui=False, output_dir="data/runs")
        ctrl = FixedTimeController()

        with SimulationRunner(scenario_config=cfg, controller=ctrl, simulation_config=sim_cfg, run_id="smoke_test_run") as sim:
            summary = sim.run_until(60.0)

        print(f"  [PASS] Simulation executed 60s cleanly! Throughput: {summary.get('throughput_vph', 0)} vph, Avg Queue: {summary.get('average_queue_length', 0):.2f}")
    except Exception as e:
        print(f"  [FAIL] Smoke simulation execution failed: {e}")
        all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("RESULT: ALL ENVIRONMENT PREREQUISITES AND SMOKE TESTS PASSED!")
        print("=" * 60)
        return True
    else:
        print("RESULT: SMOKE TEST FAILED - CHECK DIAGNOSTIC LOGS ABOVE.")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = check_prerequisites()
    sys.exit(0 if success else 1)
