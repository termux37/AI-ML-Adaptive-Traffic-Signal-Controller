"""Integration tests for end-to-end simulation, controllers, and artifacts."""

import json
from pathlib import Path
import pytest

from traffic_ai.config.schemas import ScenarioConfig, ScenarioName, SimulationConfig
from traffic_ai.control.actuated import ActuatedController
from traffic_ai.control.dqn_policy import DQNController
from traffic_ai.control.fixed_time import FixedTimeController
from traffic_ai.control.max_pressure import MaxPressureController
from traffic_ai.simulation.runner import SimulationRunner


@pytest.mark.parametrize("controller_cls", [
    FixedTimeController,
    ActuatedController,
    MaxPressureController,
])
def test_controller_end_to_end_execution(controller_cls, tmp_path):
    scenario = ScenarioConfig(name=ScenarioName.LOW, seed=77, duration_seconds=60, warmup_seconds=10)
    sim_cfg = SimulationConfig(gui=False, output_dir=str(tmp_path))
    ctrl = controller_cls()

    run_id = f"test_{ctrl.name}_int"
    with SimulationRunner(
        scenario_config=scenario,
        controller=ctrl,
        simulation_config=sim_cfg,
        run_id=run_id,
    ) as runner:
        summary = runner.run_until(60.0)

    assert "throughput_vph" in summary
    assert "average_queue_length" in summary
    assert "jains_fairness_index" in summary

    # Verify artifacts
    csv_file = tmp_path / f"{run_id}_timeseries.csv"
    manifest_file = tmp_path / f"{run_id}_manifest.json"

    assert csv_file.exists()
    assert manifest_file.exists()

    with open(manifest_file, "r") as f:
        manifest_data = json.load(f)
    assert manifest_data["run_id"] == run_id
    assert manifest_data["metadata"]["controller"] == ctrl.name
