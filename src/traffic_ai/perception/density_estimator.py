"""Traffic density and queue estimation from visual perceptions."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np

from traffic_ai.perception.camera_calibration import CameraCalibration
from traffic_ai.perception.detector import Detection
from traffic_ai.perception.tracker import TrackedVehicle
from traffic_ai.state.schemas import ApproachState


@dataclass
class ApproachPerceptionEstimate:
    name: str
    estimated_count: int = 0
    estimated_queue: int = 0
    ground_truth_count: int = 0
    ground_truth_queue: int = 0
    count_error: int = 0
    class_breakdown: Dict[str, int] = field(default_factory=dict)


@dataclass
class PerceptionFrameSummary:
    timestamp: float
    total_detections: int
    mean_confidence: float
    inference_ms: float
    fps: float
    mean_absolute_error: float
    approaches: Dict[str, ApproachPerceptionEstimate] = field(default_factory=dict)


class DensityEstimator:
    """Estimates lane-level and approach traffic metrics from object detections."""

    def __init__(self, calibration: CameraCalibration):
        self.calibration = calibration
        self.error_history: List[float] = []

    def estimate(
        self,
        tracks: List[TrackedVehicle],
        detections: List[Detection],
        ground_truth: Optional[Dict[str, ApproachState]] = None,
        sim_time: float = 0.0,
        inference_ms: float = 0.0,
    ) -> PerceptionFrameSummary:
        """Assigns vehicles to approaches, estimates counts, and computes error metrics against ground truth."""
        estimates: Dict[str, ApproachPerceptionEstimate] = {
            "north": ApproachPerceptionEstimate(name="north"),
            "south": ApproachPerceptionEstimate(name="south"),
            "east":  ApproachPerceptionEstimate(name="east"),
            "west":  ApproachPerceptionEstimate(name="west"),
        }

        # Map each tracked vehicle to approach via centroid
        for track in tracks:
            u, v = track.centroid
            approach = self.calibration.assign_approach(u, v)
            if approach in estimates:
                est = estimates[approach]
                est.estimated_count += 1
                est.estimated_queue += 1  # In camera ROI, arriving vehicles form queues
                cls_name = track.class_name
                est.class_breakdown[cls_name] = est.class_breakdown.get(cls_name, 0) + 1

        # Calculate errors against SUMO ground truth
        errors = []
        if ground_truth:
            for name, est in estimates.items():
                gt_app = ground_truth.get(name)
                if gt_app:
                    est.ground_truth_count = gt_app.vehicle_count
                    est.ground_truth_queue = gt_app.queue_length
                    est.count_error = est.estimated_count - gt_app.vehicle_count
                    errors.append(abs(est.count_error))

        mae = float(np.mean(errors)) if errors else 0.0
        self.error_history.append(mae)

        confs = [d.confidence for d in detections]
        mean_conf = float(np.mean(confs)) if confs else 0.0
        fps = round(1000.0 / inference_ms, 1) if inference_ms > 0 else 0.0

        return PerceptionFrameSummary(
            timestamp=sim_time,
            total_detections=len(detections),
            mean_confidence=round(mean_conf, 3),
            inference_ms=round(inference_ms, 2),
            fps=fps,
            mean_absolute_error=round(mae, 2),
            approaches=estimates,
        )
