"""Vehicle-Actuated traffic signal controller."""

from typing import Dict, List, Optional
from traffic_ai.control.interfaces import TrafficSignalController
from traffic_ai.control.phase_catalog import PhaseCatalog
from traffic_ai.state.schemas import TrafficState


class ActuatedController(TrafficSignalController):
    """Actuated controller with dynamic green extension, gap-out logic, and demand-responsive switching."""

    def __init__(
        self,
        min_green: float = 10.0,
        max_green: float = 50.0,
        gap_threshold: float = 3.0,
        name: str = "actuated",
    ):
        super().__init__(name=name)
        self.min_green = min_green
        self.max_green = max_green
        self.gap_threshold = gap_threshold
        self.last_detection_time: Dict[int, float] = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}

    def reset(self) -> None:
        self.last_detection_time = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}

    def propose_action(self, state: TrafficState) -> Optional[int]:
        if state.is_in_transition:
            return None

        curr = state.current_green_id

        # Get demand on current active green phase
        active_phase_def = PhaseCatalog.get_phase(curr)
        # Check active approach queue/presence
        active_lanes = active_phase_def.incoming_lanes

        # Calculate demand on each phase
        phase_demand = self._calculate_phase_demands(state)

        # Update last detection on active phase if demand present
        if phase_demand[curr] > 0:
            self.last_detection_time[curr] = state.timestamp

        # 1. Enforce minimum green
        if state.time_in_green < self.min_green:
            return curr

        # 2. Check for max-out
        if state.time_in_green >= self.max_green:
            # Must switch: select phase with highest demand
            return self._select_next_phase(curr, phase_demand)

        # 3. Check for gap-out (time since last arrival > gap_threshold)
        time_since_last_detection = state.timestamp - self.last_detection_time.get(curr, 0.0)
        gap_out = (time_since_last_detection >= self.gap_threshold) and (phase_demand[curr] == 0)

        if gap_out:
            # Check if conflicting demand exists
            other_demands = {p: d for p, d in phase_demand.items() if p != curr}
            if any(d > 0 for d in other_demands.values()):
                return self._select_next_phase(curr, phase_demand)

        # Extend green
        return curr

    def _calculate_phase_demands(self, state: TrafficState) -> Dict[int, float]:
        """Calculates instantaneous demand (queue + waiting vehicles) for each green phase."""
        demands = {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}

        # Approaches mapping
        # Phase 0: NS Through/Right
        n_q = state.approaches.get("north", None)
        s_q = state.approaches.get("south", None)
        e_q = state.approaches.get("east", None)
        w_q = state.approaches.get("west", None)

        if n_q and s_q:
            demands[0] = (n_q.queue_length + s_q.queue_length) * 1.0 + (n_q.vehicle_count + s_q.vehicle_count) * 0.5
            demands[1] = (n_q.queue_length + s_q.queue_length) * 0.4  # protected left demand proxy
        if e_q and w_q:
            demands[2] = (e_q.queue_length + w_q.queue_length) * 1.0 + (e_q.vehicle_count + w_q.vehicle_count) * 0.5
            demands[3] = (e_q.queue_length + w_q.queue_length) * 0.4

        return demands

    def _select_next_phase(self, curr: int, phase_demand: Dict[int, float]) -> int:
        """Selects the candidate phase with greatest demand, prioritizing conflicting phases."""
        candidates = [(p, demand) for p, demand in phase_demand.items() if p != curr]
        # Sort by demand descending
        candidates.sort(key=lambda x: x[1], reverse=True)
        if candidates and candidates[0][1] > 0:
            return candidates[0][0]
        # If no demand anywhere, cycle sequentially
        return (curr + 1) % 4
