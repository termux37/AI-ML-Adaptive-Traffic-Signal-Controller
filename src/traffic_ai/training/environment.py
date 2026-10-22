"""Gymnasium-compatible reinforcement learning environment for adaptive traffic signal control."""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import gymnasium as gym
from gymnasium import spaces
import numpy as np

from traffic_ai.config.schemas import (
    ObservationMode,
    SafetyConfig,
    ScenarioConfig,
    ScenarioName,
    SimulationConfig,
)
from traffic_ai.control.safety_manager import DeterministicSafetyManager
from traffic_ai.simulation.runner import SimulationRunner
from traffic_ai.simulation.scenario_manager import ScenarioManager
from traffic_ai.state.ground_truth import GroundTruthAdapter
from traffic_ai.state.schemas import TrafficState


class TrafficSignalEnv(gym.Env):
    """Custom Gymnasium environment for traffic signal control over TraCI."""

    metadata = {"render_modes": ["human", "rgb_array"]}

    def __init__(
        self,
        scenario_config: Optional[ScenarioConfig] = None,
        safety_config: Optional[SafetyConfig] = None,
        sim_config: Optional[SimulationConfig] = None,
        decision_interval: float = 5.0,
        observation_mode: ObservationMode = ObservationMode.GROUND_TRUTH,
        reward_weights: Optional[Dict[str, float]] = None,
    ):
        super().__init__()
        self.scenario_config = scenario_config or ScenarioManager.get_preset_config(
            ScenarioName.BALANCED, seed=42, duration=1800
        )
        self.safety_config = safety_config or SafetyConfig()
        self.sim_config = sim_config or SimulationConfig()
        self.decision_interval = decision_interval
        self.observation_mode = observation_mode

        self.reward_weights = reward_weights or {
            "weight_queue": 1.0,
            "weight_throughput": 4.0,
            "weight_switch": 0.2,
        }

        # Action space: 4 discrete green phases
        self.action_space = spaces.Discrete(4)

        # Observation space: 25 normalized continuous values
        # 4 approaches x 5 features (count, queue, speed, wait, occ) = 20
        # + 4 one-hot current phase + 1 normalized time in green = 25
        self.observation_space = spaces.Box(
            low=0.0,
            high=1.0,
            shape=(25,),
            dtype=np.float32,
        )

        self.runner: Optional[SimulationRunner] = None
        self.prev_total_queue: float = 0.0
        self.prev_total_wait: float = 0.0
        self.prev_completed: int = 0
        self.current_step: int = 0
        self.max_steps: int = max(10, int(self.scenario_config.duration_seconds / 12.0))

    def _build_observation(self, state: TrafficState) -> np.ndarray:
        """Constructs a normalized 25-dimensional observation vector."""
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

        # One-hot active green phase
        curr_phase = state.current_green_id
        if 0 <= curr_phase < 4:
            obs[20 + curr_phase] = 1.0

        # Normalized time in green
        obs[24] = np.clip(state.time_in_green / self.safety_config.max_green_seconds, 0.0, 1.0)

        return obs

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        super().reset(seed=seed)

        if seed is not None:
            self.scenario_config.seed = seed

        if self.runner is not None:
            self.runner.close()

        # Generate fresh runner
        run_id = f"rl_ep_{self.scenario_config.seed}_{np.random.randint(1000, 9999)}"
        self.runner = SimulationRunner(
            scenario_config=self.scenario_config,
            safety_config=self.safety_config,
            simulation_config=self.sim_config,
            run_id=run_id,
        )
        self.runner.start()

        # Step until min_green (10s) is satisfied so the agent can act immediately
        state = self.runner.step()
        while state.time_in_green < self.safety_config.min_green_seconds and self.runner.is_running:
            state = self.runner.step()

        self.prev_total_queue = float(state.total_queue)
        self.prev_total_wait = float(state.total_waiting_time)
        self.prev_completed = state.total_completed_vehicles
        self.current_step = 0

        obs = self._build_observation(state)
        info = {"initial_state": state}
        return obs, info

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        if self.runner is None or not self.runner.is_running:
            raise RuntimeError("Environment step called before reset().")

        curr_phase_before = self.runner.safety_manager.current_green_id
        target_phase = int(action)
        self.runner.controller.propose_action = lambda s: target_phase

        # If switching, execute 5s clearance (yellow + all-red) + min_green (10s) = 15s
        # If holding, execute min_green (10s)
        duration_to_step = int(
            (self.safety_config.yellow_seconds + self.safety_config.all_red_seconds + self.safety_config.min_green_seconds)
            if target_phase != curr_phase_before
            else self.safety_config.min_green_seconds
        )
        steps_in_epoch = max(1, int(duration_to_step / self.sim_config.step_length))

        latest_state = self.runner.current_state
        step_count = 0
        total_queue_accum = 0.0
        total_wait_accum = 0.0

        for _ in range(steps_in_epoch):
            latest_state = self.runner.step()
            step_count += 1
            total_queue_accum += latest_state.total_queue
            total_wait_accum += latest_state.total_waiting_time
            if not self.runner.is_running:
                break

        self.current_step += 1

        curr_queue = float(latest_state.total_queue)
        curr_wait = float(latest_state.total_waiting_time)
        throughput_delta = float(latest_state.total_completed_vehicles - self.prev_completed)
        queue_diff = self.prev_total_queue - curr_queue
        wait_diff = self.prev_total_wait - curr_wait
        mean_q = float(total_queue_accum / max(1, step_count))
        switched = 1.0 if target_phase != curr_phase_before else 0.0

        w_queue = self.reward_weights.get("weight_queue", 1.0)
        w_throughput = self.reward_weights.get("weight_throughput", 4.0)
        w_switch = self.reward_weights.get("weight_switch", 0.2)

        reward = - w_queue * mean_q + w_throughput * throughput_delta - w_switch * switched

        # Update previous tracking
        self.prev_total_queue = curr_queue
        self.prev_total_wait = curr_wait
        self.prev_completed = latest_state.total_completed_vehicles

        # Termination checks
        terminated = not self.runner.is_running
        truncated = self.current_step >= self.max_steps

        obs = self._build_observation(latest_state)
        info = {
            "queue_diff": queue_diff,
            "wait_diff": wait_diff,
            "throughput_delta": throughput_delta,
            "switched": switched,
            "total_queue": curr_queue,
            "total_waiting_time": curr_wait,
            "max_wait_time": latest_state.max_waiting_time,
            "active_phase": latest_state.current_green_id,
        }

        if terminated or truncated:
            self.runner.close()

        return obs, float(reward), terminated, truncated, info

    def close(self) -> None:
        if self.runner is not None:
            self.runner.close()
            self.runner = None
