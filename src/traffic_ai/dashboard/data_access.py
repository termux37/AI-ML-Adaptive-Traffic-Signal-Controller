"""Data access and simulation invocation layer for the dashboard."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import pandas as pd

from traffic_ai.config.schemas import ScenarioConfig, ScenarioName, SimulationConfig
from traffic_ai.control.actuated import ActuatedController
from traffic_ai.control.dqn_policy import DQNController
from traffic_ai.control.fixed_time import FixedTimeController
from traffic_ai.control.max_pressure import MaxPressureController
from traffic_ai.simulation.runner import SimulationRunner
from traffic_ai.simulation.scenario_manager import ScenarioManager


def load_available_runs(runs_dir: Path = Path("data/runs")) -> List[Dict[str, Any]]:
    """Scans data/runs for completed run manifests."""
    if not runs_dir.exists():
        return []

    manifests = []
    for f in runs_dir.glob("*_manifest.json"):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                manifests.append(data)
        except Exception:
            pass

    # Sort descending by generated_at
    manifests.sort(key=lambda m: m.get("generated_at", ""), reverse=True)
    return manifests


def load_run_timeseries(run_id: str, runs_dir: Path = Path("data/runs")) -> Optional[pd.DataFrame]:
    """Loads step-by-step metrics timeseries CSV for a given run ID."""
    csv_path = runs_dir / f"{run_id}_timeseries.csv"
    if not csv_path.exists():
        return None
    try:
        return pd.read_csv(csv_path)
    except Exception:
        return None


def load_benchmark_data(processed_dir: Path = Path("data/processed")) -> Optional[pd.DataFrame]:
    """Loads aggregated benchmark results CSV."""
    csv_path = processed_dir / "benchmark_results.csv"
    if not csv_path.exists():
        return None
    try:
        return pd.read_csv(csv_path)
    except Exception:
        return None


def load_training_progress(model_dir: Path = Path("artifacts/models")) -> Dict[str, Any]:
    """Reads live/saved training telemetry JSON."""
    prog_path = model_dir / "training_progress.json"
    if not prog_path.exists():
        return {"status": "NO_TRAINING_DATA", "timesteps_completed": 0, "history": {}}
    try:
        with open(prog_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"status": "ERROR_READING_FILE"}


def load_model_metadata(model_dir: Path = Path("artifacts/models")) -> Dict[str, Any]:
    """Reads model architecture and hyperparameter metadata."""
    meta_path = model_dir / "dqn_metadata.json"
    if not meta_path.exists():
        return {}
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def run_live_simulation(
    scenario_name: ScenarioName,
    controller_type: str,
    seed: int = 42,
    duration: int = 120,
    warmup: int = 20,
) -> Dict[str, Any]:
    """Launches a controlled simulation run and returns summary metrics."""
    scenario_cfg = ScenarioManager.get_preset_config(scenario_name, seed=seed, duration=duration)
    scenario_cfg.warmup_seconds = warmup
    sim_cfg = SimulationConfig(gui=False, output_dir="data/runs")

    run_id = f"live_{scenario_name.value}_{controller_type}_s{seed}"

    if controller_type == "fixed_time":
        ctrl = FixedTimeController()
    elif controller_type == "actuated":
        ctrl = ActuatedController()
    elif controller_type == "max_pressure":
        ctrl = MaxPressureController()
    elif controller_type == "dqn":
        ctrl = DQNController(model_path="artifacts/models/dqn_best.zip")
    else:
        ctrl = FixedTimeController()

    with SimulationRunner(
        scenario_config=scenario_cfg,
        controller=ctrl,
        simulation_config=sim_cfg,
        run_id=run_id,
    ) as runner:
        summary = runner.run_until(duration)

    return {
        "run_id": run_id,
        "summary": summary,
        "scenario": scenario_name.value,
        "controller": controller_type,
    }
