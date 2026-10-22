# Module 03: Deterministic Safety Manager

## 1. Safety Philosophy & Policy Independence
In intelligent transportation systems, reinforcement learning policies are treated as **untrusted optimization proposal agents**. An unconstrained neural network could output illegal phase states, oscillate rapidly, violate clearance intervals, or create catastrophic green-green vehicle collisions.

To guarantee zero safety violations, Adaptive Traffic Control System enforces a strict architectural boundary:
- The controller (DQN or baseline) emits only an **Action Proposal** ($a \in \{0, 1, 2, 3\}$).
- The `DeterministicSafetyManager` intercepts all proposals, validates them against physical traffic engineering constraints, executes clearance state transitions, and commits the resulting signal state to the simulator.

```
+--------------------+                 +-------------------------------+
|  Signal Controller |                 | Deterministic Safety Manager  |
|   (DQN / Policy)   |                 |                               |
+--------------------+                 +-------------------------------+
          |                                            |
          | 1. Action Proposal (Target Phase j)        |
          |------------------------------------------->|
          |                                            | 2. Check Constraints:
          |                                            |    • Is phase valid?
          |                                            |    • Is clearance in progress?
          |                                            |    • Has min_green elapsed?
          |                                            |    • Has max_green expired?
          |                                            |
          | 3. Decision Record & Reason                | 4. Execute State Machine:
          |<-------------------------------------------|    • Advance yellow / red timer
          |                                            |    • Emit valid 16-char string
          v                                            v
```

---

## 2. Signal States & Transitions

The safety manager maintains an internal finite state machine with three operational states:
1. **`SignalState.GREEN`:** Active green phase $i \in \{0, 1, 2, 3\}$.
2. **`SignalState.YELLOW`:** Intermediate clearance yellow phase for movement $i$.
3. **`SignalState.ALL_RED`:** Total clearance interval where all links display red (`rrrrrrrrrrrrrrrr`).

### Legal Transition Sequence
When transitioning from Phase $i$ to Phase $j$ ($i \neq j$):
1. **Step 1 (Yellow Clearance):** The signal displays the yellow state corresponding to Phase $i$ for exactly $t_{yellow} = 3.0$ seconds.
2. **Step 2 (All-Red Clearance):** The signal displays `rrrrrrrrrrrrrrrr` for exactly $t_{all\_red} = 2.0$ seconds to clear any vehicles remaining in the intersection box.
3. **Step 3 (Target Green):** The signal transitions to the green state of Phase $j$, and the green timer resets to $0.0$ seconds.

---

## 3. Mandatory Safety Constraints & Invariants

| Invariant Parameter | Configured Value | Enforcement Logic | Reason Code Emitted |
| :--- | :---: | :--- | :--- |
| **Minimum Green Duration** | 10.0 seconds | If an agent requests a phase switch when $t_{green} < 10.0$s, the request is rejected and current green is maintained. | `MIN_GREEN_NOT_REACHED` |
| **Maximum Green Duration** | 60.0 seconds | If $t_{green} \ge 60.0$s, the current green is terminated regardless of agent requests to prevent approach starvation. A transition to $(i+1) \pmod 4$ is forced. | `MAX_GREEN_ENFORCED` |
| **Yellow Clearance Duration** | 3.0 seconds | Enforced strictly by internal timer; cannot be truncated or bypassed. | `TRANSITION_IN_PROGRESS` |
| **All-Red Clearance Duration** | 2.0 seconds | Enforced strictly by internal timer; opposing greens cannot be displayed early. | `TRANSITION_IN_PROGRESS` |
| **Same Phase Hold** | Dynamic | If the agent requests the currently active green phase ($j == i$) and $t_{green} < 60.0$s, green is extended. | `HOLD_GREEN` |

---

## 4. Signal Strings and Link Mappings

The 16-character signal strings correspond exactly to the 16 controlled link movements:

```
Link indices:   0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15
Movements:      Nr Ns Ns Nl Er Es Es El Sr Ss Ss Sl Wr Ws Ws Wl
```

### Phase Catalog Definitions
- **Phase 0 (NS Through & Right):**
  - Green state: `GGGrrrrrGGGrrrrr` (duration 30s)
  - Yellow state: `yyyrrrrryyyrrrrr` (duration 3s)
- **Phase 1 (NS Protected Left):**
  - Green state: `rrrGrrrrrrrGrrrr` (duration 15s)
  - Yellow state: `rrryrrrrrrryrrrr` (duration 3s)
- **Phase 2 (EW Through & Right):**
  - Green state: `rrrrGGGrrrrrGGGr` (duration 30s)
  - Yellow state: `rrrryyyrrrrryyyr` (duration 3s)
- **Phase 3 (EW Protected Left):**
  - Green state: `rrrrrrrGrrrrrrrG` (duration 15s)
  - Yellow state: `rrrrrrryrrrrrrry` (duration 3s)
- **All-Red Clearance State:**
  - Clearance state: `rrrrrrrrrrrrrrrr` (duration 2s)

---

## 5. Fail-Safe Fallback Behavior
- **Invalid Phase Requests:** If a policy outputs an index outside $\{0, 1, 2, 3\}$ (e.g. negative number or integer $\ge 4$), the safety manager rejects the request with `INVALID_PHASE_REQUEST` and maintains the current safe state.
- **Controller Exceptions:** If a controller throws an unhandled Python exception during inference, the `SimulationRunner` catches the exception, logs a warning, and defaults to holding the current safe green phase.
- **Simulation Shutdown:** The reset procedure restores the network to Phase 0 Green before terminating TraCI connections.
