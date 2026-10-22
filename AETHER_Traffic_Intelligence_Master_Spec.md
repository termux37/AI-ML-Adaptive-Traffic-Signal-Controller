# MASTER ENGINEERING SPECIFICATION

## AI/ML Adaptive Traffic Signal Controller --- Virtual Research Platform

**Project deadline:** 30 October 2026\
**Target development environment:** Windows 10/11, 16 GB RAM, NVIDIA
GPU\
**Scope:** One configurable four-way signalized intersection, fully
virtual simulation\
**Primary audience:** Gemini Antigravity acting as autonomous software
engineer\
**Delivery standard:** Production-minded, research-grade, highly
polished, reproducible, documented

------------------------------------------------------------------------

# 0. Instructions to the coding agent

You are responsible for implementing a complete software project, not
merely producing a plan, mockup, or isolated snippets. Work directly in
the project workspace. Inspect the current repository before changing
it. Preserve working code, establish a clear architecture, and implement
in small, testable milestones.

## Mandatory working rules

1.  **Start by inspecting the environment and repository.** Determine
    Python version, operating system, installed SUMO version, CUDA
    availability, current files, and project status. Do not assume
    dependencies or APIs without checking.
2.  **Build a vertical slice first.** A user must be able to launch one
    virtual junction, see traffic move, run a controller, and collect
    metrics before advanced features are added.
3.  **Run the application and tests.** Do not claim something works
    merely because code was written. Run relevant commands, inspect
    logs, and fix issues.
4.  **Avoid fake functionality.** No buttons that do nothing, no
    fabricated data presented as live, no fake training curves, no
    hard-coded performance claims, and no placeholder screens presented
    as complete.
5.  **Never silently hide failures.** Show clear errors, diagnostics,
    and recovery instructions. Log full technical details while keeping
    user-facing messages understandable.
6.  **Do not over-engineer before the baseline works.** Prioritize
    end-to-end correctness, then polish and additional features.
7.  **Use current installed-library APIs.** Pin compatible dependencies
    after successful testing. Consult official documentation if API
    signatures differ.
8.  **All simulation is virtual.** No hardware, real-world camera,
    physical signal controller, or live-road integration is in scope.
9.  **Safety rules must not depend on the learned policy.** A
    deterministic safety manager must control legal phase transitions
    and clearance intervals.
10. **No unsupported claims.** Performance improvements must be
    calculated from recorded experiments using defined metrics and
    comparable conditions.
11. **Keep a project journal.** Maintain `docs/IMPLEMENTATION_LOG.md`
    with date, changes, commands run, test results, blockers, and next
    steps.
12. **If time is short, degrade gracefully.** Preserve a working
    simulator, baseline controller, metrics, and presentation before
    attempting optional complexity.

At the beginning, return a concise assessment of the repository and a
milestone plan. Then begin implementation rather than stopping after the
plan.

------------------------------------------------------------------------

# 1. Product vision

Build a polished research and operations platform called **AETHER
Traffic Intelligence** (working name; rename if the repository already
has a better established name). It demonstrates how computer vision and
reinforcement learning can improve traffic-signal decisions in a
controlled virtual environment.

It must include:

-   A microscopic traffic simulation of one four-way junction.
-   Configurable vehicle demand and traffic scenarios.
-   Multiple control strategies: fixed-time, vehicle-actuated,
    pressure-based heuristic, and learned DQN policy.
-   Virtual-camera perception using rendered simulation video and YOLO
    object detection.
-   Vehicle class detection, detection confidence, approximate lane
    assignment, traffic-density estimation, queue estimation, and
    tracking where feasible.
-   A deterministic safety layer that constrains all signal decisions.
-   A training pipeline and saved model artifacts.
-   Repeatable evaluation with CSV/JSON outputs and charts.
-   A premium dashboard that looks like a carefully maintained
    professional traffic operations platform.
-   A comprehensive README, research notes, architecture documentation,
    test suite, and reproducible demo.

The system is an academic simulation and decision-support demonstration,
not a certified real-world traffic controller. Clearly disclose this in
the interface and report.

## Product principle

**Trustworthy data and real functionality outrank visual spectacle.**
The UI should feel premium, but every displayed metric must have a clear
source, definition, and update path.

------------------------------------------------------------------------

# 2. Non-negotiable constraints

-   Deadline: 30 October 2026.
-   Windows 10/11.
-   16 GB system RAM.
-   NVIDIA GPU available; CUDA may or may not be configured correctly.
-   One intersection is the required scope.
-   Entirely virtual: SUMO-generated vehicles, rendered video, virtual
    traffic lights, synthetic demand.
-   The primary system must still work if GPU acceleration is
    unavailable; fall back to CPU for compatible tasks.
-   Avoid requiring cloud services, paid APIs, or credentials.
-   Prefer local-first execution and local artifact storage.
-   Use a supported Python version compatible with SUMO, PyTorch,
    Gymnasium, Stable-Baselines3, and the selected YOLO package.
-   Do not build a multi-intersection network until the one-intersection
    version is reliable.
-   No claim that the system is "real-time" unless measured and
    qualified.
-   No claim that YOLO output controls the signal unless the controller
    actually consumes YOLO-derived observations.

------------------------------------------------------------------------

# 3. Recommended technology stack

Use the following unless environment checks reveal a concrete
incompatibility:

## Simulation and control

-   Eclipse SUMO and SUMO-GUI for microscopic vehicle simulation.
-   TraCI for Python-to-SUMO interaction.
-   `sumolib` for network and lane metadata.
-   A generated, version-controlled, single four-way junction network
    with explicit traffic phases and route files.
-   A Python simulation runner that owns lifecycle, configuration,
    logging, and shutdown.

## Reinforcement learning

-   Gymnasium-compatible environment.
-   SUMO-RL if its installed API fits the chosen network and
    observation/action design; otherwise create a small custom Gymnasium
    environment over TraCI to avoid unnecessary abstraction.
-   Stable-Baselines3 DQN as the primary learned controller.
-   PyTorch backend.
-   Optional pressure-based policy inspired by max-pressure research as
    a baseline or fallback.

## Vision

-   Ultralytics YOLO small model for vehicle detection in rendered
    simulation video.
-   OpenCV for frame processing, overlays, video I/O, and calibration
    utilities.
-   Tracking: use a supported lightweight tracker if stable; otherwise
    implement simple IoU/centroid tracking with clear limitations.
-   Explicit class mapping for relevant vehicle classes: car,
    motorcycle, bus, truck, and other vehicle classes supported by the
    model.
-   Optional region-of-interest / polygon-based lane approach zones.

## Dashboard and charts

Preferred: **Streamlit + Plotly** for rapid delivery and rich
interactions. Use a clean multipage architecture and reusable
components. Do not mix simulation control logic directly into page
rendering code. - If a React-based frontend is already established in
the repository, retain it only if doing so does not threaten delivery;
do not rewrite the entire stack without a compelling reason. - Use
Plotly for interactive time series and comparisons. - Use a consistent
design system, typography, spacing, and component library. - Optional
FastAPI backend only if separation is needed and time permits. Do not
add a server just for architectural fashion.

## Data and quality

-   Python logging with rotating log files.
-   Pydantic or dataclasses for configuration and structured data
    contracts.
-   `pytest` for unit/integration tests.
-   Ruff for linting/format checks.
-   Pandas/NumPy for metrics.
-   Matplotlib or Plotly for publication-quality plots.
-   YAML or TOML configuration for scenarios and experiment definitions.
-   CSV for raw metric exports; JSON for metadata and run manifests.

## Windows compatibility

-   Use `pathlib` for paths.
-   Avoid shell-specific assumptions where possible.
-   Provide PowerShell commands in documentation.
-   Detect SUMO binaries and `SUMO_HOME`; show actionable setup
    diagnostics.
-   Do not assume CUDA is installed just because the machine has an
    NVIDIA GPU.

------------------------------------------------------------------------

# 4. System architecture

Keep modules separated by responsibility.

``` text
traffic-intelligence/
├── app.py                         # Dashboard entry point
├── pyproject.toml / requirements*.txt
├── README.md
├── .env.example
├── configs/
│   ├── app.yaml
│   ├── simulation.yaml
│   ├── perception.yaml
│   ├── rl.yaml
│   └── experiments.yaml
├── simulation/
│   ├── network/                   # Nodes, edges, connections, generated net
│   ├── routes/                    # Demand and route files
│   ├── scenario.sumocfg
│   └── README.md
├── src/traffic_ai/
│   ├── config/
│   ├── simulation/
│   │   ├── runner.py
│   │   ├── traci_client.py
│   │   ├── scenario_manager.py
│   │   └── lifecycle.py
│   ├── control/
│   │   ├── interfaces.py
│   │   ├── fixed_time.py
│   │   ├── actuated.py
│   │   ├── max_pressure.py
│   │   ├── dqn_policy.py
│   │   ├── safety_manager.py
│   │   └── phase_catalog.py
│   ├── perception/
│   │   ├── detector.py
│   │   ├── tracker.py
│   │   ├── lane_mapper.py
│   │   ├── density_estimator.py
│   │   ├── camera_calibration.py
│   │   └── video_pipeline.py
│   ├── state/
│   │   ├── schemas.py
│   │   ├── ground_truth.py
│   │   └── fusion.py
│   ├── metrics/
│   │   ├── definitions.py
│   │   ├── collector.py
│   │   ├── evaluator.py
│   │   └── reports.py
│   ├── training/
│   │   ├── environment.py
│   │   ├── train_dqn.py
│   │   ├── evaluate_policy.py
│   │   └── callbacks.py
│   ├── experiments/
│   │   ├── runner.py
│   │   └── manifest.py
│   ├── dashboard/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── theme.py
│   │   └── data_access.py
│   └── utils/
│       ├── logging.py
│       ├── paths.py
│       └── diagnostics.py
├── scripts/
│   ├── check_environment.py
│   ├── generate_scenario.py
│   ├── run_simulation.py
│   ├── train_agent.py
│   ├── evaluate_agent.py
│   └── make_demo_video.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── smoke/
├── artifacts/
│   ├── models/
│   ├── videos/
│   └── reports/
├── data/
│   ├── runs/
│   └── processed/
└── docs/
    ├── ARCHITECTURE.md
    ├── METHODOLOGY.md
    ├── RESEARCH_NOTES.md
    ├── METRICS.md
    ├── SAFETY.md
    ├── USER_GUIDE.md
    ├── IMPLEMENTATION_LOG.md
    └── LIMITATIONS.md
```

Do not create every file as an empty placeholder. Add modules as they
become necessary and ensure imports work. The final repository may
simplify this tree if the structure remains clear.

## Main data flow

1.  Scenario manager loads the selected virtual road network and demand
    configuration.
2.  SUMO runs one simulation step or a controlled batch of steps.
3.  Ground-truth adapter reads vehicle/lane/signal state for reference,
    metrics, and optional training.
4.  Camera pipeline reads rendered video frames, detects vehicles,
    optionally tracks detections, and estimates lane-level traffic
    features.
5.  Observation builder creates a normalized state vector from the
    selected observation source.
6.  The controller proposes an action.
7.  Safety manager validates the action and handles phase
    transitions/clearance.
8.  Simulation advances.
9.  Metrics collector records results and writes a run manifest.
10. Dashboard reads structured run state and artifacts, not ad-hoc
    globals.

Provide explicit modes: - `ground_truth`: ideal simulator state; used
for debugging, baseline RL training, and reference evaluation. -
`vision`: perception-derived observations; used for camera pipeline
demonstration and, only when integrated, closed-loop control. -
`hybrid`: vision-derived state with simulator ground truth used for
comparison and debugging, never silently substituted without indicating
that substitution.

The UI must always disclose which observation mode is active.

------------------------------------------------------------------------

# 5. Simulation specification

## Intersection

Build one clear four-way junction with: - North, south, east, west
approaches. - At least one incoming and one outgoing lane per approach;
preferably two incoming lanes if network generation is reliable. -
Explicitly defined signal phases and signal-group mapping. - Lane IDs,
stop-line locations, route definitions, and detector regions stored in a
configuration or generated metadata file. - Pedestrian phases are
optional and must not be faked; add them only if fully modeled and
tested. - Turn movements should include left/straight/right where
supported by the chosen lane geometry. - Vehicle classes and speed
distributions should be configurable.

Prefer a deliberately designed single-junction network over a generated
grid containing multiple uncontrolled signals. Make the controlled
junction ID explicit and validate it at startup.

## Demand scenarios

Implement reproducible demand profiles: 1. Low / off-peak. 2. Balanced
moderate demand. 3. Heavy / peak demand. 4. North-south dominant. 5.
East-west dominant. 6. Bursty arrivals. 7. Unseen evaluation profile
with different seed and demand proportions.

Each scenario must specify: - Random seed. - Vehicle arrival rates or
route-generation parameters. - Turning ratios. - Simulation duration. -
Warm-up interval. - Step length. - Scenario name and version. - Optional
vehicle class mix.

Use identical scenario configuration and seeds when comparing
controllers. Use separate seeds for evaluation and training.

## Simulation performance

-   Default step length: 1 simulated second unless a reasoned
    alternative is documented.
-   Allow simulation speed control for the GUI, while maintaining
    correct simulated time.
-   Support headless runs for experiments.
-   Support graceful stop and cleanup even if the UI session ends.
-   Never leave SUMO processes orphaned.
-   Log simulation startup arguments, version, seed, and duration.

------------------------------------------------------------------------

# 6. Signal-control design and safety

## Phase catalog

Create an explicit phase catalog based on the generated SUMO network's
actual controlled links. Do not assume a particular signal-string order
without inspecting `getControlledLinks()` and the generated phase
program.

A common conceptual plan is: - Phase A: compatible north-south
movements. - Yellow transition from A. - Optional all-red clearance if
required by the network/safety design. - Phase B: compatible east-west
movements. - Yellow transition from B. - Optional all-red clearance. -
Return to A.

If turning movements require protected arrows or separate phases, model
them explicitly. Do not allow conflicting greens.

## Deterministic safety manager

The learned policy must never directly write arbitrary red/yellow/green
strings. It proposes a target phase or action; the safety manager: -
Rejects illegal phase requests. - Enforces minimum green duration. -
Enforces maximum green duration to prevent starvation. - Enforces yellow
transition duration. - Enforces any configured all-red clearance. -
Prevents incompatible green groups from being active together. -
Enforces legal transitions from the current phase to the target phase. -
Handles shutdown and simulation reset safely. - Records every
accepted/rejected action with a reason. - Has a safe, deterministic
fallback if the agent errors or outputs an invalid action.

All durations must be configurable and explicitly labeled as simulation
assumptions, not certified traffic engineering recommendations.

## Controller interface

Create one consistent interface, e.g.: - `reset(context)` -
`observe(context) -> Observation` -
`propose_action(observation) -> Action` -
`apply_action(action, safety_manager) -> AppliedAction` -
`on_step(metrics)` - `close()`

Controllers: 1. Fixed-time: fixed cycle and green splits. 2.
Vehicle-actuated: extend/terminate green based on demand and configured
gap/max-green limits. 3. Pressure-based: choose the phase with the
strongest queue/flow pressure using a documented formula. 4. DQN: select
among safe abstract actions such as keep current green or request a
compatible alternate phase at decision epochs.

Every controller must use the same network, scenario, step length,
warm-up, and evaluation definitions.

------------------------------------------------------------------------

# 7. Reinforcement-learning specification

## Algorithm

Use DQN as the first learned controller because the single-junction
action space can be kept discrete. Do not implement PPO, multi-agent RL,
graph neural networks, or custom neural architectures unless the basic
DQN controller is already reliable and time remains.

## Observation vector

For each incoming approach or lane group, include normalized values such
as: - Vehicle count. - Queue length or queue vehicle count. - Mean
speed. - Waiting time / accumulated waiting estimate. - Occupancy or
density proxy. - Current green phase (one-hot). - Time elapsed in
current phase. - Time since last switch. - Optional incoming/outgoing
pressure feature.

Clip or normalize features consistently. Record the observation schema
and version it. Ensure the same order and scaling are used during
training and inference.

For vision mode, the lane-level features must be computed from YOLO
detections/tracks and calibrated lane regions. Do not pass ground-truth
values into a vision-mode policy while labeling it camera-driven.

## Action space

Keep a discrete and interpretable action space. Suggested actions at a
decision epoch: - Hold current green for another decision interval. -
Request the next compatible phase. - Request another explicitly
permitted compatible phase, if phase design allows it.

The safety manager decides whether and when to execute a requested phase
transition. A policy action must not bypass yellow or clearance.

## Reward

Use a documented reward based primarily on changes in total
queue/waiting, with a modest penalty for excessive switching. Example
conceptual form:

`reward_t = wq * (Q_previous - Q_current) + ww * (W_previous - W_current) + wt * throughput_delta - ws * switch_penalty`

Where: - `Q` is total queue burden. - `W` is aggregate waiting burden. -
`throughput_delta` is a measured change in vehicles served. -
`switch_penalty` discourages rapid phase oscillation. - weights are
configured, normalized where appropriate, and justified.

Avoid rewarding only the currently green approach. The agent must not
improve one direction by starving another. Consider fairness/starvation
penalties and maximum green limits. Record individual reward components
for debugging.

## Training requirements

-   Seed Python, NumPy, and the RL framework where supported.
-   Save model checkpoint, hyperparameters, observation/action schema,
    training curves, environment config, and package versions.
-   Use a bounded replay buffer appropriate for 16 GB RAM.
-   Start with a modest number of timesteps (e.g. 10,000--30,000 as a
    smoke experiment), then extend only if learning evidence warrants
    it.
-   Use evaluation callbacks on fixed validation seeds.
-   Keep the best validated checkpoint, not merely the final checkpoint.
-   Make training interruptible and resumable where feasible.
-   Write a clear status/progress file so the dashboard can show actual
    training state.
-   Do not fabricate a converged model or training history.
-   Check whether GPU use helps; small DQN MLPs may be faster on CPU due
    to simulation overhead. Use `device="auto"` or a measured choice.

## Validation

-   Compare random or untrained policy, fixed-time, actuated,
    pressure-based, and trained DQN.
-   Plot reward and traffic metrics.
-   Evaluate on unseen demand seeds.
-   Do not assert that DQN wins unless the measured results support it.
-   If DQN does not outperform a baseline by the deadline, report the
    result honestly and discuss likely causes.

------------------------------------------------------------------------

# 8. Virtual-camera perception specification

## Purpose

Demonstrate an AI perception pipeline from simulated camera video to
traffic features. A virtual camera is a rendered view of the SUMO
environment or a reproducible recorded clip; no physical camera is
involved.

## Pipeline

1.  Render or record the SUMO GUI / simulation scene at a known camera
    viewpoint.
2.  Process frames with a YOLO model.
3.  Filter to vehicle classes relevant to traffic control.
4.  Track detections across frames if possible to avoid counting one
    moving vehicle repeatedly.
5.  Apply approach/lane region polygons or a calibrated mapping.
6.  Estimate per-approach vehicle count, class distribution, occupancy,
    approximate queue length, and speed proxy if tracking supports it.
7.  Smooth noisy estimates over a short configurable window.
8.  Publish observation data with timestamp, source mode, confidence,
    and freshness.
9.  Compare against SUMO ground truth at synchronized timestamps.

## Important limitations

-   A GUI screen recording is a visualization feed, not a calibrated
    road camera by default.
-   A top-down or fixed oblique virtual camera is preferable to a moving
    cinematic view.
-   Lane assignment needs geometry/calibration and must not be inferred
    solely from detection class.
-   Standard pretrained YOLO classes may not distinguish all local
    vehicle types.
-   Queue length from image detections is approximate unless calibrated.
-   Detection outputs must include confidence and a way to indicate
    stale/invalid observations.
-   Occlusion and vehicles hidden by perspective must be documented.

## Closed-loop integration rule

A true vision-driven experiment must: - Use only perception-derived
features for the policy observation, apart from explicitly allowed
non-perception fields such as current signal phase and simulation
time. - Log the vision estimate and ground truth separately. - Never
replace failed vision estimates with ground truth without marking the
run as hybrid/fallback. - Include a comparison between `ground_truth`
and `vision` observation modes where practical.

## Detection evaluation

At sampled timestamps compare: - Vehicle count error by approach. -
Precision/recall if bounding-box ground truth is available. - Mean
absolute count error. - Detection confidence distribution. - Runtime per
frame / approximate FPS. - Tracking ID switches if a tracker is used.

Do not report detection accuracy percentages without a defined
ground-truth annotation/evaluation procedure.

------------------------------------------------------------------------

# 9. Metrics and experiment protocol

## Primary metrics

1.  Mean travel time for completed trips.
2.  Mean delay or time loss, with exact definition documented.
3.  Throughput: completed vehicles per simulation interval.
4.  Average queue length by approach and overall.
5.  Maximum queue length.
6.  Total waiting time or average waiting time, clearly distinguished.
7.  Stops per vehicle where available.
8.  Emissions, only if correctly configured and supported by SUMO.
9.  Starvation/fairness: maximum wait and distribution of waits by
    approach.
10. Controller switching frequency.
11. Simulation wall-clock runtime and training runtime.

Avoid confusing instantaneous active-vehicle waiting time with
trip-level travel delay. Define each metric in `docs/METRICS.md`.

## Experimental protocol

-   Use a warm-up period and exclude it from scored metrics.
-   Use at least 5 seeds if compute/time allows; otherwise report the
    exact number and explain the limitation.
-   Run all controllers on the same demand scenarios and seed set.
-   Keep training seeds separate from final test seeds.
-   Include at least low, moderate, heavy, and directional-imbalance
    demand.
-   Save per-run raw results and aggregated mean/std.
-   Include confidence intervals or uncertainty bands where practical.
-   Plot each controller on the same axes and use consistent units.
-   Do not cherry-pick the best run.
-   Include failures and scenario limitations in the report.

## Improvement calculation

For metrics where lower is better:

`improvement_percent = 100 * (baseline_value - proposed_value) / baseline_value`

For metrics where higher is better, define a corresponding formula.
Protect against division by zero and explain how runs with zero
completed vehicles are handled.

## Run manifest

Every run must save a JSON manifest containing: - Unique run ID. -
Timestamp. - Controller name and version. - Model checkpoint hash/path
if applicable. - Observation mode. - Scenario name/version. - Seed. -
Simulation step length and duration. - Demand parameters. - Package
versions. - SUMO version. - Git commit if available. - Metric
definitions/version. - Output file paths. - Exit status and errors, if
any.

------------------------------------------------------------------------

# 10. Premium dashboard design specification

## Overall design goal

The dashboard must look like a mature professional
intelligent-transportation operations and research product---not a
default Streamlit demo, hackathon template, or generic admin panel. It
should feel intentionally designed, maintained, information-dense
without clutter, and visually consistent.

Use a restrained **dark operations-console theme**: - Deep graphite/navy
background. - Slightly lighter panels with subtle borders. -
High-contrast white/off-white typography. - Muted slate secondary
text. - One restrained cyan/teal accent for active/interactive
elements. - Green only for verified healthy/normal states. - Amber for
warnings and degraded data. - Red for errors, safety violations, or
critical conditions. - Avoid excessive gradients, neon glows,
glassmorphism, oversized empty cards, random emojis, and decorative
animations. - Use consistent spacing, grid, border radius, iconography,
and number formatting. - Use a professional sans-serif typeface such as
Inter or an available equivalent. - Prefer line icons (Lucide or
similar) and consistent icon size. - Make every page work at common
laptop screen sizes; no clipped controls or horizontal overflow.

The design must be attractive in both a live demo and screenshots for an
academic presentation. Include a light theme only if it can be done
consistently without delaying core functionality.

## Visual identity

Working product name: **AETHER \| Traffic Intelligence** Tagline:
**Simulation, perception, and adaptive control.** Provide a compact
wordmark/brand treatment, not a giant hero banner. Display a persistent
`SIMULATION ONLY` indicator and the active observation mode. Use a clear
environment badge such as `SUMO · LOCAL SIMULATION`. Do not use fake
city names, fake agency logos, or real-world live traffic data.

## Global layout

-   Slim left sidebar with product identity, navigation, current
    run/session, and system status.
-   Main content area with a compact top bar.
-   Top bar includes current scenario, controller, simulation state,
    observation mode, and a visible start/pause/stop/reset control where
    safe.
-   Main content should prioritize the intersection view and the most
    important traffic KPIs.
-   A collapsible right-side inspector or contextual panel may show
    selected lane, selected vehicle, model details, or event details.
-   Persistent toast/alert region for actionable feedback.
-   Consistent page titles, subtitles, and breadcrumbs where useful.
-   No navigation item may lead to an empty page. Hide unfinished items
    or mark them transparently as planned.

## Information architecture / pages

### 1. Operations Overview

Purpose: understand the current simulation and controller at a glance.
Include: - Large central intersection visualization or embedded SUMO
GUI/video feed. - Current signal phase and phase elapsed timer. - Four
approach summaries (N/S/E/W) with queue estimate, vehicle count, mean
speed, wait estimate, and demand indicator. - Core KPI strip: mean
delay, throughput, total queue, active vehicles, controller mode. - Live
time-series charts for queues, delay, throughput, and signal phase
history. - Current AI action and short explanation of the action's input
factors, without claiming the neural network is explainable if it is
not. - Recent event timeline: phase change, demand surge, detector
degradation, training complete, simulation started/stopped. - Clear run
state: Idle, Starting, Running, Paused, Stopping, Completed, Failed. - A
visual indicator when values are simulator ground truth vs
camera-estimated. - Start, pause, stop, reset, and scenario controls
that actually work. - If live SUMO embedding is impractical, show a
synchronized rendered video or clean schematic that updates from actual
state. Do not fake live video.

### 2. Live Intersection

-   Top-down schematic of the four-way junction.
-   Vehicle glyphs positioned from actual SUMO coordinates where
    possible; alternatively use a video panel.
-   Signal heads/phase status and approach labels.
-   Selectable approaches and lanes.
-   Per-lane count, occupancy proxy, queue estimate, speed, and wait.
-   Toggle overlays: detections, track IDs, lane regions, queue region,
    confidence, ground-truth positions.
-   Side-by-side perception vs ground truth view when available.
-   Simulation time and playback speed controls.
-   Camera view selector only if multiple real virtual camera
    configurations exist.

### 3. AI Controller

-   Active controller selector: Fixed-time, Actuated, Pressure-based,
    DQN.
-   Current observation mode: Ground Truth, Vision, Hybrid.
-   Current state vector displayed in a readable, expandable inspector.
-   Action proposal, accepted/rejected result, and safety-manager
    reason.
-   Reward component breakdown during training/evaluation.
-   Phase timeline and green duration history.
-   Controller parameters in validated configuration forms.
-   Model metadata: architecture, trained timestamp, checkpoint path,
    training steps, evaluation score.
-   Safe fallback status and errors.
-   Explainability should be framed as input/decision diagnostics, not a
    false claim that DQN is inherently interpretable.

### 4. Camera & Perception

-   Video preview with annotated detections.
-   Vehicle-class filters.
-   Detection confidence threshold control.
-   Inference FPS / frame latency.
-   Count by vehicle class and approach.
-   Tracking IDs if implemented.
-   Lane-region polygons and calibration status.
-   Detection freshness and pipeline health.
-   Count estimate vs simulator ground truth chart.
-   Mean absolute count error over time.
-   Clear warnings if lane mapping is not calibrated.
-   Button to select/import a locally recorded virtual-camera clip.
-   Display model name and model source.
-   No claims of precision/recall unless evaluated against labeled
    ground truth.

### 5. Scenario Lab

-   Scenario cards for Low, Balanced, Heavy, NS-dominant, EW-dominant,
    Bursty, Custom.
-   Traffic demand sliders/inputs with sensible ranges.
-   Turning ratios that validate to 100% or are normalized with explicit
    feedback.
-   Vehicle class mix and simulation duration.
-   Random seed control.
-   Warm-up duration and step length.
-   Create/duplicate/save scenario configurations.
-   Scenario configuration preview.
-   Validation errors before launch.
-   Show scenario ID/version and generated artifact paths.

### 6. Training Center

-   Start/stop training with clear resource expectations.
-   Training progress based on actual callback/status data.
-   Timesteps completed / target.
-   Episode reward and evaluation metrics.
-   Rolling reward plot, loss plot if genuinely available, and
    evaluation results.
-   Current model/checkpoint and best validated checkpoint.
-   Hyperparameter editor with validation.
-   CPU/GPU device status and memory info only when actually obtainable.
-   Training logs and recent warnings.
-   Resume/reload support only if implemented and tested.
-   Do not show fabricated loss, progress, or GPU telemetry.

### 7. Experiments & Benchmarking

-   Select scenarios, controllers, seeds, and metrics.
-   Launch reproducible batch experiment.
-   Queue and status for runs if background execution is implemented.
-   Results table with run ID, controller, scenario, seed, status,
    metrics.
-   Comparison charts with confidence intervals/variability where
    available.
-   Baseline-normalized improvement.
-   Filter by scenario/controller/seed.
-   Export CSV and JSON.
-   Export a research summary report.
-   Clearly mark incomplete/failed runs.
-   Never compare runs with incompatible metric definitions without a
    warning.

### 8. Analytics & Reports

-   KPI cards with metric definitions available by tooltip or info
    panel.
-   Time-series trends and controller comparisons.
-   Per-approach fairness and starvation analysis.
-   Travel-time distributions and queue distributions.
-   Emissions only if supported and configured.
-   Export publication-quality plots.
-   Download report containing configuration, metrics, seed count,
    uncertainty, and limitations.
-   Separate observed data from derived estimates.

### 9. Model Registry

-   List model checkpoints, algorithm, version, date, training scenario,
    steps, evaluation score, and artifact size.
-   Mark best validated model based on a defined evaluation metric.
-   Load model only after compatibility checks.
-   Compare model metadata.
-   Avoid overwriting existing checkpoints silently.
-   Show observation schema version and reject incompatible models.

### 10. System Health / Settings

-   SUMO path/version and connection state.
-   Python/package versions.
-   CUDA/PyTorch device check.
-   Writable paths and disk usage where possible.
-   Log viewer with level filter.
-   Configuration viewer/editor with validation.
-   Theme and display preferences.
-   Data retention / clear generated data controls with confirmation.
-   Diagnostics bundle export.
-   Helpful setup wizard if dependencies are missing.

### 11. Documentation / About

-   Architecture overview.
-   How to run the simulation.
-   Controller descriptions.
-   Metric definitions.
-   Research references.
-   Assumptions and limitations.
-   Project version, commit, dependency versions.
-   Persistent disclaimer: virtual research demonstration, not certified
    for real-world control.

## Dashboard interaction quality

-   All controls must have meaningful state transitions.
-   Show loading, empty, error, disabled, and success states.
-   Confirm destructive actions such as deleting data or stopping
    training.
-   Prevent duplicate launches.
-   Disable controls that are invalid during a run.
-   Show progress for long-running tasks and allow cancellation when
    safe.
-   Preserve filter/configuration state where appropriate.
-   Use tooltips for technical terminology.
-   Provide keyboard-accessible controls and readable contrast.
-   Ensure charts have axis labels, units, legends, and informative
    hover data.
-   Use consistent date/time formatting and units.
-   No tiny illegible text for critical information.
-   Avoid chartjunk and excessive KPI cards.
-   Keep important information visible without requiring many scrolls.
-   Do not use animations that reduce readability or consume excessive
    resources.

## Dashboard quality gates

-   A new user can start a scenario and identify the active controller
    within 30 seconds.
-   A user can see why a signal changed, what observation mode was used,
    and which metrics changed.
-   No live value is hard-coded.
-   No visible button is inert.
-   No page has placeholder text or empty charts presented as real data.
-   All errors have actionable messages.
-   At 1366x768 and 1920x1080, layout remains usable.

------------------------------------------------------------------------

# 11. Event logging and observability

Log structured events: - Simulation start/stop/reset. - Scenario loaded
and seed selected. - Controller switched. - Observation mode changed. -
Phase requested, accepted, rejected, and applied. - Safety constraint
triggered. - Detector or tracker error. - Observation stale/invalid. -
Training start/stop/checkpoint. - Evaluation start/complete/fail. -
Export/report generation. - Any unexpected exception.

Every event should include timestamp, run ID, severity, subsystem, and
structured details. Provide human-readable messages in the dashboard and
detailed logs in files.

Do not log secrets; this project should not require secrets.

------------------------------------------------------------------------

# 12. Error handling and recovery

Handle these cases deliberately: - SUMO is not installed or its
executable is not on PATH. - `SUMO_HOME` is missing or incorrect. -
Generated network has no traffic light or the expected TLS ID is
missing. - Route generation produces no vehicles. - SUMO process exits
unexpectedly. - TraCI disconnects. - Model checkpoint is missing or
incompatible. - CUDA is unavailable. - YOLO weights cannot be downloaded
or loaded. - Video codec/file is unsupported. - Camera estimate is stale
or invalid. - Dashboard is refreshed while a run is active. - Training
is interrupted. - Output directory is read-only. - A run produces zero
completed trips. - A controller proposes an illegal phase. - A metric
denominator is zero.

Each error should have: 1. A user-friendly message. 2. A technical log
entry. 3. A recovery action or explanation. 4. A safe shutdown behavior
if the simulator is running.

------------------------------------------------------------------------

# 13. Testing requirements

## Unit tests

-   Observation normalization and shape.
-   Reward components.
-   Metric formulas and zero-denominator handling.
-   Scenario configuration validation.
-   Phase transition table.
-   Minimum/maximum green rules.
-   Yellow/all-red clearance logic.
-   Conflict prevention.
-   Detection-to-lane assignment.
-   Track de-duplication.
-   Run-manifest serialization.

## Integration tests

-   Start SUMO headless and close cleanly.
-   Generate a scenario with deterministic seed.
-   Run each baseline controller.
-   Produce a valid results manifest and CSV.
-   Load a saved model and run evaluation.
-   Run detector on a short test clip if available.
-   Dashboard reads completed run artifacts.
-   Export CSV/JSON/report successfully.

## Smoke tests

Create one command that checks environment prerequisites and runs a
short simulation, e.g. 60--120 simulated seconds. It should exit nonzero
on failure and print clear diagnostics.

## Safety tests

-   The safety manager never permits conflicting greens.
-   A requested switch during minimum green is delayed/rejected.
-   Yellow transition occurs before the next conflicting green.
-   A controller exception triggers a safe fallback.
-   Repeated action requests cannot skip clearance phases.
-   Simulation reset restores a known legal phase.

------------------------------------------------------------------------

# 14. Documentation deliverables

Create and maintain: - `README.md`: quickstart, prerequisites, commands,
screenshots, feature list, limitations. - `docs/ARCHITECTURE.md`:
modules, data flow, lifecycle, component diagram. -
`docs/METHODOLOGY.md`: simulation, state, action, reward, algorithms,
training procedure. - `docs/RESEARCH_NOTES.md`: literature review with
correct citations and relevance to implementation. - `docs/METRICS.md`:
definitions, formulas, units, aggregation, caveats. - `docs/SAFETY.md`:
phase model, safety manager, transition table, test coverage. -
`docs/USER_GUIDE.md`: walkthrough of each page and scenario launch. -
`docs/LIMITATIONS.md`: simulated environment, camera limitations,
uncertainty, lack of real-world certification. -
`docs/IMPLEMENTATION_LOG.md`: work log and actual test evidence. -
`docs/EXPERIMENT_PROTOCOL.md`: seeds, scenarios, controllers,
aggregation and reporting. - `requirements` or lock file with tested
versions. - `.env.example` only if configuration environment variables
are genuinely used. - A small sample result set or demo data clearly
labeled as sample, never as actual AI performance.

All docs must reflect the code that exists. Do not document
unimplemented features as completed.

------------------------------------------------------------------------

# 15. Research foundation and references

Use official docs and papers as primary sources. Verify each citation,
title, author list, publication venue, year, and URL. Do not invent
bibliographic details.

## Core technical documentation

1.  SUMO documentation: https://eclipse.dev/sumo/docs/
2.  SUMO traffic lights:
    https://eclipse.dev/sumo/docs/Simulation/Traffic_Lights.html
3.  TraCI documentation: https://eclipse.dev/sumo/docs/TraCI/
4.  SUMO TraCI traffic-light tutorial:
    https://eclipse.dev/sumo/docs/Tutorials/TraCI4Traffic_Lights.html
5.  SUMO-RL repository: https://github.com/LucasAlegre/sumo-rl
6.  Stable-Baselines3 DQN docs:
    https://stable-baselines3.readthedocs.io/en/master/modules/dqn.html
7.  Ultralytics prediction docs:
    https://docs.ultralytics.com/modes/predict/

## Research reference

**PressLight: Learning Max Pressure Control to Coordinate Traffic
Signals in Arterial Network** (KDD 2019). Repository:
https://github.com/wingsweihua/presslight

Use the paper to discuss the relationship between traffic pressure and
RL reward design. Do not claim to reproduce PressLight unless the
implementation follows the paper sufficiently and the report explicitly
describes differences.

## Literature review themes

-   Fixed-time and actuated control.
-   Max-pressure traffic signal control.
-   Deep reinforcement learning for traffic signal control.
-   Observation and reward design.
-   Simulator-to-real-world limitations and partial observability.
-   Computer-vision vehicle detection and tracking.
-   Fairness and starvation across approaches.
-   Evaluation reproducibility and seed variance.

The literature review must distinguish peer-reviewed research from
software documentation and repositories. Summarize methods and
limitations in your own words, and cite sources near relevant claims.

------------------------------------------------------------------------

# 16. Acceptance criteria / definition of done

The project is complete only when the following required criteria are
met or explicitly reported as incomplete.

## P0 --- Required end-to-end functionality

-   [ ] Runs on the target Windows machine using documented setup steps.
-   [ ] One controlled four-way SUMO intersection with reproducible
    demand.
-   [ ] Traffic can be started, paused/stopped, and reset cleanly.
-   [ ] At least fixed-time and one adaptive controller work.
-   [ ] Deterministic safety manager handles legal phase transitions.
-   [ ] Results are saved to CSV plus a run manifest.
-   [ ] Dashboard displays real state and real metrics.
-   [ ] A short smoke test runs without manual code edits after setup.
-   [ ] Errors and shutdown are handled gracefully.

## P1 --- Core AI research deliverable

-   [ ] DQN training can run and saves a checkpoint.
-   [ ] Saved model can be reloaded for evaluation.
-   [ ] Training/evaluation seeds are separated.
-   [ ] At least fixed-time, actuated or pressure-based, and DQN are
    compared.
-   [ ] Metrics include travel time/delay, queue, throughput, and
    fairness/starvation.
-   [ ] No unsupported performance claims.
-   [ ] Experiment configuration and dependencies are recorded.

## P1 --- Camera demonstration

-   [ ] A virtual-camera clip is available from the simulation.
-   [ ] YOLO detects vehicles in the clip.
-   [ ] Annotated output is saved.
-   [ ] Per-approach count estimation exists or its missing calibration
    is explicitly stated.
-   [ ] Detection estimates are compared with SUMO ground truth.
-   [ ] UI clearly distinguishes ground truth, vision, and hybrid modes.

## P1 --- Premium dashboard

-   [ ] Every implemented page is functional.
-   [ ] No inert buttons, fake charts, fake metrics, or placeholder
    pages.
-   [ ] Operations overview includes intersection, signal phase,
    approaches, and core KPIs.
-   [ ] Camera/perception page shows detections and pipeline status.
-   [ ] AI controller page shows controller state, actions, and
    safety-manager decisions.
-   [ ] Scenario lab allows repeatable demand configuration.
-   [ ] Experiments page compares real runs.
-   [ ] Reports can be exported.
-   [ ] UI is usable at 1366x768 and 1920x1080.
-   [ ] Simulation-only disclaimer is visible.

## P2 --- Stretch features only after P0/P1

-   [ ] Rich video overlays and vehicle tracking.
-   [ ] Interactive report generation.
-   [ ] Model registry and checkpoint comparisons.
-   [ ] Training resume and experiment queue.
-   [ ] Emission analysis.
-   [ ] Custom scenario editor.
-   [ ] Light theme.
-   [ ] More advanced RL algorithm or multi-intersection extension.

------------------------------------------------------------------------

# 17. Timeline and prioritization

Assume work must be submitted by 30 October 2026. Freeze new features by
29 October.

## Phase 1: Environment and vertical slice

-   Inspect Python, SUMO, CUDA, repository.
-   Install/configure missing dependencies.
-   Create one explicit four-way network and route scenarios.
-   Run SUMO headless and GUI.
-   Produce first results CSV.
-   Build a simple but real dashboard shell.

## Phase 2: Controller and safety

-   Implement fixed-time baseline.
-   Implement deterministic phase state machine.
-   Implement vehicle-actuated controller.
-   Implement pressure-based controller if time permits.
-   Add safety tests and structured logs.

## Phase 3: Reinforcement learning

-   Build/validate Gymnasium environment.
-   Define observations, actions, rewards.
-   Run short DQN smoke training.
-   Save/reload checkpoint.
-   Evaluate on fixed validation seeds.

## Phase 4: Camera perception

-   Render or record a stable virtual camera view.
-   Run YOLO detection.
-   Implement lane-region mapping and optional tracking.
-   Compare estimated counts with ground truth.
-   Connect vision estimates to controller only if the integration is
    stable and testable.

## Phase 5: Dashboard and experiments

-   Polish operations overview.
-   Add controller, camera, scenario, training, experiments, analytics,
    and system-health pages as functionality permits.
-   Implement run manifests and experiment exports.
-   Run repeated controller comparisons and generate charts.

## Phase 6: Stabilization and submission

-   Stop adding major features.
-   Run smoke tests from a clean terminal.
-   Run final evaluation seeds.
-   Save model and logs.
-   Verify all documentation commands.
-   Capture demo video and screenshots.
-   Prepare final research report and limitations.

## Prioritization rule

If any phase overruns, do not sacrifice P0 stability to achieve a
stretch feature. The minimum acceptable final product is a working
virtual junction, safe adaptive controller, reproducible baseline
comparison, real metrics, and a polished dashboard.

------------------------------------------------------------------------

# 18. Final report structure

Generate a report with these sections: 1. Abstract. 2. Problem statement
and objectives. 3. Scope and simulation-only constraints. 4. Related
work. 5. System architecture. 6. Virtual road network and demand
generation. 7. Camera perception and state estimation. 8. Controller
designs. 9. RL formulation: state, action, reward, algorithm,
hyperparameters. 10. Safety manager. 11. Experiment protocol and metric
definitions. 12. Results and charts. 13. Error analysis and ablation
study. 14. Limitations and validity threats. 15. Conclusion and future
work. 16. References. 17. Reproducibility appendix with commands,
versions, seeds, and artifact locations.

Report actual results only. If results are mixed or the learned agent
does not outperform a baseline, state that honestly and analyze why.

------------------------------------------------------------------------

# 19. Final instruction to the coding agent

Implement this project in the current workspace. First inspect the
existing files and environment. Then build and verify the smallest
end-to-end version. Keep the architecture modular, UI polished, and the
data honest.

At the end of each milestone: 1. Summarize files changed. 2. List
commands executed. 3. Report tests that passed and failed. 4. Show any
remaining blockers. 5. State the next highest-priority task.

Do not stop at writing plans or documentation. Make actual code changes,
run the software, inspect its behavior, and iteratively improve it. Do
not claim completion for untested components.

**The final deliverable must be a runnable, visually polished,
research-backed simulation platform---not a mockup, not a notebook-only
prototype, and not a collection of disconnected scripts.**
