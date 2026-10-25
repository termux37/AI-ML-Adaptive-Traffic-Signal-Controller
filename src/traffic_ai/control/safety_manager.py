"""Deterministic signal safety manager for traffic phase transitions."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from traffic_ai.config.schemas import SafetyConfig
from traffic_ai.control.phase_catalog import PhaseCatalog


class SignalState(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    ALL_RED = "ALL_RED"


class DecisionReason(str, Enum):
    HOLD_GREEN = "HOLD_GREEN"
    TRANSITION_APPROVED = "TRANSITION_APPROVED"
    MIN_GREEN_NOT_REACHED = "MIN_GREEN_NOT_REACHED"
    MAX_GREEN_ENFORCED = "MAX_GREEN_ENFORCED"
    TRANSITION_IN_PROGRESS = "TRANSITION_IN_PROGRESS"
    INVALID_PHASE_REQUEST = "INVALID_PHASE_REQUEST"
    INITIALIZATION = "INITIALIZATION"


@dataclass
class DecisionRecord:
    timestamp: float
    requested_phase: Optional[int]
    active_green_id: int
    target_green_id: int
    signal_state: SignalState
    accepted: bool
    reason: DecisionReason


class DeterministicSafetyManager:
    """Enforces all clearance intervals, minimum/maximum green bounds, and legal transitions."""

    def __init__(self, config: Optional[SafetyConfig] = None):
        self.config = config or SafetyConfig()
        self.reset()

    def reset(self, initial_green_id: int = 0) -> None:
        """Resets the safety manager to a known safe green state."""
        self.current_green_id: int = initial_green_id
        self.target_green_id: int = initial_green_id
        self.state: SignalState = SignalState.GREEN
        self.time_in_state: float = 0.0
        self.current_simulation_time: float = 0.0

        # Last logged decision
        self.last_decision = DecisionRecord(
            timestamp=0.0,
            requested_phase=initial_green_id,
            active_green_id=initial_green_id,
            target_green_id=initial_green_id,
            signal_state=SignalState.GREEN,
            accepted=True,
            reason=DecisionReason.INITIALIZATION,
        )

    def request_phase(self, requested_phase_id: Optional[int], sim_time: float) -> DecisionRecord:
        """Processes an agent or baseline phase request according to safety rules."""
        self.current_simulation_time = sim_time

        # Validate input
        if requested_phase_id is not None and requested_phase_id not in PhaseCatalog.PHASES:
            self.last_decision = DecisionRecord(
                timestamp=sim_time,
                requested_phase=requested_phase_id,
                active_green_id=self.current_green_id,
                target_green_id=self.target_green_id,
                signal_state=self.state,
                accepted=False,
                reason=DecisionReason.INVALID_PHASE_REQUEST,
            )
            return self.last_decision

        # Case 1: In clearance transition (Yellow or All-Red)
        if self.state in (SignalState.YELLOW, SignalState.ALL_RED):
            self.last_decision = DecisionRecord(
                timestamp=sim_time,
                requested_phase=requested_phase_id,
                active_green_id=self.current_green_id,
                target_green_id=self.target_green_id,
                signal_state=self.state,
                accepted=False,
                reason=DecisionReason.TRANSITION_IN_PROGRESS,
            )
            return self.last_decision

        # Case 2: Currently in GREEN
        # 2A: Max Green constraint enforcement (prevent approach starvation)
        if self.time_in_state >= self.config.max_green_seconds:
            # Force transition to next sequential green phase
            next_phase = (self.current_green_id + 1) % PhaseCatalog.NUM_GREEN_PHASES
            self._begin_transition(target_phase=next_phase)
            self.last_decision = DecisionRecord(
                timestamp=sim_time,
                requested_phase=requested_phase_id,
                active_green_id=self.current_green_id,
                target_green_id=next_phase,
                signal_state=self.state,
                accepted=False,
                reason=DecisionReason.MAX_GREEN_ENFORCED,
            )
            return self.last_decision

        # 2B: Agent requests holding the same phase (or None)
        if requested_phase_id is None or requested_phase_id == self.current_green_id:
            self.last_decision = DecisionRecord(
                timestamp=sim_time,
                requested_phase=requested_phase_id,
                active_green_id=self.current_green_id,
                target_green_id=self.current_green_id,
                signal_state=self.state,
                accepted=True,
                reason=DecisionReason.HOLD_GREEN,
            )
            return self.last_decision

        # 2C: Agent requests a phase transition
        if self.time_in_state < self.config.min_green_seconds:
            # Minimum green not yet satisfied; hold green
            self.last_decision = DecisionRecord(
                timestamp=sim_time,
                requested_phase=requested_phase_id,
                active_green_id=self.current_green_id,
                target_green_id=self.current_green_id,
                signal_state=self.state,
                accepted=False,
                reason=DecisionReason.MIN_GREEN_NOT_REACHED,
            )
            return self.last_decision

        # Transition is legal and safe
        self._begin_transition(target_phase=requested_phase_id)
        self.last_decision = DecisionRecord(
            timestamp=sim_time,
            requested_phase=requested_phase_id,
            active_green_id=self.current_green_id,
            target_green_id=requested_phase_id,
            signal_state=self.state,
            accepted=True,
            reason=DecisionReason.TRANSITION_APPROVED,
        )
        return self.last_decision

    def _begin_transition(self, target_phase: int) -> None:
        """Initiates yellow clearance for the current phase towards target phase."""
        self.target_green_id = target_phase
        self.state = SignalState.YELLOW
        self.time_in_state = 0.0

    def step(self, dt: float) -> str:
        """Advances safety state machine by dt seconds and returns current signal string."""
        self.time_in_state += dt

        if self.state == SignalState.YELLOW:
            if self.time_in_state >= self.config.yellow_seconds:
                self.state = SignalState.ALL_RED
                self.time_in_state = 0.0

        elif self.state == SignalState.ALL_RED:
            if self.time_in_state >= self.config.all_red_seconds:
                self.state = SignalState.GREEN
                self.current_green_id = self.target_green_id
                self.time_in_state = 0.0

        return self.get_current_signal_string()

    def get_current_signal_string(self) -> str:
        """Returns the 16-character signal state string for SUMO."""
        if self.state == SignalState.GREEN:
            return PhaseCatalog.get_phase(self.current_green_id).signal_state
        elif self.state == SignalState.YELLOW:
            return PhaseCatalog.get_phase(self.current_green_id).yellow_state
        else:  # SignalState.ALL_RED
            return PhaseCatalog.ALL_RED_STATE

    @property
    def is_in_transition(self) -> bool:
        return self.state in (SignalState.YELLOW, SignalState.ALL_RED)
