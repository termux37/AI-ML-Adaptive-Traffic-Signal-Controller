"""Lightweight vehicle tracker using spatial IoU association."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
from traffic_ai.perception.detector import Detection


@dataclass
class TrackedVehicle:
    track_id: int
    bbox: Tuple[int, int, int, int]
    centroid: Tuple[int, int]
    class_name: str
    hits: int
    age: int
    approach: Optional[str] = None


class VehicleTracker:
    """Maintains consistent vehicle identities across consecutive camera frames."""

    def __init__(self, iou_threshold: float = 0.25, max_age: int = 5):
        self.iou_threshold = iou_threshold
        self.max_age = max_age
        self.next_id: int = 1
        self.tracks: Dict[int, TrackedVehicle] = {}

    def _compute_iou(self, boxA: Tuple[int, int, int, int], boxB: Tuple[int, int, int, int]) -> float:
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

        denom = float(boxAArea + boxBArea - interArea)
        return (interArea / denom) if denom > 0 else 0.0

    def update(self, detections: List[Detection]) -> List[TrackedVehicle]:
        """Associates detections with existing tracks or creates new ones."""
        # Age existing tracks
        for track in self.tracks.values():
            track.age += 1

        matched_track_ids = set()
        matched_det_indices = set()

        # Match existing tracks with detections via greedy IoU
        if self.tracks and detections:
            track_ids = list(self.tracks.keys())
            iou_matrix = np.zeros((len(track_ids), len(detections)), dtype=np.float32)

            for i, tid in enumerate(track_ids):
                for j, det in enumerate(detections):
                    iou_matrix[i, j] = self._compute_iou(self.tracks[tid].bbox, det.bbox)

            while True:
                max_val = np.max(iou_matrix) if iou_matrix.size > 0 else 0.0
                if max_val < self.iou_threshold:
                    break
                row, col = np.unravel_index(np.argmax(iou_matrix), iou_matrix.shape)
                tid = track_ids[row]

                # Update track
                self.tracks[tid].bbox = detections[col].bbox
                self.tracks[tid].centroid = detections[col].centroid
                self.tracks[tid].hits += 1
                self.tracks[tid].age = 0

                matched_track_ids.add(tid)
                matched_det_indices.add(col)

                iou_matrix[row, :] = -1.0
                iou_matrix[:, col] = -1.0

        # Create new tracks for unmatched detections
        for j, det in enumerate(detections):
            if j not in matched_det_indices:
                new_track = TrackedVehicle(
                    track_id=self.next_id,
                    bbox=det.bbox,
                    centroid=det.centroid,
                    class_name=det.class_name,
                    hits=1,
                    age=0,
                )
                self.tracks[self.next_id] = new_track
                self.next_id += 1

        # Prune expired tracks
        dead_ids = [tid for tid, track in self.tracks.items() if track.age > self.max_age]
        for tid in dead_ids:
            del self.tracks[tid]

        return list(self.tracks.values())
