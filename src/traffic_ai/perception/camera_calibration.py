"""Camera calibration and spatial ROI mapping for approach zones."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np


@dataclass
class ApproachROI:
    """Polygon region defining an approach zone in image coordinates."""
    name: str
    polygon: np.ndarray  # Shape (N, 2), dtype int32
    color_bgr: Tuple[int, int, int]


class CameraCalibration:
    """Maps intersection world coordinates (meters) to virtual camera pixel space."""

    def __init__(
        self,
        image_width: int = 800,
        image_height: int = 800,
        center_world: Tuple[float, float] = (250.0, 250.0),
        pixels_per_meter: float = 3.0,
    ):
        self.image_width = image_width
        self.image_height = image_height
        self.center_world = center_world
        self.ppm = pixels_per_meter

        self.cx_px = image_width / 2.0
        self.cy_px = image_height / 2.0

        # Define calibrated approach polygons in pixel space
        # Approaches are 2 lanes wide (approx 7.0m = 21px wide), extending 70m (210px) upstream
        self.approach_rois: Dict[str, ApproachROI] = {
            "north": ApproachROI(
                name="north",
                polygon=np.array([
                    [self.cx_px - 22, 50],
                    [self.cx_px - 2,  50],
                    [self.cx_px - 2,  self.cy_px - 30],
                    [self.cx_px - 22, self.cy_px - 30],
                ], dtype=np.int32),
                color_bgr=(255, 120, 50),
            ),
            "south": ApproachROI(
                name="south",
                polygon=np.array([
                    [self.cx_px + 2,  self.cy_px + 30],
                    [self.cx_px + 22, self.cy_px + 30],
                    [self.cx_px + 22, self.image_height - 50],
                    [self.cx_px + 2,  self.image_height - 50],
                ], dtype=np.int32),
                color_bgr=(50, 180, 255),
            ),
            "east": ApproachROI(
                name="east",
                polygon=np.array([
                    [self.cx_px + 30, self.cy_px - 22],
                    [self.image_width - 50, self.cy_px - 22],
                    [self.image_width - 50, self.cy_px - 2],
                    [self.cx_px + 30, self.cy_px - 2],
                ], dtype=np.int32),
                color_bgr=(100, 255, 100),
            ),
            "west": ApproachROI(
                name="west",
                polygon=np.array([
                    [50, self.cy_px + 2],
                    [self.cx_px - 30, self.cy_px + 2],
                    [self.cx_px - 30, self.cy_px + 22],
                    [50, self.cy_px + 22],
                ], dtype=np.int32),
                color_bgr=(255, 50, 200),
            ),
        }

    def world_to_pixel(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """Converts SUMO world coords (meters) to canvas pixel (u, v)."""
        dx = world_x - self.center_world[0]
        dy = world_y - self.center_world[1]
        u = int(round(self.cx_px + dx * self.ppm))
        # Note: image Y is inverted relative to standard Cartesian
        v = int(round(self.cy_px - dy * self.ppm))
        return u, v

    def pixel_to_world(self, u: int, v: int) -> Tuple[float, float]:
        """Converts canvas pixel (u, v) back to SUMO world coords."""
        dx = (u - self.cx_px) / self.ppm
        dy = (self.cy_px - v) / self.ppm
        return self.center_world[0] + dx, self.center_world[1] + dy

    def assign_approach(self, u: int, v: int) -> Optional[str]:
        """Finds which approach ROI polygon contains point (u, v)."""
        point = (float(u), float(v))
        for name, roi in self.approach_rois.items():
            if cv2.pointPolygonTest(roi.polygon, point, measureDist=False) >= 0:
                return name
        return None
