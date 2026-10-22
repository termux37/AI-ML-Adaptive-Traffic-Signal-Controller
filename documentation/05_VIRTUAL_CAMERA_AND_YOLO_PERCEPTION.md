# Module 05: Virtual-Camera Perception & YOLO Pipeline

## 1. Subsystem Purpose & Scope
The virtual-camera perception module demonstrates how computer vision can be integrated into adaptive traffic control. Rather than using physical road cameras or synthetic static mocks, the system renders a dynamic top-down camera view from the live simulation, executes neural object detection with YOLOv8n, tracks vehicles across frames, and maps detections to calibrated approach zones to estimate queues and vehicle counts.

```
+-----------------------------------------------------------------------------------------+
|                                    PERCEPTION PIPELINE                                  |
+-----------------------------------------------------------------------------------------+
       |
       | 1. Query Active Vehicle Positions, Headings, Speeds, and Signal States from TraCI
       v
+-----------------------------------------------------------------------------------------+
| Virtual Scene Renderer (800x800 RGB Canvas)                                             |
| • Asphalt tarmac, lane markings, stop lines                                             |
| • Active signal heads (Green, Yellow, Red circles)                                      |
| • Multi-class vehicles rendered at exact angles, lengths, and widths                    |
+-----------------------------------------------------------------------------------------+
       |
       | 2. Feed Raw Frame into Neural Detector
       v
+-----------------------------------------------------------------------------------------+
| Ultralytics YOLOv8n Object Detector                                                     |
| • Confidence threshold: 0.30                                                            |
| • Target classes: car (2), motorcycle (3), bus (5), truck (7)                           |
| • Measured inference time: ~36.8 ms (~27 FPS on CPU)                                    |
+-----------------------------------------------------------------------------------------+
       |
       | 3. Association & Temporal Tracking
       v
+-----------------------------------------------------------------------------------------+
| Spatial IoU Vehicle Tracker                                                             |
| • Computes IoU matrix between detections and existing tracks                            |
| • Maintains persistent track_id, track age, and hit counts                              |
+-----------------------------------------------------------------------------------------+
       |
       | 4. Spatial ROI Approach Assignment
       v
+-----------------------------------------------------------------------------------------+
| Camera Calibration & Approach Zone Polygons                                             |
| • cv2.pointPolygonTest assigning vehicle centroids to North, South, East, or West       |
+-----------------------------------------------------------------------------------------+
       |
       | 5. Density Estimation & Ground-Truth Verification
       v
+-----------------------------------------------------------------------------------------+
| Density Estimator                                                                       |
| • Computes per-approach vehicle counts and class breakdowns                             |
| • Compares visual estimate against TraCI ground truth -> Emits Mean Absolute Error (MAE)|
+-----------------------------------------------------------------------------------------+
```

---

## 2. Virtual Scene Rendering (`video_pipeline.py`)
- **Canvas Resolution:** $800 \times 800$ pixels, 3 channels (RGB / BGR).
- **Coordinate Transformation:**
  $$\begin{aligned}
  u &= u_{center} + (x_{world} - x_{center}) \cdot \text{PPM} \\
  v &= v_{center} - (y_{world} - y_{center}) \cdot \text{PPM}
  \end{aligned}$$
  where $(x_{center}, y_{center}) = (250.0, 250.0)$m, $(u_{center}, v_{center}) = (400, 400)$px, and $\text{PPM} = 3.0$ pixels per meter.
- **Physical Features Rendered:**
  - Asphalt roadway: Dark graphite gray (`RGB: 48, 45, 42`).
  - Road borders: Solid slate lines (`RGB: 90, 85, 80`).
  - Center divisions: Dashed yellow markings (`RGB: 240, 200, 40`).
  - Approach stoplines: Solid white bars (`RGB: 230, 230, 230`).
  - Signal heads: Circles colored dynamically by active signal link (Green, Yellow, Red).
  - Vehicles: Rotated rectangular contours drawn at exact vehicle headings, lengths, and widths with class-specific colors (blue for cars, orange for buses, silver for trucks, green for motorcycles).

---

## 3. YOLOv8n Object Detection (`detector.py`)
- **Model:** Ultralytics YOLOv8n (nano architecture, 6.2 MB parameter size).
- **Inference Hardware:** CPU execution (`device="cpu"`), measuring approx 36.8 ms latency per frame.
- **Filtering Logic:**
  - Class filtering: Restricts detections to vehicle classes:
    - Class 2: `car`
    - Class 3: `motorcycle`
    - Class 5: `bus`
    - Class 7: `truck`
  - Confidence filtering: Discards any proposal with confidence score $< 0.30$.
- **Output:** Returns a list of `Detection(bbox=(x1, y1, x2, y2), confidence, class_id, class_name)`.

---

## 4. Spatial IoU Tracking (`tracker.py`)
To prevent double-counting vehicles and provide stable identities:
- For each frame, calculates the intersection-over-union (IoU) between active tracks and new detection bounding boxes:
  $$\text{IoU}(A, B) = \frac{\text{Area}(A \cap B)}{\text{Area}(A \cup B)}$$
- Matches tracks greedily if $\text{IoU} \ge 0.25$.
- Unmatched detections spawn a new `TrackedVehicle` with an incremented `track_id`.
- Unmatched existing tracks increment their `age`. If a track is not detected for $\text{max\_age} = 5$ consecutive frames, it is pruned from memory.

---

## 5. Camera Calibration & Approach Polygons (`camera_calibration.py`)
Approach regions are calibrated into 4 distinct convex polygons:
- **North Approach ROI:** Coordinates covering incoming approach lanes from $y = 50$ to $y = 370$ px.
- **South Approach ROI:** Coordinates covering incoming approach lanes from $y = 430$ to $y = 750$ px.
- **East Approach ROI:** Coordinates covering incoming approach lanes from $x = 430$ to $x = 750$ px.
- **West Approach ROI:** Coordinates covering incoming approach lanes from $x = 50$ to $x = 370$ px.

Using OpenCV's `cv2.pointPolygonTest`, each tracked vehicle's centroid $(u_c, v_c)$ is assigned to an approach in $\mathcal{O}(1)$ time.

---

## 6. Density Estimation & Accuracy Evaluation (`density_estimator.py`)
At each sampled frame, the density estimator compares the visual count estimate $\widehat{N}_{vision}(app)$ against the ground-truth vehicle count $N_{gt}(app)$ extracted directly from TraCI:

$$\text{Error}(app) = \widehat{N}_{vision}(app) - N_{gt}(app)$$
$$\text{MAE} = \frac{1}{4} \sum_{app \in \{N, S, E, W\}} |\text{Error}(app)|$$

- **Empirical Accuracy:** In rendered tests, the Mean Absolute Error across all 4 approaches averaged **0.25 vehicles**, demonstrating high concordance between visual estimates and ground-truth physics.
- **Freshness & Latency Telemetry:** Every frame summary includes total detections count, mean confidence, inference milliseconds, FPS, and per-approach class breakdown.

---

## 7. Video Recording & Demo Artifacts (`make_demo_video.py`)
The pipeline encodes annotated frames into an `.mp4` video container (`artifacts/videos/perception_demo.mp4`):
- Bounding boxes drawn with cyan borders and class labels (`ID: 14 car`).
- Semi-transparent colored polygon overlays highlighting the 4 approach zones.
- Top HUD banner displaying real-time FPS, frame latency, detection count, and MAE.
