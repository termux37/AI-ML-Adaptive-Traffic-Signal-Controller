"""Max-Pressure signal controller inspired by Varaiya (2013) and PressLight (KDD 2019)."""

from typing import Dict, List, Optional, Tuple
from traffic_ai.control.interfaces import TrafficSignalController
from traffic_ai.control.phase_catalog import PhaseCatalog
from traffic_ai.state.schemas import TrafficState


class MaxPressureController(TrafficSignalController):
    """Max-Pressure controller selecting the phase with highest downstream queue differential."""

    def __init__(
        self,
        decision_interval: float = 5.0,
        min_green: float = 10.0,
        name: str = "max_pressure",
    ):
        super().__init__(name=name)
        self.decision_interval = decision_interval
        self.min_green = min_green
        self.last_decision_time: float = -1.0

    def reset(self) -> None:
        self.last_decision_time = -1.0

    def propose_action(self, state: TrafficState) -> Optional[int]:
        if state.is_in_transition:
            return None

        # Check if min green is satisfied
        if state.time_in_green < self.min_green:
            return state.current_green_id

        # Check decision interval
        if state.timestamp - self.last_decision_time < self.decision_interval:
            return state.current_green_id

        self.last_decision_time = state.timestamp

        # Calculate pressure for each phase
        phase_pressures = self._calculate_pressures(state)

        # Select phase with maximum pressure
        best_phase = max(phase_pressures.items(), key=lambda kv: kv[1])[0]

        # If pressures are all zero or tied, retain current green to minimize switching
        if phase_pressures[best_phase] <= 0 and phase_pressures[state.current_green_id] >= 0:
            return state.current_green_id

        return best_phase

    def _calculate_pressures(self, state: TrafficState) -> Dict[int, float]:
        """Calculates pressure P(p) = sum(upstream_queue - downstream_queue) for each phase."""
        pressures = {}

        n_q = state.approaches.get("north", None)
        s_q = state.approaches.get("south", None)
        e_q = state.approaches.get("east", None)
        w_q = state.approaches.get("west", None)

        n_val = (n_q.queue_length if n_q else 0)
        s_val = (s_q.queue_length if s_q else 0)
        e_val = (e_q.queue_length if e_q else 0)
        w_val = (w_q.queue_length if w_q else 0)

        # In a single intersection, outgoing lanes typically drain freely (downstream queue ~ 0)
        # Phase 0: NS Through/Right
        pressures[0] = float(n_val + s_val) * 1.0
        # Phase 1: NS Left
        pressures[1] = float(n_val + s_val) * 0.4
        # Phase 2: EW Through/Right
        pressures[2] = float(e_val + w_val) * 1.0
        # Phase 3: EW Left
        pressures[3] = float(e_val + w_val) * 0.4

        return pressures
