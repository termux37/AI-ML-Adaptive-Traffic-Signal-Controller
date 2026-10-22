# AI & ML Based Adaptive Traffic Control System - Methodology

## 1. Intersection Simulation Design
The virtual road network consists of a symmetrical 4-way intersection (`junction_center`) with approaches from North (`edge_n2c`), South (`edge_s2c`), East (`edge_e2c`), and West (`edge_w2c`).
- Each incoming edge has 2 lanes of width 3.2 meters and length 250 meters.
- Speed limit: 50 km/h (13.89 m/s).
- Stop lines are positioned 239.6 meters downstream from the network boundary.
- Movement assignment:
  - Lane 0 (outer / right): Through movement + Right turn
  - Lane 1 (inner / left): Through movement + Protected Left turn

### Phase Catalog
The traffic light controls 16 individual link movements partitioned into 4 mutually exclusive green phases:
- **Phase 0 (NS Through/Right):** `GGGrrrrrGGGrrrrr` (Links 0, 1, 2, 8, 9, 10 green)
- **Phase 1 (NS Protected Left):** `rrrGrrrrrrrGrrrr` (Links 3, 11 green)
- **Phase 2 (EW Through/Right):** `rrrrGGGrrrrrGGGr` (Links 4, 5, 6, 12, 13, 14 green)
- **Phase 3 (EW Protected Left):** `rrrrrrrGrrrrrrrG` (Links 7, 15 green)

## 2. Reinforcement Learning Formulation

### Observation Space
The state is represented as a normalized continuous vector $\mathbf{s}_t \in \mathbb{R}^{25}$:
1. **Per-Approach Metrics (5 features $\times$ 4 approaches = 20):**
   - Normalized vehicle count: $\min(1.0, N_{app} / 30.0)$
   - Normalized queue length: $\min(1.0, Q_{app} / 30.0)$
   - Normalized mean speed: $\min(1.0, v_{app} / 13.89)$
   - Normalized accumulated wait: $\min(1.0, W_{app} / 600.0)$
   - Lane occupancy ratio: $[0.0, 1.0]$
2. **Intersection State (5 features):**
   - Active green phase one-hot: $\mathbf{e}_{phase} \in \{0, 1\}^4$
   - Normalized green phase elapsed timer: $\min(1.0, t_{green} / 60.0)$

### Action Space
Discrete action space $\mathcal{A} = \{0, 1, 2, 3\}$ where each action represents a request to transition to (or maintain) the corresponding Green Phase. Decisions are evaluated at 5-second decision epochs.

### Reward Function
The reward balances queue reduction, vehicle throughput, phase stability, and fairness:
$$r_t = w_q \cdot (Q_{t-1} - Q_t) + w_w \cdot \frac{W_{t-1} - W_t}{10.0} + w_{thr} \cdot \Delta Thr - w_s \cdot \mathbb{I}_{switch} - w_{starv} \cdot \frac{\max(0, W_{max} - 60.0)}{60.0}$$
- $w_q = 1.0$: Encourages clearing queues.
- $w_w = 0.05$: Rewards decreasing total active waiting time.
- $w_{thr} = 2.0$: Positive bonus for each vehicle departing the intersection.
- $w_s = 2.0$: Penalty incurred if a phase transition is initiated, damping high-frequency signal hunting.
- $w_{starv} = 1.5$: Penalty proportional to how much the longest-waiting vehicle exceeds 60 seconds.

## 3. Baseline Controllers
1. **Fixed-Time:** Pre-timed cyclic program with green splits: Phase 0 (30s), Phase 1 (15s), Phase 2 (30s), Phase 3 (15s).
2. **Vehicle-Actuated:** Dynamic extension using stopline presence detectors. Green is extended if arriving vehicles maintain a time headway $< 3.0$ seconds, terminating on gap-out or at 50s max-green.
3. **Max-Pressure:** Evaluates queue differential $P(p) = \sum_{in} Q_{in} - \sum_{out} Q_{out}$ and requests the phase with maximum positive pressure.
