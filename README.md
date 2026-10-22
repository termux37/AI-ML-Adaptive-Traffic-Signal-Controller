# AI & ML Based Adaptive Traffic Control System

A research and simulation platform for evaluating adaptive traffic signal control algorithms at isolated signalized intersections. The system couples microscopic vehicular traffic modeling (Eclipse SUMO) with deterministic safety enforcement, classic traffic engineering heuristics, deep reinforcement learning, and a simulated computer-vision perception pipeline.

---

## What the Project Is

Traditional traffic signal systems in municipal networks predominantly rely on static time-of-day plans (Fixed-Time) or localized induction-loop actuations (Vehicle-Actuated). While these methods are predictable, they struggle during asymmetric demand surges, incident-induced congestion, and non-stationary flow patterns. 

This platform evaluates how decentralized feedback heuristics (Max-Pressure) and model-free reinforcement learning (Deep Q-Networks) compare against standard traffic engineering baselines under controlled, reproducible conditions. 

The project models a four-way signalized intersection with dedicated turning bays, multi-class vehicular traffic, and realistic driver behavior. It incorporates a hard architectural separation between the decision policy and the signal hardware: control policies only emit *action proposals*, while a standalone **Deterministic Signal Safety Manager** verifies clearance timings and prevents hazardous phase conflicts before commands reach the simulation engine.

Additionally, the platform includes a simulated top-down camera pipeline running YOLOv8 object detection and spatial tracking to evaluate closed-loop control under synthetic perception noise versus perfect simulator ground truth.

---

## How It Works

The platform operates as a synchronized discrete-time control loop where the microscopic simulation advances at 1-second intervals ($dt = 1.0\text{ s}$), and control decisions occur at configured intervals (e.g., every 5 seconds).

```
 +-------------------------------------------------------------------------+
 |                         SUMO Microscopic Engine                         |
 |      (Krauss Car-Following, 4-Way Intersection, 16 Link Movements)      |
 +-------------------------------------------------------------------------+
             |                                              ^
             | Vehicle positions, speeds, detectors         | Validated phase string
             v                                              |
 +-------------------------------+              +--------------------------+
 |       State Extraction        |              | Deterministic Safety     |
 |  - TraCI Ground Truth         |              | Manager                  |
 |  - Synthetic Vision (YOLOv8)  |              | - Min Green (10s)        |
 +-------------------------------+              | - Max Green (60s)        |
             |                                  | - Yellow Clearance (3s)  |
             v                                  | - All-Red Clearance (2s) |
 +-------------------------------+              +--------------------------+
 |      Observation Builder      |                          ^
 |  25-dim normalized state      |                          | Target phase
 +-------------------------------+                          | proposal
             |                                              |
             +--------------------> [ Active Controller ] --+
                                    - Fixed-Time
                                    - Vehicle-Actuated
                                    - Max-Pressure
                                    - Deep Q-Network (DQN)
```

### 1. Microscopic Simulation Environment
- **Intersection Topology:** A four-way intersection (`junction_center`) with North, South, East, and West approach legs.
- **Lane Configuration:** Two incoming lanes (through/right lane and a dedicated left-turn pocket) and two outgoing lanes per approach, yielding 16 distinct link movements.
- **Car-Following Dynamics:** Simulated using the Krauss model with stochastic driver imperfection ($\sigma = 0.5$, driver reaction time $\tau = 1.0\text{ s}$).
- **Sensors:** Stop-line induction loops (E1 detectors) on all incoming lanes providing instantaneous occupancy and vehicle speed measurements.

### 2. State Representation & Observation Space
The control environment (implemented as a Gymnasium interface) constructs a 25-dimensional continuous observation vector normalized to $[0.0, 1.0]$:
- **Approach Queue & Flow Features (20 dimensions):** For each of the 4 approaches (North, South, East, West), 5 normalized metrics are measured:
  1. Active vehicle count on the approach ($N / 30.0$)
  2. Queued/halting vehicle count ($Q / 30.0$, speed $< 0.1\text{ m/s}$)
  3. Mean approach speed ($v / 13.89\text{ m/s}$)
  4. Accumulated waiting time ($W / 300.0\text{ s}$)
  5. Detector lane occupancy ratio ($[0.0, 1.0]$)
- **Active Signal State (4 dimensions):** One-hot encoded vector representing the current green phase index ($p \in \{0, 1, 2, 3\}$).
- **Phase Elapsed Time (1 dimension):** Normalized duration spent in the active green phase ($t_{green} / t_{max}$).

### 3. Signal Phase Catalog
The intersection uses a 4-phase dual-ring design:
- **Phase 0 (N_S_THRU):** North-South through and right turns green (`GGGgrrrrGGGgrrrr`).
- **Phase 1 (N_S_LEFT):** North-South protected left turns green (`rrrGrrrrrrrGrrrr`).
- **Phase 2 (E_W_THRU):** East-West through and right turns green (`rrrrGGGgrrrrGGGg`).
- **Phase 3 (E_W_LEFT):** East-West protected left turns green (`rrrrrrrGrrrrrrrG`).

### 4. Deterministic Signal Safety Manager
Machine learning policies and heuristic controllers are not permitted to write signal strings directly to TraCI. Instead, every action passes through `DeterministicSafetyManager`, which enforces:
- **Minimum Green Time ($t_{min} = 10.0\text{ s}$):** A green phase cannot be terminated prematurely, allowing queue startup dissipation and pedestrian walk safety.
- **Maximum Green Time ($t_{max} = 60.0\text{ s}$):** Prevents phase holding and cross-street vehicle starvation.
- **Yellow Clearance Interval ($t_{yellow} = 3.0\text{ s}$):** Displays amber for clearing the dilemma zone based on approach design speed ($50\text{ km/h}$).
- **All-Red Clearance Interval ($t_{red} = 2.0\text{ s}$):** Holds all approaches in red (`rrrrrrrrrrrrrrrr`) to clear conflicting vehicular movements before granting opposing green.
- **Conflict Prevention:** Rejects illegal transitions; while clearance timers run, any external phase switch requests are discarded.

### 5. Control Regimes
- **Fixed-Time Baseline:** Cyclic round-robin scheduler with static phase splits (e.g., 90-second total cycle length).
- **Vehicle-Actuated Baseline:** Extends green time in increments when detector gap headway is below 3.0 seconds, subject to minimum green and maximum green cutoffs.
- **Max-Pressure Controller:** Implements the Varaiya (2013) queue differential formulation:
  $$w(l, m) = x_l - x_m$$
  where $x_l$ is the upstream queue on incoming lane $l$, and $x_m$ is the downstream occupancy on receiving lane $m$. The phase selected maximizes aggregate pressure relief:
  $$p^* = \arg\max_p \sum_{(l, m) \in \mathcal{M}(p)} w(l, m)$$
- **Deep Q-Network (DQN):** Deep Q-Learning agent with target network synchronization, experience replay, and $\epsilon$-greedy exploration. The reward function aligns with PressLight principles:
  $$R_t = - w_q \sum Q - w_w \sum W + w_{th} N_{completed} - w_{sw} \mathbb{I}_{switch} - w_{starv} t_{starve}$$

### 6. Synthetic Vision Pipeline
To evaluate performance with visual sensing rather than direct simulation queries:
- **Top-Down Virtual Rendering:** Generates orthographic scene frames from vehicle positions and bounding extents.
- **Object Detection:** Ultralytics YOLOv8n identifies vehicle classes (car, truck, bus, motorcycle).
- **Spatial Tracking:** Frame-to-frame spatial IoU association assigns persistent track IDs.
- **Approach Polygon Mapping:** Homography and region-of-interest (ROI) polygons assign detections to incoming approach lanes (North, South, East, West).
- **Telemetry & Validation:** Estimates are compared continuously against ground-truth TraCI arrays to compute Mean Absolute Error (MAE).

### 7. Evaluation Metrics & Fairness
- **Throughput:** Vehicles completing trips per hour of simulation ($vph$).
- **Queue Length:** Average number of stopped vehicles ($\le 0.1\text{ m/s}$) across all approaches.
- **Average Waiting Time:** Mean cumulative stopped delay experienced by vehicles.
- **Jain's Fairness Index:** Measures delay equity across all 4 approach legs to identify starvation:
  $$\mathcal{J}(w_1, w_2, w_3, w_4) = \frac{\left(\sum_{i=1}^4 w_i\right)^2}{4 \cdot \sum_{i=1}^4 w_i^2}$$
  bounded between $0.25$ (complete starvation of 3 approaches) and $1.0$ (identical delay across all legs).

---

## Technologies Used

| Layer | Tools & Libraries | Role in System |
| :--- | :--- | :--- |
| **Microscopic Simulation** | Eclipse SUMO (>= 1.20), TraCI Python API, `netconvert` | Intersection network, vehicle car-following physics, signal state actuation, loop detector simulation |
| **Deep Learning & RL** | PyTorch, Stable-Baselines3, Gymnasium | Deep Q-Network policy, experience replay buffer, continuous observation space, discrete action dispatching |
| **Computer Vision** | Ultralytics YOLOv8 (`yolov8n`), OpenCV, NumPy, SciPy | Object detection, spatial IoU tracking, geometric approach ROI mapping, MAE calculation |
| **Backend & Modeling** | Python 3.12, Pydantic, PyYAML, Pandas | Runtime data validation contracts, configuration loading, timeseries data aggregation, manifest serialization |
| **Visualization & UI** | Streamlit, Plotly, Altair | 11-page dark operations console, interactive telemetry, live simulation streaming, phase timing charts |
| **Verification & Testing** | Pytest | Deterministic unit tests for safety manager, perception modules, RL environment, and simulation integration |

---

## Repository Structure

```text
ai_ml_project/
├── app.py                          # Streamlit operations console entry point
├── pyproject.toml                  # Python package configuration and pytest settings
├── README.md                       # System architecture and literature reference
├── LICENSE                         # MIT License
├── .gitignore                      # Git exclusion rules
├── .env.example                    # Environment variable configuration template
├── launch.py                       # Automated verification and startup pipeline
├── launch.bat                      # Windows batch startup launcher
├── launch.ps1                      # Windows PowerShell startup launcher
├── configs/
│   ├── app.yaml                    # UI and dashboard parameters
│   ├── simulation.yaml             # SUMO network, timestep, and port settings
│   ├── perception.yaml             # Camera geometry, YOLO confidence, and ROI polygons
│   ├── rl.yaml                     # DQN hyperparameters and reward function weights
│   └── experiments.yaml            # Benchmark scenario matrices and seed lists
├── simulation/
│   ├── network/                    # SUMO node, edge, connection, net, and detector XMLs
│   ├── routes/                     # Synthetic traffic demand profiles (balanced, bursty, heavy)
│   ├── scenario.sumocfg            # Master SUMO configuration file
│   └── gui-settings.cfg.xml        # Desktop SUMO-GUI viewport and rendering configuration
├── src/traffic_ai/
│   ├── config/schemas.py           # Pydantic schemas and strict runtime data contracts
│   ├── simulation/                 # TraCI connection lifecycle and scenario generator
│   ├── control/                    # Safety manager, phase catalog, and 4 signal controllers
│   ├── perception/                 # YOLO inference, IoU tracker, calibration, and renderer
│   ├── state/                      # Ground truth adapter and observation builder
│   ├── metrics/                    # Step metrics collector, stats aggregator, manifest generator
│   ├── training/                   # Gymnasium environment wrapper and DQN training loop
│   ├── experiments/                # Multi-seed multi-scenario benchmark evaluation runner
│   ├── dashboard/                  # Operations console pages and dark design system
│   └── utils/                      # Structured logging and hardware diagnostics
├── scripts/
│   ├── check_environment.py        # Environment and dependency verification
│   ├── generate_scenario.py        # Demand generation CLI
│   ├── run_simulation.py           # Standalone single-run simulation CLI
│   ├── train_agent.py              # DQN training CLI
│   ├── evaluate_agent.py           # Multi-controller benchmark CLI
│   └── make_demo_video.py          # Perception demo video generator
└── tests/
    ├── unit/                       # Tests for safety invariants, environment, and vision
    ├── integration/                # End-to-end multi-controller simulation tests
    └── smoke/                      # Quick environment verification tests
```

---

## Research Papers & Literature References

The theoretical foundation, algorithmic formulations, and safety mechanisms in this project are based on the following published literature and technical standards:

### 1. Max-Pressure Control & Network Stability
- **Varaiya, P. (2013).** *The max-pressure controller for arbitrary networks of signalized intersections.* Advances in Dynamic Network Modeling in Complex Systems, pp. 27–66. Springer, Boston, MA.  
  *Significance:* Establishes the mathematical proof that decentralized feedback control based on upstream minus downstream queue differentials guarantees maximum network throughput without requiring explicit knowledge of arrival demand rates.
- **Wei, H., Chen, C., Zheng, G., Wu, K., Gayah, V., Xu, K., & Li, Z. (2019).** *PressLight: Learning Max Pressure Control to Coordinate Traffic Signals in Arterial Networks.* Proceedings of the 25th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining (KDD '19), pp. 1290–1298.  
  *Significance:* Bridges classical Max-Pressure control theory and deep reinforcement learning by designing reward functions that minimize pressure changes, aligning reinforcement learning policies with Lyapunov queue stability.

### 2. Reinforcement Learning for Traffic Signal Control
- **Mnih, V., Kavukcuoglu, K., Silver, D., Rusu, A. A., Veness, J., Bellemare, M. G., ... & Hassabis, D. (2015).** *Human-level control through deep reinforcement learning.* Nature, 518(7540), 529–533.  
  *Significance:* Introduces deep Q-networks (DQN) with target network stabilization and experience replay mechanisms utilized in this project's learning agent.
- **Wei, H., Zheng, G., Yao, H., & Li, Z. (2018).** *IntelliLight: A Reinforcement Learning Approach for Intelligent Traffic Light Control.* Proceedings of the 24th ACM SIGKDD International Conference on Knowledge Discovery & Data Mining (KDD '18), pp. 2496–2505.  
  *Significance:* Demonstrates phase-duration state representations and multi-objective reward designs (delay, queue, phase transitions) for signalized intersections.
- **Chen, C., Wei, H., Xu, N., Zheng, G., Yang, M., Xiong, Y., Xu, K., & Li, Z. (2020).** *Toward a Thousand Lights: Decentralized Deep Reinforcement Learning for Large-Scale Traffic Signal Control.* Proceedings of the AAAI Conference on Artificial Intelligence, 34(04), pp. 3414–3421.  
  *Significance:* Analyzes scalable decentralized state-action formulations and communication-efficient policies across independent intersection agents.
- **Ault, J., & Sharon, G. (2021).** *Reinforcement Learning Benchmarks for Traffic Signal Control (RESCO).* Thirty-fifth Conference on Neural Information Processing Systems (NeurIPS 2021) Datasets and Benchmarks Track.  
  *Significance:* Provides standard benchmark protocols and reproducible metrics for traffic signal control algorithms.

### 3. Microscopic Traffic Modeling & Car-Following Dynamics
- **Lopez, P. A., Behrisch, M., Bieker-Walz, L., Erdmann, J., Flötteröd, Y. P., Hilbrich, R., Lücken, L., Rummel, J., Wagner, P., & Wießner, E. (2018).** *Microscopic Traffic Simulation using SUMO.* The 21st IEEE International Conference on Intelligent Transportation Systems (ITSC 2018), pp. 2575–2582.  
  *Significance:* Technical reference for Eclipse SUMO, its TraCI socket architecture, induction loop modeling, and traffic light controller interfaces.
- **Krauss, S., Wagner, P., & Gawron, C. (1997).** *Metastable states in a microscopic model of traffic flow.* Physical Review E, 55(5), 5597–5602.  
  *Significance:* Formulates the stochastic car-following model used for vehicle kinematics, acceleration bounds, and collision avoidance in the simulation network.

### 4. Traffic Signal Timing Standards & Clearance Intervals
- **Federal Highway Administration (FHWA). (2009 / 2023).** *Manual on Uniform Traffic Control Devices for Streets and Highways (MUTCD).* U.S. Department of Transportation.  
  *Significance:* Standard specifications for signal phase displays, minimum green timing intervals, yellow change intervals, and red clearance calculations.
- **Roess, R. P., Prassas, E. S., & McShane, W. R. (2010).** *Traffic Engineering* (4th ed.). Pearson Prentice Hall.  
  *Significance:* Theoretical basis for intersection capacity, dilemma zone equations, and vehicle delay modeling.
- **Webster, F. V. (1958).** *Traffic Signal Settings.* Road Research Technical Paper No. 39. Road Research Laboratory, HMSO, London.  
  *Significance:* Foundation of pre-timed signal optimization and delay minimization equations used in the Fixed-Time controller baseline.
- **Gordon, R. L., & Tighe, W. (2005).** *Traffic Control Systems Handbook.* Federal Highway Administration, Report FHWA-HOP-06-006.  
  *Significance:* Standard reference for vehicle-actuated signal operations, passage time calculations, detector placement, and gap-out logic.

### 5. Computer Vision & Vehicle Tracking
- **Jocher, G., Chaurasia, A., & Qiu, J. (2023).** *Ultralytics YOLOv8.* Version 8.0.0. GitHub repository: https://github.com/ultralytics/ultralytics.  
  *Significance:* Real-time deep learning object detector used for identifying multi-class vehicles from simulated camera feeds.
- **Bewley, A., Ge, Z., Ott, L., Ramos, F., & Upcroft, B. (2016).** *Simple online and realtime tracking.* 2016 IEEE International Conference on Image Processing (ICIP), pp. 3464–3468.  
  *Significance:* Algorithmic basis for the spatial intersection-over-union (IoU) vehicle tracking logic used in the perception module.

### 6. Quantitative Fairness & Resource Allocation
- **Jain, R., Chiu, D. M., & Hawe, W. (1984).** *A Quantitative Measure of Fairness and Discrimination for Resource Allocation in Shared Computer Systems.* Technical Report TR-301, Digital Equipment Corporation.  
  *Significance:* Mathematical formulation of Jain's Fairness Index, used here to assess whether signal controllers equitably distribute green time and avoid starving minority traffic movements.
