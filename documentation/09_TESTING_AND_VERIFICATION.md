# Module 09: Testing & Verification Suite

## 1. Quality Assurance Philosophy
In accordance with Mandatory Working Rule 3 and Section 13 of the Master Engineering Specification:
> *"Run the application and tests. Do not claim something works merely because code was written. Run relevant commands, inspect logs, and fix issues."*

Adaptive Traffic Control System maintains a comprehensive, automated test suite built with **Pytest 9.1.1** partitioned across unit, integration, and smoke test layers.

---

## 2. Test Suite Breakdown (15 Tests Total)

### 2.1 Safety Manager Unit Tests (`tests/unit/test_safety_manager.py`)
Verifies deterministic signal safety invariants:
1. `test_safety_manager_initialization`: Verifies initial state starts in Phase 0 Green with legal signal string and no transitions in progress.
2. `test_safety_manager_min_green_rejection`: Verifies that requests to switch prior to 10 seconds of green are strictly rejected with reason `MIN_GREEN_NOT_REACHED`.
3. `test_safety_manager_legal_transition_sequence`: Steps the safety manager through Yellow (3.0s), All-Red (2.0s), and verifies target green phase is committed accurately without skipping clearance intervals.
4. `test_safety_manager_max_green_enforcement`: Advances the clock past 60.0s and verifies that the safety manager forces a transition to the next phase with reason `MAX_GREEN_ENFORCED`.
5. `test_safety_manager_rejects_requests_during_clearance`: Verifies that any phase request received while in yellow or all-red clearance is safely ignored with reason `TRANSITION_IN_PROGRESS`.

### 2.2 Gymnasium Environment Unit Tests (`tests/unit/test_environment.py`)
Validates reinforcement learning environment contracts:
6. `test_env_observation_and_action_spaces`: Verifies `action_space` is `Discrete(4)`, `observation_space` is `Box(0.0, 1.0, (25,), float32)`.
7. `test_env_reset_and_step`: Verifies `env.reset()` returns valid normalized observation vector within $[0.0, 1.0]$, and `env.step(action)` advances simulation and returns correct types for `(obs, reward, terminated, truncated, info)`.

### 2.3 Perception Pipeline Unit Tests (`tests/unit/test_perception.py`)
Validates computer vision calibration, tracking, and error estimation:
8. `test_camera_calibration_coordinate_mapping`: Verifies world coordinate $(250, 250)$m maps to pixel $(400, 400)$px, and checks inverse mapping accuracy.
9. `test_camera_approach_roi_assignment`: Tests point-in-polygon assignment for North, South, East, and West approach zones.
10. `test_vehicle_tracker_lifecycle`: Tests track creation, spatial IoU association across consecutive frames, and track expiration after $\text{max\_age} = 2$.
11. `test_density_estimator_mae`: Verifies calculation of Mean Absolute Error (MAE) against known ground-truth approach counts.

### 2.4 Simulation Pipeline Integration Tests (`tests/integration/test_simulation_pipeline.py`)
Validates end-to-end execution with the SUMO engine:
12. `test_controller_end_to_end_execution[FixedTimeController]`: Runs headless SUMO with Fixed-Time controller, verifying TraCI startup, stepping, cleanup, CSV time-series creation, and JSON manifest generation.
13. `test_controller_end_to_end_execution[ActuatedController]`: Runs headless SUMO with Vehicle-Actuated controller.
14. `test_controller_end_to_end_execution[MaxPressureController]`: Runs headless SUMO with Max-Pressure controller.

### 2.5 Smoke Environment Test (`tests/smoke/test_smoke.py`)
15. `test_smoke_environment`: Executes `scripts/check_environment.py`, auditing Python, SUMO binaries, `SUMO_HOME`, TraCI, PyTorch, YOLO, and executing a 60-second headless run.

---

## 3. Test Execution Command & Official Results

To execute the entire test suite from the project root:
```powershell
python -m pytest tests/ -v
```

### Verified Terminal Output
```text
============================= test session starts =============================
platform win32 -- Python 3.12.10, pytest-9.1.1, pluggy-1.7.0
rootdir: C:\ai_ml_project
configfile: pyproject.toml
plugins: anyio-4.15.1
collected 15 items

tests/integration/test_simulation_pipeline.py::test_controller_end_to_end_execution[FixedTimeController] PASSED [  6%]
tests/integration/test_simulation_pipeline.py::test_controller_end_to_end_execution[ActuatedController] PASSED [ 13%]
tests/integration/test_simulation_pipeline.py::test_controller_end_to_end_execution[MaxPressureController] PASSED [ 20%]
tests/smoke/test_smoke.py::test_smoke_environment PASSED                 [ 26%]
tests/unit/test_environment.py::test_env_observation_and_action_spaces PASSED [ 33%]
tests/unit/test_environment.py::test_env_reset_and_step PASSED           [ 40%]
tests/unit/test_perception.py::test_camera_calibration_coordinate_mapping PASSED [ 46%]
tests/unit/test_perception.py::test_camera_approach_roi_assignment PASSED [ 53%]
tests/unit/test_perception.py::test_vehicle_tracker_lifecycle PASSED     [ 60%]
tests/unit/test_perception.py::test_density_estimator_mae PASSED         [ 66%]
tests/unit/test_safety_manager.py::test_safety_manager_initialization PASSED [ 73%]
tests/unit/test_safety_manager.py::test_safety_manager_min_green_rejection PASSED [ 80%]
tests/unit/test_safety_manager.py::test_safety_manager_legal_transition_sequence PASSED [ 86%]
tests/unit/test_safety_manager.py::test_safety_manager_max_green_enforcement PASSED [ 93%]
tests/unit/test_safety_manager.py::test_safety_manager_rejects_requests_during_clearance PASSED [100%]

============================= 15 passed in 6.17s ==============================
```
- **Execution Time:** 6.17 seconds
- **Pass Rate:** 100% (15/15 passed, 0 failures, 0 warnings)
