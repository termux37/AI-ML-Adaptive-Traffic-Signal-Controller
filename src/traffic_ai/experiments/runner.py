"""Batch experiment runner for reproducible controller benchmarking."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd

from traffic_ai.config.schemas import ScenarioConfig, ScenarioName, SimulationConfig
from traffic_ai.control.actuated import ActuatedController
from traffic_ai.control.dqn_policy import DQNController
from traffic_ai.control.fixed_time import FixedTimeController
from traffic_ai.control.max_pressure import MaxPressureController
from traffic_ai.simulation.runner import SimulationRunner
from traffic_ai.simulation.scenario_manager import ScenarioManager
from traffic_ai.utils.logging import setup_logger


class BenchmarkRunner:
    """Runs systematic experiments across controllers, scenarios, and seeds."""

    def __init__(
        self,
        output_dir: Path = Path("data/runs"),
        processed_dir: Path = Path("data/processed"),
    ):
        self.output_dir = output_dir
        self.processed_dir = processed_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.logger = setup_logger("benchmark_runner", log_dir=output_dir)

    def run_benchmark(
        self,
        scenarios: Optional[List[ScenarioName]] = None,
        controllers: Optional[List[str]] = None,
        seeds: Optional[List[int]] = None,
        duration_seconds: int = 180,
        warmup_seconds: int = 30,
    ) -> pd.DataFrame:
        """Executes full factorial evaluation across scenarios, controllers, and seeds."""
        scenarios = scenarios or [ScenarioName.BALANCED, ScenarioName.NORTH_SOUTH_DOMINANT]
        controllers = controllers or ["fixed_time", "actuated", "max_pressure", "dqn"]
        seeds = seeds or [101, 202]

        results: List[Dict[str, Any]] = []

        total_runs = len(scenarios) * len(controllers) * len(seeds)
        run_count = 0

        self.logger.info(f"Starting benchmark batch: {total_runs} total runs planned.")

        for sc_name in scenarios:
            for seed in seeds:
                # Same scenario configuration and demand for all controllers on this seed
                base_cfg = ScenarioManager.get_preset_config(sc_name, seed=seed, duration=duration_seconds)
                base_cfg.warmup_seconds = warmup_seconds

                for ctrl_name in controllers:
                    run_count += 1
                    run_id = f"bench_{sc_name.value}_{ctrl_name}_s{seed}"
                    self.logger.info(f"[{run_count}/{total_runs}] Running {ctrl_name} on {sc_name.value} (seed {seed})")

                    # Instantiate controller
                    if ctrl_name == "fixed_time":
                        ctrl = FixedTimeController()
                    elif ctrl_name == "actuated":
                        ctrl = ActuatedController()
                    elif ctrl_name == "max_pressure":
                        ctrl = MaxPressureController()
                    elif ctrl_name == "dqn":
                        ctrl = DQNController(model_path="artifacts/models/dqn_best.zip")
                    else:
                        raise ValueError(f"Unknown controller: {ctrl_name}")

                    sim_cfg = SimulationConfig(gui=False, output_dir=str(self.output_dir))

                    with SimulationRunner(
                        scenario_config=base_cfg,
                        controller=ctrl,
                        simulation_config=sim_cfg,
                        run_id=run_id,
                    ) as sim:
                        summary = sim.run_until(duration_seconds)

                    results.append({
                        "run_id": run_id,
                        "scenario": sc_name.value,
                        "controller": ctrl_name,
                        "seed": seed,
                        "duration_seconds": duration_seconds,
                        "throughput_vph": summary.get("throughput_vph", 0.0),
                        "total_completed": summary.get("total_completed_vehicles", 0),
                        "average_queue": summary.get("average_queue_length", 0.0),
                        "max_queue": summary.get("max_queue_length", 0),
                        "average_wait_s": summary.get("average_waiting_time_seconds", 0.0),
                        "max_wait_s": summary.get("max_wait_time_seconds", 0.0),
                        "phase_switches": summary.get("phase_switches_total", 0),
                        "fairness_index": summary.get("jains_fairness_index", 1.0),
                    })

        df = pd.DataFrame(results)

        # Calculate improvement percentage relative to fixed_time baseline
        csv_out = self.processed_dir / "benchmark_results.csv"
        json_out = self.processed_dir / "benchmark_results.json"

        df.to_csv(csv_out, index=False)
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)

        self.logger.info(f"Benchmark finished. Exported: {csv_out}")
        return df
