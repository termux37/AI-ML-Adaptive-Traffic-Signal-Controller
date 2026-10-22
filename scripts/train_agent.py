"""CLI script to train DQN traffic signal controller."""

import argparse
from pathlib import Path
from traffic_ai.config.schemas import ScenarioName
from traffic_ai.training.train_dqn import train_dqn


def main():
    parser = argparse.ArgumentParser(description="Train DQN Traffic Signal Controller")
    parser.add_argument("--timesteps", type=int, default=3000, help="Total training timesteps")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for environment and training")
    parser.add_argument(
        "--scenario",
        type=str,
        default="balanced",
        choices=[s.value for s in ScenarioName],
        help="Training demand scenario",
    )
    parser.add_argument("--device", type=str, default="cpu", help="Torch device ('cpu' or 'cuda')")
    args = parser.parse_args()

    scenario_enum = ScenarioName(args.scenario)
    model_path = train_dqn(
        total_timesteps=args.timesteps,
        seed=args.seed,
        scenario_name=scenario_enum,
        device=args.device,
    )
    print(f"Training completed successfully. Model artifact saved at: {model_path}")


if __name__ == "__main__":
    main()
