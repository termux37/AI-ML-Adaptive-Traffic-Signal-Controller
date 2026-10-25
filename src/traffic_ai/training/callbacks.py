"""Training callbacks for progress logging and checkpoint evaluation."""

import json
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
from stable_baselines3.common.callbacks import BaseCallback


class TrainingProgressCallback(BaseCallback):
    """Logs real training progress, episodic returns, and saves live JSON status for the dashboard."""

    def __init__(
        self,
        log_path: Path = Path("artifacts/models/training_progress.json"),
        check_freq: int = 50,
        verbose: int = 1,
    ):
        super().__init__(verbose)
        self.log_path = log_path
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.check_freq = check_freq

        self.episode_rewards: List[float] = []
        self.episode_lengths: List[int] = []
        self.timesteps_history: List[int] = []
        self.rolling_rewards: List[float] = []
        self.current_ep_reward: float = 0.0
        self.current_ep_length: int = 0
        self.is_training: bool = True

    def _on_training_start(self) -> None:
        self.is_training = True
        self._update_status(status="RUNNING")

    def _on_step(self) -> bool:
        # Accumulate reward from environment
        rewards = self.locals.get("rewards")
        if rewards is not None and len(rewards) > 0:
            self.current_ep_reward += float(rewards[0])
            self.current_ep_length += 1

        # Check if episode ended
        dones = self.locals.get("dones")
        if dones is not None and len(dones) > 0 and dones[0]:
            self.episode_rewards.append(round(self.current_ep_reward, 2))
            self.episode_lengths.append(self.current_ep_length)
            self.timesteps_history.append(self.num_timesteps)

            # Rolling 10-episode mean
            rolling_avg = float(np.mean(self.episode_rewards[-10:]))
            self.rolling_rewards.append(round(rolling_avg, 2))

            self.current_ep_reward = 0.0
            self.current_ep_length = 0

            self._update_status(status="RUNNING")

        elif self.n_calls % self.check_freq == 0:
            self._update_status(status="RUNNING")

        return True

    def _on_training_end(self) -> None:
        self.is_training = False
        self._update_status(status="COMPLETED")

    def _update_status(self, status: str) -> None:
        """Writes current training telemetry to JSON for the dashboard."""
        data = {
            "status": status,
            "timesteps_completed": self.num_timesteps,
            "total_timesteps": getattr(self.model, "_total_timesteps", 0),
            "episodes_completed": len(self.episode_rewards),
            "latest_reward": self.episode_rewards[-1] if self.episode_rewards else 0.0,
            "rolling_reward": self.rolling_rewards[-1] if self.rolling_rewards else 0.0,
            "history": {
                "timesteps": self.timesteps_history[-100:],
                "rewards": self.episode_rewards[-100:],
                "rolling_rewards": self.rolling_rewards[-100:],
            },
        }
        with open(self.log_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
