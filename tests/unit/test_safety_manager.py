"""Unit tests for the Deterministic Safety Manager."""

import pytest
from traffic_ai.config.schemas import SafetyConfig
from traffic_ai.control.phase_catalog import PhaseCatalog
from traffic_ai.control.safety_manager import (
    DecisionReason,
    DeterministicSafetyManager,
    SignalState,
)


def test_safety_manager_initialization():
    sm = DeterministicSafetyManager()
    assert sm.current_green_id == 0
    assert sm.state == SignalState.GREEN
    assert sm.get_current_signal_string() == PhaseCatalog.get_phase(0).signal_state
    assert not sm.is_in_transition


def test_safety_manager_min_green_rejection():
    config = SafetyConfig(min_green_seconds=10.0, max_green_seconds=60.0)
    sm = DeterministicSafetyManager(config=config)

    # At t=2s, time_in_state is 2s < 10s. Request to switch to Phase 2 should be rejected.
    sm.step(2.0)
    dec = sm.request_phase(requested_phase_id=2, sim_time=2.0)
    assert not dec.accepted
    assert dec.reason == DecisionReason.MIN_GREEN_NOT_REACHED
    assert sm.current_green_id == 0
    assert sm.state == SignalState.GREEN


def test_safety_manager_legal_transition_sequence():
    config = SafetyConfig(min_green_seconds=10.0, yellow_seconds=3.0, all_red_seconds=2.0)
    sm = DeterministicSafetyManager(config=config)

    # Advance beyond min_green
    sm.step(12.0)
    assert sm.time_in_state == 12.0

    # Request switch to Phase 2 (EW Through)
    dec = sm.request_phase(requested_phase_id=2, sim_time=12.0)
    assert dec.accepted
    assert dec.reason == DecisionReason.TRANSITION_APPROVED
    assert sm.state == SignalState.YELLOW
    assert sm.target_green_id == 2
    assert sm.get_current_signal_string() == PhaseCatalog.get_phase(0).yellow_state

    # Advance 2 seconds into yellow (total 2s of yellow)
    sig = sm.step(2.0)
    assert sm.state == SignalState.YELLOW
    assert sig == PhaseCatalog.get_phase(0).yellow_state

    # Advance 1.5 seconds (crossing 3.0s yellow limit into all-red)
    sig = sm.step(1.5)
    assert sm.state == SignalState.ALL_RED
    assert sig == PhaseCatalog.ALL_RED_STATE

    # Advance 2.0 seconds (completing all-red clearance into Target Phase 2 Green)
    sig = sm.step(2.0)
    assert sm.state == SignalState.GREEN
    assert sm.current_green_id == 2
    assert sig == PhaseCatalog.get_phase(2).signal_state
    assert not sm.is_in_transition


def test_safety_manager_max_green_enforcement():
    config = SafetyConfig(min_green_seconds=10.0, max_green_seconds=50.0)
    sm = DeterministicSafetyManager(config=config)

    # Advance past max_green
    sm.step(51.0)
    dec = sm.request_phase(requested_phase_id=0, sim_time=51.0)
    assert not dec.accepted
    assert dec.reason == DecisionReason.MAX_GREEN_ENFORCED
    assert sm.target_green_id == 1  # Sequential next phase
    assert sm.state == SignalState.YELLOW


def test_safety_manager_rejects_requests_during_clearance():
    config = SafetyConfig(min_green_seconds=10.0, yellow_seconds=3.0)
    sm = DeterministicSafetyManager(config=config)
    sm.step(15.0)

    # Trigger transition
    sm.request_phase(requested_phase_id=2, sim_time=15.0)
    assert sm.is_in_transition

    # Attempt to request phase 3 while in transition
    dec = sm.request_phase(requested_phase_id=3, sim_time=16.0)
    assert not dec.accepted
    assert dec.reason == DecisionReason.TRANSITION_IN_PROGRESS
