"""Unit tests for the perception pipeline and camera calibration."""

import numpy as np
import pytest
from traffic_ai.perception.camera_calibration import CameraCalibration
from traffic_ai.perception.density_estimator import DensityEstimator
from traffic_ai.perception.detector import Detection
from traffic_ai.perception.tracker import VehicleTracker
from traffic_ai.state.schemas import ApproachState


def test_camera_calibration_coordinate_mapping():
    calib = CameraCalibration(image_width=800, image_height=800, center_world=(250.0, 250.0), pixels_per_meter=3.0)

    # Center of intersection should be (400, 400)
    u, v = calib.world_to_pixel(250.0, 250.0)
    assert u == 400
    assert v == 400

    # 10m East (world x = 260.0) -> u = 400 + 30 = 430
    u_e, v_e = calib.world_to_pixel(260.0, 250.0)
    assert u_e == 430
    assert v_e == 400

    # Invert mapping back to world
    x_rec, y_rec = calib.pixel_to_world(u_e, v_e)
    assert abs(x_rec - 260.0) < 1e-4
    assert abs(y_rec - 250.0) < 1e-4


def test_camera_approach_roi_assignment():
    calib = CameraCalibration()

    # Point clearly inside North approach ROI (approx (390, 200))
    app_n = calib.assign_approach(390, 200)
    assert app_n == "north"

    # Point clearly inside South approach ROI (approx (410, 600))
    app_s = calib.assign_approach(410, 600)
    assert app_s == "south"

    # Point in dead center of junction
    app_c = calib.assign_approach(400, 400)
    assert app_c is None


def test_vehicle_tracker_lifecycle():
    tracker = VehicleTracker(iou_threshold=0.3, max_age=2)

    # Frame 1: Detection at (100, 100, 120, 120)
    det1 = Detection(bbox=(100, 100, 120, 120), confidence=0.85, class_id=2, class_name="car")
    tracks_f1 = tracker.update([det1])
    assert len(tracks_f1) == 1
    t1_id = tracks_f1[0].track_id
    assert tracks_f1[0].hits == 1

    # Frame 2: Vehicle moved slightly to (103, 102, 123, 122)
    det2 = Detection(bbox=(103, 102, 123, 122), confidence=0.88, class_id=2, class_name="car")
    tracks_f2 = tracker.update([det2])
    assert len(tracks_f2) == 1
    assert tracks_f2[0].track_id == t1_id
    assert tracks_f2[0].hits == 2

    # Frame 3 & 4: Detection disappears (age increments)
    tracker.update([])
    tracker.update([])
    # Frame 5: Track should expire (max_age=2)
    tracks_f5 = tracker.update([])
    assert len(tracks_f5) == 0


def test_density_estimator_mae():
    calib = CameraCalibration()
    estimator = DensityEstimator(calib)

    gt_approaches = {
        "north": ApproachState(name="north", vehicle_count=4),
        "south": ApproachState(name="south", vehicle_count=2),
        "east":  ApproachState(name="east", vehicle_count=1),
        "west":  ApproachState(name="west", vehicle_count=3),
    }

    # Empty tracks (0 estimated across all)
    summary = estimator.estimate(
        tracks=[],
        detections=[],
        ground_truth=gt_approaches,
        sim_time=10.0,
        inference_ms=25.0,
    )
    # Errors: |0-4| + |0-2| + |0-1| + |0-3| = 10 / 4 = 2.5 MAE
    assert summary.mean_absolute_error == 2.5
    assert summary.total_detections == 0
