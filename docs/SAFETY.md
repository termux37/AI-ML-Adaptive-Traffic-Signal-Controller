# AI & ML Based Adaptive Traffic Control System - Deterministic Safety Specification

## 1. Safety Principles & Independence
A fundamental engineering principle of Adaptive Traffic Control System is that **safety constraints are completely independent of the learned neural network policy**. The reinforcement learning agent (or heuristic controller) only emits an *action proposal*. All proposals are intercepted and governed by the `DeterministicSafetyManager`.

Under no circumstances can the policy directly write arbitrary signal strings, bypass yellow clearance, or produce conflicting green indications.

## 2. Guard Parameters and Invariants

| Parameter | Value | Traffic Engineering Purpose | Enforced Behavior |
| :--- | :--- | :--- | :--- |
| **Minimum Green ($t_{min}$)** | 10.0 s | Prevents rapid cycling; allows queue discharge | Requests to switch prior to 10s are rejected with `MIN_GREEN_NOT_REACHED` |
| **Maximum Green ($t_{max}$)** | 60.0 s | Prevents cross-street starvation | When $t \ge 60$s, transition to next phase is forced with `MAX_GREEN_ENFORCED` |
| **Yellow Clearance ($t_{yellow}$)** | 3.0 s | Allows moving vehicles to clear intersection | Signal displays approach-specific yellow state for exactly 3.0 seconds |
| **All-Red Clearance ($t_{red}$)** | 2.0 s | Clears intersection box before opposing green | Signal displays `rrrrrrrrrrrrrrrr` for exactly 2.0 seconds |

## 3. Transition State Machine
```
[ GREEN PHASE i ] 
       |
       |-- Action requested: j != i AND time >= min_green
       v
[ YELLOW PHASE i (3.0s) ] 
       |
       v (timer expires)
[ ALL-RED CLEARANCE (2.0s) ]
       |
       v (timer expires)
[ GREEN PHASE j (time = 0.0s) ]
```

During clearance intervals (`YELLOW` or `ALL_RED`):
- Any action requests from the agent are ignored with reason `TRANSITION_IN_PROGRESS`.
- Opposing conflicting movements are strictly held in red (`r`).

## 4. Conflict Matrix
In the single-intersection 4-phase catalog:
- NS movements (Phases 0 & 1) conflict with EW movements (Phases 2 & 3).
- Through movements conflict with opposing left turns.
- Therefore, the legal transition matrix allows only transitions that pass through intermediate yellow and all-red clearance intervals. Simultaneous conflicting green indications evaluate to 0 in all reachable states.

## 5. Verification & Test Suite
Unit tests in `tests/unit/test_safety_manager.py` systematically verify:
- Initial state safety (`test_safety_manager_initialization`)
- Minimum green rejection (`test_safety_manager_min_green_rejection`)
- Multi-step clearance progression (`test_safety_manager_legal_transition_sequence`)
- Maximum green starvation prevention (`test_safety_manager_max_green_enforcement`)
- Immunity to illegal requests during clearance (`test_safety_manager_rejects_requests_during_clearance`)
