"""CLI script to generate reproducible SUMO route scenarios."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from traffic_ai.config.schemas import ScenarioName
from traffic_ai.simulation.scenario_manager import ScenarioManager


def main():
    parser = argparse.ArgumentParser(description="Generate SUMO Traffic Scenario Route Files")
    parser.add_argument(
        "--scenario",
        type=str,
        default="balanced",
        choices=[s.value for s in ScenarioName],
        help="Scenario preset name",
    )
    parser.add_argument("--seed", type=int, default=42, help="Deterministic random seed")
    parser.add_argument("--duration", type=int, default=3600, help="Simulation duration in seconds")
    parser.add_argument("--output", type=str, default=None, help="Custom output path for rou.xml")
    args = parser.parse_args()

    scenario_enum = ScenarioName(args.scenario)
    cfg = ScenarioManager.get_preset_config(scenario_enum, seed=args.seed, duration=args.duration)

    if args.output:
        out_path = Path(args.output)
    else:
        out_path = Path(f"simulation/routes/{args.scenario}_seed{args.seed}_{args.duration}s.rou.xml")

    print(f"Generating scenario '{args.scenario}' (seed={args.seed}, duration={args.duration}s)...")
    ScenarioManager.generate_routes_file(cfg, out_path)
    print(f"Successfully generated: {out_path}")


if __name__ == "__main__":
    main()
