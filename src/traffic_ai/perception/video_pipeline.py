"""Virtual camera rendering, YOLO inference, tracking, and video annotation pipeline."""

import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np
import traci

from traffic_ai.perception.camera_calibration import CameraCalibration
from traffic_ai.perception.density_estimator import DensityEstimator, PerceptionFrameSummary
from traffic_ai.perception.detector import VehicleDetector
from traffic_ai.perception.tracker import VehicleTracker
from traffic_ai.state.schemas import ApproachState


class VideoPipeline:
    """Renders virtual intersection video, applies YOLO perception, and generates annotated recordings."""

    def __init__(
        self,
        calibration: Optional[CameraCalibration] = None,
        detector: Optional[VehicleDetector] = None,
        tracker: Optional[VehicleTracker] = None,
        output_video_path: Optional[Path] = Path("artifacts/videos/perception_demo.mp4"),
    ):
        self.calibration = calibration or CameraCalibration()
        self.detector = detector or VehicleDetector()
        self.tracker = tracker or VehicleTracker()
        self.density_estimator = DensityEstimator(self.calibration)
        self.output_video_path = output_video_path

        if self.output_video_path:
            self.output_video_path.parent.mkdir(parents=True, exist_ok=True)

        self.video_writer: Optional[cv2.VideoWriter] = None
        self.last_summary: Optional[PerceptionFrameSummary] = None

    def render_virtual_scene(
        self,
        signal_string: str,
        sim_time: float,
    ) -> np.ndarray:
        """Renders the intersection geometry, signal heads, and active vehicles onto an RGB image."""
        w, h = self.calibration.image_width, self.calibration.image_height
        # Canvas: Dark operations asphalt background (BGR: 28, 30, 33)
        img = np.full((h, w, 3), (33, 30, 28), dtype=np.uint8)

        cx, cy = int(self.calibration.cx_px), int(self.calibration.cy_px)
        road_half_width = 30  # approx 10 meters width for 2 incoming + 2 outgoing lanes

        # 1. Draw North-South roadway
        cv2.rectangle(img, (cx - road_half_width, 0), (cx + road_half_width, h), (48, 45, 42), -1)
        # 2. Draw East-West roadway
        cv2.rectangle(img, (0, cy - road_half_width), (w, cy + road_half_width), (48, 45, 42), -1)

        # 3. Draw Road borders (crisp slate gray lines)
        border_col = (90, 85, 80)
        # NS borders
        cv2.line(img, (cx - road_half_width, 0), (cx - road_half_width, cy - road_half_width), border_col, 2)
        cv2.line(img, (cx + road_half_width, 0), (cx + road_half_width, cy - road_half_width), border_col, 2)
        cv2.line(img, (cx - road_half_width, cy + road_half_width), (cx - road_half_width, h), border_col, 2)
        cv2.line(img, (cx + road_half_width, cy + road_half_width), (cx + road_half_width, h), border_col, 2)
        # EW borders
        cv2.line(img, (0, cy - road_half_width), (cx - road_half_width, cy - road_half_width), border_col, 2)
        cv2.line(img, (0, cy + road_half_width), (cx - road_half_width, cy + road_half_width), border_col, 2)
        cv2.line(img, (cx + road_half_width, cy - road_half_width), (w, cy - road_half_width), border_col, 2)
        cv2.line(img, (cx + road_half_width, cy + road_half_width), (w, cy + road_half_width), border_col, 2)

        # 4. Yellow Center dashed lines
        yellow_col = (40, 200, 240)
        cv2.line(img, (cx, 0), (cx, cy - road_half_width), yellow_col, 2)
        cv2.line(img, (cx, cy + road_half_width), (cx, h), yellow_col, 2)
        cv2.line(img, (0, cy), (cx - road_half_width, cy), yellow_col, 2)
        cv2.line(img, (cx + road_half_width, cy), (w, cy), yellow_col, 2)

        # 5. Stop Lines (Solid White)
        white_col = (230, 230, 230)
        cv2.line(img, (cx - road_half_width, cy - road_half_width), (cx, cy - road_half_width), white_col, 3)
        cv2.line(img, (cx, cy + road_half_width), (cx + road_half_width, cy + road_half_width), white_col, 3)
        cv2.line(img, (cx + road_half_width, cy - road_half_width), (cx + road_half_width, cy), white_col, 3)
        cv2.line(img, (cx - road_half_width, cy), (cx - road_half_width, cy + road_half_width), white_col, 3)

        # 6. Signal Heads (Visual indicators at stoplines)
        def get_col(char: str):
            if char in ('G', 'g'):
                return (50, 220, 50)
            elif char in ('Y', 'y'):
                return (30, 210, 240)
            else:
                return (40, 40, 240)

        # North approach signal (link 1)
        col_n = get_col(signal_string[1] if len(signal_string) > 1 else 'r')
        cv2.circle(img, (cx - 15, cy - road_half_width - 8), 6, col_n, -1)

        # South approach signal (link 9)
        col_s = get_col(signal_string[9] if len(signal_string) > 9 else 'r')
        cv2.circle(img, (cx + 15, cy + road_half_width + 8), 6, col_s, -1)

        # East approach signal (link 5)
        col_e = get_col(signal_string[5] if len(signal_string) > 5 else 'r')
        cv2.circle(img, (cx + road_half_width + 8, cy - 15), 6, col_e, -1)

        # West approach signal (link 13)
        col_w = get_col(signal_string[13] if len(signal_string) > 13 else 'r')
        cv2.circle(img, (cx - road_half_width - 8, cy + 15), 6, col_w, -1)

        # 7. Render vehicles from live TraCI coordinates
        try:
            veh_ids = traci.vehicle.getIDList()
            for vid in veh_ids:
                x_w, y_w = traci.vehicle.getPosition(vid)
                angle_deg = traci.vehicle.getAngle(vid)
                v_type = traci.vehicle.getTypeID(vid)

                u, v = self.calibration.world_to_pixel(x_w, y_w)

                # Skip if outside canvas
                if not (0 <= u < w and 0 <= v < h):
                    continue

                # Dimensions in pixels
                length_px = 16
                width_px = 9
                col = (220, 160, 60)  # default car blue

                if "bus" in v_type:
                    length_px, width_px, col = 30, 11, (50, 140, 230)  # Orange
                elif "truck" in v_type:
                    length_px, width_px, col = 24, 11, (160, 160, 170) # Silver
                elif "motorcycle" in v_type:
                    length_px, width_px, col = 10, 6, (60, 200, 60)   # Green

                # Draw rotated rectangle for vehicle
                rect = ((float(u), float(v)), (float(width_px), float(length_px)), float(-angle_deg))
                box = cv2.boxPoints(rect)
                box = np.int32(box)
                cv2.drawContours(img, [box], 0, col, -1)
                cv2.drawContours(img, [box], 0, (20, 20, 20), 1)
        except Exception:
            pass

        return img

    def process_and_annotate_frame(
        self,
        raw_frame: np.ndarray,
        ground_truth: Optional[Dict[str, ApproachState]] = None,
        sim_time: float = 0.0,
    ) -> Tuple[np.ndarray, PerceptionFrameSummary]:
        """Runs detector, tracker, density estimator, and overlays annotations on the frame."""
        # 1. Detect
        detections = self.detector.detect(raw_frame)

        # 2. Track
        tracks = self.tracker.update(detections)

        # 3. Estimate density & compare with ground truth
        summary = self.density_estimator.estimate(
            tracks=tracks,
            detections=detections,
            ground_truth=ground_truth,
            sim_time=sim_time,
            inference_ms=self.detector.last_inference_ms,
        )
        self.last_summary = summary

        # 4. Annotate output image
        annotated = raw_frame.copy()

        # Overlay Approach ROIs (semi-transparent polygons)
        overlay = annotated.copy()
        for name, roi in self.calibration.approach_rois.items():
            cv2.fillPoly(overlay, [roi.polygon], roi.color_bgr)
            # Label approach
            center = np.mean(roi.polygon, axis=0).astype(int)
            est_cnt = summary.approaches[name].estimated_count
            gt_cnt = summary.approaches[name].ground_truth_count
            cv2.putText(
                annotated,
                f"{name.upper()}: {est_cnt} (GT:{gt_cnt})",
                (center[0] - 35, center[1]),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                (255, 255, 255),
                1,
                cv2.LINE_AA,
            )
        cv2.addWeighted(overlay, 0.20, annotated, 0.80, 0, annotated)

        # Draw Detection Bounding Boxes & IDs
        for track in tracks:
            x1, y1, x2, y2 = track.bbox
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 255), 1)
            lbl = f"ID:{track.track_id} {track.class_name}"
            cv2.putText(
                annotated,
                lbl,
                (x1, max(12, y1 - 4)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.32,
                (0, 255, 255),
                1,
                cv2.LINE_AA,
            )

        # Top Telemetry Banner
        cv2.rectangle(annotated, (0, 0), (self.calibration.image_width, 36), (15, 15, 20), -1)
        banner_text = (
            f"TRAFFIC AI PERCEPTION | YOLOv8n | Time: {sim_time:0.1f}s | "
            f"FPS: {summary.fps} | Det: {summary.total_detections} | MAE: {summary.mean_absolute_error}"
        )
        cv2.putText(
            annotated,
            banner_text,
            (12, 22),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (0, 230, 255),
            1,
            cv2.LINE_AA,
        )

        return annotated, summary

    def record_frame(self, frame: np.ndarray, fps: float = 10.0) -> None:
        """Appends annotated frame to output video file."""
        if self.output_video_path is None:
            return

        if self.video_writer is None:
            h, w = frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self.video_writer = cv2.VideoWriter(str(self.output_video_path), fourcc, fps, (w, h))

        self.video_writer.write(frame)

    def close(self) -> None:
        """Finalizes and flushes output video."""
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
