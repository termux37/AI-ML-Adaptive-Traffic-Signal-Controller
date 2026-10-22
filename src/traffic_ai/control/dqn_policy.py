"""DQN policy controller wrapping Stable-Baselines3 model for online inference."""

from pathlib import Path
from typing import Optional
import numpy as np
from stable_baselines3 import DQN

from traffic_ai.control.interfaces import TrafficSignalController
from traffic_ai.state.schemas import TrafficState


class DQNController(TrafficSignalController):
    """Deep Q-Network controller for discrete signal phase selection."""

    def __init__(
        self,
        model_path: Optional[str] = "artifacts/models/dqn_best.zip",
        device: str = "cpu",
        name: str = "dqn",
    ):
        super().__init__(name=name)
        self.model_path = model_path
        self.device = device
        self.model: Optional[DQN] = None

        if model_path and Path(model_path).exists():
            self._load_model(model_path)

    def _load_model(self, path: str) -> None:
        """Loads trained DQN policy checkpoint."""
        try:
            self.model = DQN.load(path, device=self.device)
            self.model_path = path
        except Exception as e:
            self.model = None

    def reset(self) -> None:
        pass

    def _state_to_obs(self, state: TrafficState) -> np.ndarray:
        """Constructs identical 25-dim normalized observation vector used during training."""
        obs = np.zeros(25, dtype=np.float32)
        approaches = ["north", "south", "east", "west"]

        idx = 0
        for app_name in approaches:
            app = state.approaches.get(app_name)
            if app:
                obs[idx]     = np.clip(app.vehicle_count / 30.0, 0.0, 1.0)
                obs[idx + 1] = np.clip(app.queue_length / 30.0, 0.0, 1.0)
                obs[idx + 2] = np.clip(app.mean_speed_mps / 13.89, 0.0, 1.0)
                obs[idx + 3] = np.clip(app.total_waiting_time_s / 600.0, 0.0, 1.0)
                obs[idx + 4] = np.clip(app.occupancy_ratio, 0.0, 1.0)
            idx += 5

        # Current phase one-hot
        if 0 <= state.current_green_id < 4:
            obs[20 + state.current_green_id] = 1.0

        # Normalized time in green (max 60s)
        obs[24] = np.clip(state.time_in_green / 60.0, 0.0, 1.0)

        return obs

    def propose_action(self, state: TrafficState) -> Optional[int]:
        if state.is_in_transition:
            return None

        # If trained model is available, predict action
        if self.model is not None:
            obs = self._state_to_obs(state)
            action, _ = self.model.predict(obs, deterministic=True)
            return int(action)

        # Fallback heuristic if model is not yet loaded: hold current green
        return state.current_green_id
