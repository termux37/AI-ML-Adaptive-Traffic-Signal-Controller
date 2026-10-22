"""Ground truth state extractor from TraCI simulation."""

from typing import Dict, List, Optional
import traci

from traffic_ai.config.schemas import ObservationMode
from traffic_ai.control.safety_manager import DeterministicSafetyManager
from traffic_ai.state.schemas import ApproachState, TrafficState


class GroundTruthAdapter:
    """Reads exact vehicle, queue, and timing state directly from TraCI."""

    APPROACH_EDGES = {
        "north": "edge_n2c",
        "south": "edge_s2c",
        "east":  "edge_e2c",
        "west":  "edge_w2c",
    }

    def __init__(self, tls_id: str = "junction_center"):
        self.tls_id = tls_id
        self.total_completed: int = 0

    def reset(self) -> None:
        self.total_completed = 0

    def extract_state(self, safety_manager: DeterministicSafetyManager) -> TrafficState:
        """Constructs TrafficState from live TraCI queries."""
        sim_time = traci.simulation.getTime()
        arrived_count = traci.simulation.getArrivedNumber()
        self.total_completed += arrived_count

        approaches: Dict[str, ApproachState] = {}
        total_veh = 0
        total_q = 0

        for name, edge_id in self.APPROACH_EDGES.items():
            count = traci.edge.getLastStepVehicleNumber(edge_id)
            queue = traci.edge.getLastStepHaltingNumber(edge_id)
            speed = traci.edge.getLastStepMeanSpeed(edge_id)
            wait = traci.edge.getWaitingTime(edge_id)
            occupancy = traci.edge.getLastStepOccupancy(edge_id)

            # Longest waiting vehicle on this approach
            veh_ids = traci.edge.getLastStepVehicleIDs(edge_id)
            max_wait = 0.0
            for vid in veh_ids:
                w = traci.vehicle.getWaitingTime(vid)
                if w > max_wait:
                    max_wait = w

            approaches[name] = ApproachState(
                name=name,
                vehicle_count=count,
                queue_length=queue,
                mean_speed_mps=float(speed),
                total_waiting_time_s=float(wait),
                max_wait_time_s=float(max_wait),
                occupancy_ratio=float(occupancy),
            )
            total_veh += count
            total_q += queue

        signal_str = safety_manager.get_current_signal_string()

        return TrafficState(
            timestamp=sim_time,
            current_green_id=safety_manager.current_green_id,
            time_in_green=safety_manager.time_in_state if not safety_manager.is_in_transition else 0.0,
            is_in_transition=safety_manager.is_in_transition,
            signal_string=signal_str,
            approaches=approaches,
            total_vehicles=total_veh,
            total_queue=total_q,
            completed_vehicles_step=arrived_count,
            total_completed_vehicles=self.total_completed,
            observation_mode=ObservationMode.GROUND_TRUTH,
        )
