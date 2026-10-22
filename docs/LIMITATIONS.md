# AI & ML Based Adaptive Traffic Control System - Scientific & Engineering Limitations

## 1. Virtual Simulation-to-Reality Gap
- **Microscopic Assumptions:** The simulation engine (SUMO) utilizes the Krauss car-following model and heuristic lane changing. While realistic for aggregate traffic studies, real-world human drivers display non-Markovian behaviors, heterogeneous aggression levels, distracted driving, and erratic pedestrian interference that are not fully modeled in synthetic routes.
- **Physical Road Hardware:** Real municipal intersections utilize NEMA TS-2 or 170/2070 controller cabinets, conflict monitor units (CMU / MMU), inductive loop amplifier cards, and optical emergency preemption. Adaptive Traffic Control System simulates the logical behavior of these systems but does not interface with physical electrical relays or hardware-in-the-loop (HIL) test benches.

## 2. Computer Vision & Perception Constraints
- **Perspective and Occlusion:** The virtual camera operates in a top-down planar viewpoint. In real-world roadside camera installations (e.g. pole-mounted or mast-arm cameras), oblique viewpoints cause severe vehicle occlusion where tall trucks obscure smaller sedans and motorcycles.
- **Environmental Factors:** Synthetic rendered video does not simulate severe rain, snow, optical lens flare, night-time headlight glare, or lens fogging, which degrade real-world YOLO detection confidence.
- **Queue Length Calibration:** Queue length inferred from camera detections uses geometric ROI bounding box counts. While accurate in top-down views, real roadside cameras require homography calibration and bird's-eye-view (BEV) inverse perspective mapping to avoid overestimating queues.

## 3. Scope of Single Intersection Control
- **Arterial Coordination:** Adaptive Traffic Control System explicitly limits its scope to a single 4-way signalized intersection. It does not model green wave coordination, arterial signal offset synchronization, or multi-agent decentralized network policies.
- **Pedestrian and Cyclist Phases:** The model prioritizes vehicular demand. Pedestrian push-button phases and exclusive bicycle intervals are omitted to avoid unverified synthetic assumptions.

## 4. Regulatory & Certification Disclaimers
AI & ML Based Adaptive Traffic Control System is an academic decision-support and machine learning research demonstration. It has not been submitted for or certified under NEMA, FHWA, EN 12675, or ISO 26262 functional safety standards. It must not be deployed to control physical traffic lights on public roadways.
