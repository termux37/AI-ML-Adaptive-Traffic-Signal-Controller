"""DQN training pipeline for traffic signal control."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from stable_baselines3 import DQN
from stable_baselines3.common.callbacks import CheckpointCallback

from traffic_ai.config.schemas import ScenarioConfig, ScenarioName, SimulationConfig
from traffic_ai.simulation.scenario_manager import ScenarioManager
from traffic_ai.training.callbacks import TrainingProgressCallback
from traffic_ai.training.environment import TrafficSignalEnv
from traffic_ai.utils.logging import setup_logger


def train_dqn(
    total_timesteps: int = 5000,
    seed: int = 42,
    scenario_name: ScenarioName = ScenarioName.BALANCED,
    model_output_dir: Path = Path("artifacts/models"),
    device: str = "cpu",
) -> Path:
    """Trains a DQN agent on the single-junction environment and saves checkpoints."""
    model_output_dir.mkdir(parents=True, exist_ok=True)
    logger = setup_logger("train_dqn", log_dir=Path("data/runs"))

    logger.info(f"Initiating DQN training: {total_timesteps} timesteps, seed={seed}, scenario={scenario_name.value}")

    # Load RL config if available
    rl_cfg_path = Path("configs/rl.yaml")
    rl_config = {}
    if rl_cfg_path.exists():
        with open(rl_cfg_path, "r", encoding="utf-8") as f:
            rl_config = yaml.safe_load(f) or {}

    learning_rate = rl_config.get("learning_rate", 0.0005)
    buffer_size = rl_config.get("buffer_size", 20000)
    batch_size = rl_config.get("batch_size", 64)
    gamma = rl_config.get("gamma", 0.99)
    train_freq = rl_config.get("train_freq", 4)
    target_update_interval = rl_config.get("target_update_interval", 500)
    learning_starts = rl_config.get("learning_starts", 200)

    # Build Training Environment
    scenario = ScenarioManager.get_preset_config(
        scenario_name=scenario_name,
        seed=seed,
        duration=1800,  # 30 minutes simulation episodes
    )
    sim_cfg = SimulationConfig(gui=False, output_dir="data/runs")

    env = TrafficSignalEnv(
        scenario_config=scenario,
        sim_config=sim_cfg,
        decision_interval=5.0,
    )

    # Initialize DQN model
    policy_kwargs = dict(net_arch=[128, 128])
    model = DQN(
        policy="MlpPolicy",
        env=env,
        learning_rate=learning_rate,
        buffer_size=buffer_size,
        learning_starts=learning_starts,
        batch_size=batch_size,
        tau=1.0,
        gamma=gamma,
        train_freq=train_freq,
        gradient_steps=1,
        target_update_interval=target_update_interval,
        exploration_fraction=0.3,
        exploration_initial_eps=1.0,
        exploration_final_eps=0.05,
        policy_kwargs=policy_kwargs,
        device=device,
        seed=seed,
        verbose=1,
    )

    # Progress tracking callback
    progress_cb = TrainingProgressCallback(
        log_path=model_output_dir / "training_progress.json",
        check_freq=25,
    )

    try:
        model.learn(
            total_timesteps=total_timesteps,
            callback=[progress_cb],
            progress_bar=False,
        )
    finally:
        env.close()

    # Save final model
    best_model_path = model_output_dir / "dqn_best.zip"
    model.save(str(best_model_path))
    logger.info(f"Model saved successfully to {best_model_path}")

    # Save metadata
    metadata = {
        "model_name": "DQN_MlpPolicy",
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "total_timesteps": total_timesteps,
        "seed": seed,
        "scenario": scenario_name.value,
        "observation_dim": 25,
        "action_dim": 4,
        "device": device,
        "net_arch": [128, 128],
        "hyperparameters": {
            "learning_rate": learning_rate,
            "buffer_size": buffer_size,
            "batch_size": batch_size,
            "gamma": gamma,
            "train_freq": train_freq,
            "target_update_interval": target_update_interval,
        },
    }
    with open(model_output_dir / "dqn_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    return best_model_path


if __name__ == "__main__":
    train_dqn(total_timesteps=2000, seed=42)
