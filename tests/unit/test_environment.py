"""Unit tests for the Gymnasium TrafficSignalEnv."""

import numpy as np
import pytest
from traffic_ai.config.schemas import ScenarioName
from traffic_ai.simulation.scenario_manager import ScenarioManager
from traffic_ai.training.environment import TrafficSignalEnv


def test_env_observation_and_action_spaces():
    scenario = ScenarioManager.get_preset_config(ScenarioName.LOW, seed=99, duration=60)
    env = TrafficSignalEnv(scenario_config=scenario, decision_interval=5.0)

    assert env.action_space.n == 4
    assert env.observation_space.shape == (25,)
    assert env.observation_space.dtype == np.float32


def test_env_reset_and_step():
    scenario = ScenarioManager.get_preset_config(ScenarioName.LOW, seed=99, duration=30)
    env = TrafficSignalEnv(scenario_config=scenario, decision_interval=5.0)

    try:
        obs, info = env.reset(seed=99)
        assert obs.shape == (25,)
        assert isinstance(obs, np.ndarray)
        assert np.all(obs >= 0.0) and np.all(obs <= 1.0)
        assert "initial_state" in info

        # Step action 0
        next_obs, reward, terminated, truncated, step_info = env.step(0)
        assert next_obs.shape == (25,)
        assert isinstance(reward, float)
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert "total_queue" in step_info
        assert "queue_diff" in step_info
    finally:
        env.close()
