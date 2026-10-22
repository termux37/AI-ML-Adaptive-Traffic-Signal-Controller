"""Phase catalog and link index mapping for the four-way junction."""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class GreenPhaseDefinition:
    phase_id: int
    name: str
    signal_state: str
    yellow_state: str
    controlled_links: Tuple[int, ...]
    incoming_lanes: Tuple[str, ...]
    outgoing_lanes: Tuple[str, ...]
    description: str


class PhaseCatalog:
    """Catalog of valid, conflict-free signal phases and their geometry mappings."""

    ALL_RED_STATE = "rrrrrrrrrrrrrrrr"

    PHASES: Dict[int, GreenPhaseDefinition] = {
        0: GreenPhaseDefinition(
            phase_id=0,
            name="NS_THROUGH_RIGHT",
            signal_state="GGGrrrrrGGGrrrrr",
            yellow_state="yyyrrrrryyyrrrrr",
            controlled_links=(0, 1, 2, 8, 9, 10),
            incoming_lanes=(
                "edge_n2c_0", "edge_n2c_1",
                "edge_s2c_0", "edge_s2c_1",
            ),
            outgoing_lanes=(
                "edge_c2w_0", "edge_c2s_0", "edge_c2s_1",
                "edge_c2e_0", "edge_c2n_0", "edge_c2n_1",
            ),
            description="North-South Through and Right movements",
        ),
        1: GreenPhaseDefinition(
            phase_id=1,
            name="NS_LEFT",
            signal_state="rrrGrrrrrrrGrrrr",
            yellow_state="rrryrrrrrrryrrrr",
            controlled_links=(3, 11),
            incoming_lanes=("edge_n2c_1", "edge_s2c_1"),
            outgoing_lanes=("edge_c2e_1", "edge_c2w_1"),
            description="North-South Protected Left Turns",
        ),
        2: GreenPhaseDefinition(
            phase_id=2,
            name="EW_THROUGH_RIGHT",
            signal_state="rrrrGGGrrrrrGGGr",
            yellow_state="rrrryyyrrrrryyyr",
            controlled_links=(4, 5, 6, 12, 13, 14),
            incoming_lanes=(
                "edge_e2c_0", "edge_e2c_1",
                "edge_w2c_0", "edge_w2c_1",
            ),
            outgoing_lanes=(
                "edge_c2n_0", "edge_c2w_0", "edge_c2w_1",
                "edge_c2s_0", "edge_c2e_0", "edge_c2e_1",
            ),
            description="East-West Through and Right movements",
        ),
        3: GreenPhaseDefinition(
            phase_id=3,
            name="EW_LEFT",
            signal_state="rrrrrrrGrrrrrrrG",
            yellow_state="rrrrrrryrrrrrrry",
            controlled_links=(7, 15),
            incoming_lanes=("edge_e2c_1", "edge_w2c_1"),
            outgoing_lanes=("edge_c2s_1", "edge_c2n_1"),
            description="East-West Protected Left Turns",
        ),
    }

    NUM_GREEN_PHASES = 4

    @classmethod
    def get_phase(cls, phase_id: int) -> GreenPhaseDefinition:
        return cls.PHASES[phase_id]

    @classmethod
    def is_conflicting(cls, phase_a: int, phase_b: int) -> bool:
        """Determines if two green phases share conflicting movements."""
        if phase_a == phase_b:
            return False
        # In our 4-phase catalog, all distinct phases are mutually exclusive
        return True
