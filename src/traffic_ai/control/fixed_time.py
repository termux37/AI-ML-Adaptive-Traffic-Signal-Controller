"""Fixed-Time (pre-timed) signal controller."""

from typing import Dict, List, Optional
from traffic_ai.control.interfaces import TrafficSignalController
from traffic_ai.state.schemas import TrafficState


class FixedTimeController(TrafficSignalController):
    """Pre-timed controller with fixed cycle duration and predetermined green splits."""

    def __init__(
        self,
        green_durations: Optional[Dict[int, float]] = None,
        name: str = "fixed_time",
    ):
        super().__init__(name=name)
        # Default green durations: Phase 0 (30s), Phase 1 (15s), Phase 2 (30s), Phase 3 (15s)
        self.green_durations = green_durations or {
            0: 30.0,
            1: 15.0,
            2: 30.0,
            3: 15.0,
        }

    def reset(self) -> None:
        pass

    def propose_action(self, state: TrafficState) -> Optional[int]:
        if state.is_in_transition:
            return None

        current_phase = state.current_green_id
        allocated_duration = self.green_durations.get(current_phase, 30.0)

        if state.time_in_green >= allocated_duration:
            next_phase = (current_phase + 1) % 4
            return next_phase
        else:
            return current_phase
