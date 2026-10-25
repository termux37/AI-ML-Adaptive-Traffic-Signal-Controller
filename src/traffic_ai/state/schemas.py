"""State representations and structured observations."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from traffic_ai.config.schemas import ObservationMode


@dataclass
class ApproachState:
    """Traffic metrics for a single approach direction."""
    name: str  # "north", "south", "east", "west"
    vehicle_count: int = 0
    queue_length: int = 0  # Vehicles with speed < 0.1 m/s
    mean_speed_mps: float = 0.0  # meters per second
    total_waiting_time_s: float = 0.0  # seconds
    max_wait_time_s: float = 0.0  # longest waiting vehicle on this approach
    occupancy_ratio: float = 0.0  # 0.0 to 1.0


@dataclass
class TrafficState:
    """Complete snapshot of the intersection at a simulation step."""
    timestamp: float
    current_green_id: int
    time_in_green: float
    is_in_transition: bool
    signal_string: str
    approaches: Dict[str, ApproachState] = field(default_factory=dict)
    total_vehicles: int = 0
    total_queue: int = 0
    completed_vehicles_step: int = 0
    total_completed_vehicles: int = 0
    observation_mode: ObservationMode = ObservationMode.GROUND_TRUTH

    @property
    def total_waiting_time(self) -> float:
        return sum(app.total_waiting_time_s for app in self.approaches.values())

    @property
    def max_waiting_time(self) -> float:
        if not self.approaches:
            return 0.0
        return max(app.max_wait_time_s for app in self.approaches.values())
