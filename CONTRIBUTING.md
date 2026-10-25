# Contributing Guidelines

Thank you for your interest in contributing to the **AI & ML Based Adaptive Traffic Control System**!

## Code of Conduct
Please review and adhere to our [Code of Conduct](CODE_OF_CONDUCT.md) in all interactions.

## Branching Strategy & Workflow
1. **Fork or branch** from the `main` branch.
2. Use descriptive branch names:
   - `feature/new-controller-name`
   - `fix/safety-manager-edge-case`
   - `refactor/perception-tracker`
3. Commit messages should follow conventional commits:
   - `feat: add Coordinated Max-Pressure controller`
   - `fix: resolve dilemma zone calculation edge case`
   - `test: add unit tests for perception ROI mapping`

## Coding Standards
- **Python Version:** 3.10+ (tested on Python 3.12).
- **Code Style:** PEP 8 compliance.
- **Type Hints:** Use explicit Python type annotations (`typing.Dict`, `typing.List`, `typing.Optional`, etc.).
- **Data Schemas:** All system configurations, state definitions, and manifests must use Pydantic models in `src/traffic_ai/config/schemas.py`.

## Safety Constraints (Critical)
Any changes to traffic signal controllers must preserve the hard separation between policy logic and safety enforcement:
- Controllers must **only** emit target green phase proposals ($0, 1, 2, 3$).
- Controllers must **never** bypass the `DeterministicSafetyManager` or issue raw signal state strings directly to TraCI.
- Minimum green, maximum green, yellow clearance, and all-red clearance intervals must remain invariant.

## Running Tests
Before submitting a Pull Request, ensure that all unit and integration tests pass:

```powershell
python -m pytest tests/ -v
```

All 15 test suites must pass without errors or warnings.
