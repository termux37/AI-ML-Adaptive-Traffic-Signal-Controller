"""Abstract base class interface for all traffic controllers."""

from abc import ABC, abstractmethod
from typing import Optional
from traffic_ai.state.schemas import TrafficState


class TrafficSignalController(ABC):
    """Unified interface for baseline and learned signal controllers."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def reset(self) -> None:
        """Resets controller internal states."""
        pass

    @abstractmethod
    def propose_action(self, state: TrafficState) -> Optional[int]:
        """Proposes a target green phase ID (0..3) or None (hold current)."""
        pass

    def on_step(self, state: TrafficState, action: Optional[int], applied_signal: str) -> None:
        """Optional callback after simulation step execution."""
        pass

    def close(self) -> None:
        """Releases any resources."""
        pass
