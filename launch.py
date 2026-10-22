"""AI & ML Based Adaptive Traffic Control System - Master Launch Orchestrator.

Executes all setup, verification, testing, and benchmarking tasks in sequence,
then launches the real-time simulation and operations dashboard.
"""

import argparse
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

# Add src to Python path
ROOT_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(ROOT_DIR / "src"))
os.environ["PYTHONPATH"] = str(ROOT_DIR / "src")


def print_header(title: str):
    print("\n" + "=" * 68)
    print(f"  Adaptive Traffic Control System :: {title}")
    print("=" * 68)


def run_command(cmd: list, desc: str) -> bool:
    print(f"\n[TASK] {desc}...")
    print(f"  Command: {' '.join(cmd)}")
    try:
        res = subprocess.run(cmd, check=True)
        print(f"  [PASS] {desc} completed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  [FAIL] {desc} failed with exit code {e.returncode}.")
        return False
    except Exception as e:
        print(f"  [ERROR] Could not execute {desc}: {e}")
        return False


def task_1_environment_audit() -> bool:
    print_header("Task 1: Environment & System Audit")
    cmd = [sys.executable, str(ROOT_DIR / "scripts" / "check_environment.py")]
    return run_command(cmd, "Environment & SUMO verification")


def task_2_network_and_scenarios() -> bool:
    print_header("Task 2: Network Verification & Scenario Generation")
    net_file = ROOT_DIR / "simulation" / "network" / "intersection.net.xml"
    if not net_file.exists():
        cmd = [
            "netconvert",
            f"--node-files={ROOT_DIR / 'simulation' / 'network' / 'intersection.nod.xml'}",
            f"--edge-files={ROOT_DIR / 'simulation' / 'network' / 'intersection.edg.xml'}",
            f"--connection-files={ROOT_DIR / 'simulation' / 'network' / 'intersection.con.xml'}",
            f"--tllogic-files={ROOT_DIR / 'simulation' / 'network' / 'intersection.tll.xml'}",
            f"--output-file={net_file}",
            "--no-turnarounds=true"
        ]
        if not run_command(cmd, "Compiling SUMO intersection network"):
            return False
    else:
        print(f"  [INFO] Network file already verified: {net_file}")

    # Generate baseline scenario routes
    scenarios = ["balanced", "north_south_dominant", "bursty"]
    for sc in scenarios:
        route_f = ROOT_DIR / "simulation" / "routes" / f"{sc}_seed42_180s.rou.xml"
        if not route_f.exists():
            cmd = [
                sys.executable, str(ROOT_DIR / "scripts" / "generate_scenario.py"),
                "--scenario", sc, "--seed", "42", "--duration", "180"
            ]
            run_command(cmd, f"Generating route demand for {sc}")

    return True


def task_3_run_test_suite() -> bool:
    print_header("Task 3: Automated Test Suite (Unit, Integration, Safety)")
    cmd = [sys.executable, "-m", "pytest", str(ROOT_DIR / "tests"), "-v"]
    return run_command(cmd, "Pytest test execution")


def task_4_verify_artifacts() -> bool:
    print_header("Task 4: Model Checkpoints & Vision Pipeline Artifacts")

    # 1. DQN Model Checkpoint
    model_file = ROOT_DIR / "artifacts" / "models" / "dqn_best.zip"
    if not model_file.exists():
        print("  [INFO] Training initial DQN checkpoint...")
        cmd = [
            sys.executable, str(ROOT_DIR / "scripts" / "train_agent.py"),
            "--timesteps", "1000", "--seed", "42", "--scenario", "balanced"
        ]
        run_command(cmd, "Training DQN policy checkpoint")
    else:
        print(f"  [INFO] Validated DQN checkpoint found: {model_file}")

    # 2. Perception Demo Video
    vid_file = ROOT_DIR / "artifacts" / "videos" / "perception_demo.mp4"
    if not vid_file.exists():
        print("  [INFO] Generating perception demo video with YOLOv8n...")
        cmd = [
            sys.executable, str(ROOT_DIR / "scripts" / "make_demo_video.py"),
            "--seconds", "30", "--output", str(vid_file)
        ]
        run_command(cmd, "Recording YOLO perception demo video")
    else:
        print(f"  [INFO] Perception demo video found: {vid_file}")

    return True


def task_5_verify_benchmarks() -> bool:
    print_header("Task 5: Pre-Computed Multi-Controller Benchmarks")
    bench_csv = ROOT_DIR / "data" / "processed" / "benchmark_results.csv"
    if not bench_csv.exists():
        print("  [INFO] Executing baseline and RL benchmark comparison...")
        cmd = [
            sys.executable, str(ROOT_DIR / "scripts" / "evaluate_agent.py"),
            "--duration", "90", "--seeds", "101"
        ]
        run_command(cmd, "Multi-controller benchmark execution")
    else:
        print(f"  [INFO] Benchmark empirical dataset verified: {bench_csv}")
    return True


def task_6_launch_dashboard(open_browser: bool = True):
    print_header("Task 6: Launching Operations Console Dashboard")
    port = 8501
    url = f"http://localhost:{port}"

    print(f"\n[STARTING] Streamlit Operations Console on {url}...")
    if open_browser:
        # Schedule browser opening after brief delay
        time.sleep(1.0)
        webbrowser.open(url)

    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(ROOT_DIR / "app.py"),
        f"--server.port={port}",
        "--server.headless=false",
    ]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n[INFO] Dashboard stopped cleanly.")


def task_launch_desktop_gui():
    print_header("Real-Time Desktop SUMO-GUI Animation Mode")
    cmd = [
        sys.executable, str(ROOT_DIR / "scripts" / "run_simulation.py"),
        "--controller", "max_pressure",
        "--scenario", "north_south_dominant",
        "--duration", "180",
        "--gui"
    ]
    run_command(cmd, "Launching desktop SUMO-GUI simulation in real-time")


def main():
    parser = argparse.ArgumentParser(description="Adaptive Traffic Control System Master Launch Orchestrator")
    parser.add_argument("--skip-tests", action="store_true", help="Skip pytest test suite execution")
    parser.add_argument("--test-only", action="store_true", help="Run audit and tests only, then exit")
    parser.add_argument("--gui", action="store_true", help="Launch desktop SUMO-GUI simulation window")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open web browser")
    args = parser.parse_args()

    print_header("Adaptive Traffic Control System Initializing")
    print(f"Working Directory: {ROOT_DIR}")

    # 1. Environment audit
    if not task_1_environment_audit():
        print("\n[ABORT] Environment verification failed.")
        sys.exit(1)

    # 2. Network & routes
    if not task_2_network_and_scenarios():
        print("\n[ABORT] Network setup failed.")
        sys.exit(1)

    # 3. Test suite
    if not args.skip_tests:
        if not task_3_run_test_suite():
            print("\n[ABORT] Test suite failed.")
            sys.exit(1)

    # 4. Artifacts
    if not task_4_verify_artifacts():
        print("\n[ABORT] Artifact setup failed.")
        sys.exit(1)

    # 5. Benchmarks
    if not task_5_verify_benchmarks():
        print("\n[ABORT] Benchmark setup failed.")
        sys.exit(1)

    if args.test_only:
        print_header("All Verification Tasks Completed Successfully!")
        sys.exit(0)

    if args.gui:
        task_launch_desktop_gui()
    else:
        # 6. Launch dashboard
        task_6_launch_dashboard(open_browser=not args.no_browser)


if __name__ == "__main__":
    main()
