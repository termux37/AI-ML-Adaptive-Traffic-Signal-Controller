"""CLI script to run simulation with specified controller and scenario."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from traffic_ai.config.schemas import ScenarioConfig, ScenarioName, SimulationConfig
from traffic_ai.control.actuated import ActuatedController
from traffic_ai.control.dqn_policy import DQNController
from traffic_ai.control.fixed_time import FixedTimeController
from traffic_ai.control.max_pressure import MaxPressureController
from traffic_ai.simulation.runner import SimulationRunner
from traffic_ai.simulation.scenario_manager import ScenarioManager


def main():
    parser = argparse.ArgumentParser(description="Run Adaptive Traffic Simulation")
    parser.add_argument(
        "--controller",
        type=str,
        default="fixed_time",
        choices=["fixed_time", "actuated", "max_pressure", "dqn"],
        help="Signal controller type",
    )
    parser.add_argument(
        "--scenario",
        type=str,
        default="balanced",
        choices=[s.value for s in ScenarioName],
        help="Demand scenario name",
    )
    parser.add_argument("--seed", type=int, default=42, help="Simulation random seed")
    parser.add_argument("--duration", type=int, default=180, help="Simulation duration in seconds")
    parser.add_argument("--warmup", type=int, default=30, help="Warmup duration in seconds")
    parser.add_argument("--gui", action="store_true", help="Launch with SUMO-GUI")
    args = parser.parse_args()

    scenario_cfg = ScenarioManager.get_preset_config(
        ScenarioName(args.scenario),
        seed=args.seed,
        duration=args.duration,
    )
    scenario_cfg.warmup_seconds = args.warmup

    sim_cfg = SimulationConfig(gui=args.gui, output_dir="data/runs")

    if args.controller == "fixed_time":
        ctrl = FixedTimeController()
    elif args.controller == "actuated":
        ctrl = ActuatedController()
    elif args.controller == "max_pressure":
        ctrl = MaxPressureController()
    elif args.controller == "dqn":
        ctrl = DQNController(model_path="artifacts/models/dqn_best.zip")
    else:
        ctrl = FixedTimeController()

    run_id = f"cli_{args.scenario}_{args.controller}_s{args.seed}"
    print(f"Launching simulation '{run_id}' [GUI: {args.gui}]...")

    with SimulationRunner(
        scenario_config=scenario_cfg,
        controller=ctrl,
        simulation_config=sim_cfg,
        run_id=run_id,
    ) as sim:
        summary = sim.run_until(args.duration)

    print("\nSimulation Run Complete!")
    print(f"Throughput: {summary.get('throughput_vph', 0)} vph")
    print(f"Average Queue: {summary.get('average_queue_length', 0):.2f} vehicles")
    print(f"Average Wait: {summary.get('average_waiting_time_seconds', 0):.2f} s")
    print(f"Phase Switches: {summary.get('phase_switches_total', 0)}")
    print(f"Fairness Index: {summary.get('jains_fairness_index', 1.0):.4f}")


if __name__ == "__main__":
    main()
