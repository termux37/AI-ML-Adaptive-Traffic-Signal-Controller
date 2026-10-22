"""Configuration schemas and data contracts for AI & ML Based Adaptive Traffic Control System."""

from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class ObservationMode(str, Enum):
    """Observation mode for traffic controller input."""
    GROUND_TRUTH = "ground_truth"
    VISION = "vision"
    HYBRID = "hybrid"


class ControllerType(str, Enum):
    """Supported controller implementations."""
    FIXED_TIME = "fixed_time"
    ACTUATED = "actuated"
    MAX_PRESSURE = "max_pressure"
    DQN = "dqn"


class ScenarioName(str, Enum):
    """Reproducible benchmark demand scenarios."""
    LOW = "low"
    BALANCED = "balanced"
    HEAVY = "heavy"
    NORTH_SOUTH_DOMINANT = "north_south_dominant"
    EAST_WEST_DOMINANT = "east_west_dominant"
    BURSTY = "bursty"
    UNSEEN_EVALUATION = "unseen_evaluation"


class VehicleClassMix(BaseModel):
    """Proportions of vehicle classes in simulation demand."""
    passenger: float = Field(0.75, ge=0.0, le=1.0)
    bus: float = Field(0.08, ge=0.0, le=1.0)
    truck: float = Field(0.12, ge=0.0, le=1.0)
    motorcycle: float = Field(0.05, ge=0.0, le=1.0)


class ScenarioConfig(BaseModel):
    """Definition and parameters of a traffic demand scenario."""
    name: ScenarioName = ScenarioName.BALANCED
    version: str = "1.0.0"
    seed: int = 42
    duration_seconds: int = 3600
    warmup_seconds: int = 300
    step_length_seconds: float = 1.0

    # Arrival rates (vehicles per hour per incoming approach)
    north_arrival_rate_vph: float = 400.0
    south_arrival_rate_vph: float = 400.0
    east_arrival_rate_vph: float = 400.0
    west_arrival_rate_vph: float = 400.0

    # Turning ratios: [right, straight, left], normalized to 1.0
    turn_ratios: Dict[str, List[float]] = Field(
        default_factory=lambda: {
            "north": [0.20, 0.65, 0.15],
            "south": [0.20, 0.65, 0.15],
            "east":  [0.20, 0.65, 0.15],
            "west":  [0.20, 0.65, 0.15],
        }
    )

    # Bursty wave parameters (used if name == BURSTY)
    burst_interval_seconds: int = 180
    burst_multiplier: float = 2.5

    vehicle_mix: VehicleClassMix = Field(default_factory=VehicleClassMix)


class SafetyConfig(BaseModel):
    """Deterministic signal safety constraints."""
    min_green_seconds: float = 10.0
    max_green_seconds: float = 60.0
    yellow_seconds: float = 3.0
    all_red_seconds: float = 2.0
    tls_id: str = "junction_center"


class ControllerConfig(BaseModel):
    """Controller operational parameters."""
    controller_type: ControllerType = ControllerType.FIXED_TIME
    observation_mode: ObservationMode = ObservationMode.GROUND_TRUTH

    # Fixed-Time parameters
    cycle_time_seconds: float = 90.0
    green_splits: List[float] = Field(default_factory=lambda: [0.35, 0.15, 0.35, 0.15])

    # Actuated parameters
    actuated_gap_threshold_seconds: float = 3.0
    actuated_min_green_seconds: float = 10.0
    actuated_max_green_seconds: float = 50.0

    # Max-Pressure parameters
    max_pressure_interval_seconds: float = 10.0

    # DQN parameters
    dqn_model_path: Optional[str] = None
    decision_epoch_seconds: float = 5.0


class SimulationConfig(BaseModel):
    """Top-level simulation runtime configuration."""
    net_file: str = "simulation/network/intersection.net.xml"
    route_file: Optional[str] = None
    additional_files: List[str] = Field(
        default_factory=lambda: ["simulation/network/detectors.add.xml"]
    )
    gui: bool = False
    step_length: float = 1.0
    time_to_teleport: int = -1  # Disable teleporting to measure true gridlock if it happens
    sumo_seed: int = 42
    output_dir: str = "data/runs"
