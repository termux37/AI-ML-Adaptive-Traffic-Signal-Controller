"""CLI evaluation script comparing baseline and RL controllers."""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from traffic_ai.config.schemas import ScenarioName
from traffic_ai.experiments.runner import BenchmarkRunner


def main():
    parser = argparse.ArgumentParser(description="Evaluate and Benchmark Traffic Controllers")
    parser.add_argument("--duration", type=int, default=180, help="Simulation duration per run in seconds")
    parser.add_argument("--seeds", type=int, nargs="+", default=[101, 202], help="Evaluation seeds")
    args = parser.parse_args()

    print(f"Running benchmark comparison: duration={args.duration}s, seeds={args.seeds}...")
    runner = BenchmarkRunner()
    df = runner.run_benchmark(
        scenarios=[ScenarioName.BALANCED, ScenarioName.NORTH_SOUTH_DOMINANT],
        controllers=["fixed_time", "actuated", "max_pressure", "dqn"],
        seeds=args.seeds,
        duration_seconds=args.duration,
    )

    print("\n=== BENCHMARK COMPARISON SUMMARY ===")
    summary = df.groupby(["scenario", "controller"])[
        ["throughput_vph", "average_queue", "max_queue", "average_wait_s", "fairness_index"]
    ].mean().round(2)
    print(summary.to_string())


if __name__ == "__main__":
    main()
