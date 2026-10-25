"""YOLO vehicle detector with confidence thresholding and class filtering."""

import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
from ultralytics import YOLO


@dataclass
class Detection:
    """Bounding box detection with class, confidence, and spatial centroid."""
    bbox: Tuple[int, int, int, int]  # x1, y1, x2, y2 (pixel coordinates)
    confidence: float
    class_id: int
    class_name: str

    @property
    def centroid(self) -> Tuple[int, int]:
        x1, y1, x2, y2 = self.bbox
        return int((x1 + x2) / 2), int((y1 + y2) / 2)


class VehicleDetector:
    """Performs object detection on camera frames using Ultralytics YOLO."""

    TARGET_CLASSES = {
        2: "car",
        3: "motorcycle",
        5: "bus",
        7: "truck",
    }

    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        confidence_threshold: float = 0.30,
        device: str = "cpu",
    ):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.device = device
        self.model = YOLO(model_path)
        self.last_inference_ms: float = 0.0

    def detect(self, frame: np.ndarray) -> List[Detection]:
        """Runs detection on an RGB frame and returns filtered vehicle detections."""
        t0 = time.perf_counter()
        results = self.model.predict(
            source=frame,
            conf=self.confidence_threshold,
            device=self.device,
            verbose=False,
        )
        self.last_inference_ms = round((time.perf_counter() - t0) * 1000.0, 2)

        detections: List[Detection] = []
        if not results or len(results) == 0:
            return detections

        boxes = results[0].boxes
        if boxes is None:
            return detections

        for box in boxes:
            cls_id = int(box.cls[0].item())
            if cls_id in self.TARGET_CLASSES:
                conf = float(box.conf[0].item())
                xyxy = box.xyxy[0].cpu().numpy().astype(int)
                detections.append(
                    Detection(
                        bbox=(int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])),
                        confidence=round(conf, 3),
                        class_id=cls_id,
                        class_name=self.TARGET_CLASSES[cls_id],
                    )
                )

        return detections
