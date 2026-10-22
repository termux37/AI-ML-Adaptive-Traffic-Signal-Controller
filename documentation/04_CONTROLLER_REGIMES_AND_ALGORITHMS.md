# Module 04: Controller Regimes & Algorithms

## 1. Unified Controller Interface
All traffic controllers inherit from the abstract base class `TrafficSignalController` (`src/traffic_ai/control/interfaces.py`):

```python
class TrafficSignalController(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def reset(self) -> None:
        """Resets controller internal states."""
        pass

    @abstractmethod
    def propose_action(self, state: TrafficState) -> Optional[int]:
        """Proposes a target green phase ID (0..3) or None (hold current)."""
        pass

    def on_step(self, state: TrafficState, action: Optional[int], applied_signal: str) -> None:
        """Optional callback after simulation step execution."""
        pass

    def close(self) -> None:
        """Releases any controller resources."""
        pass
```

---

## 2. Fixed-Time Controller (Pre-Timed Baseline)
- **Module:** `src/traffic_ai/control/fixed_time.py`
- **Mechanism:** Implements a classical pre-timed cyclic signal plan.
- **Cycle Structure (Total 90s Cycle):**
  - Phase 0 (NS Through & Right): 30.0 seconds
  - Phase 1 (NS Protected Left): 15.0 seconds
  - Phase 2 (EW Through & Right): 30.0 seconds
  - Phase 3 (EW Protected Left): 15.0 seconds
- **Behavior:** Operates strictly by clock timer; ignores vehicle queue accumulation or directional surges. Serves as the primary reference baseline for improvement calculations.

---

## 3. Vehicle-Actuated Controller
- **Module:** `src/traffic_ai/control/actuated.py`
- **Mechanism:** Emulates standard NEMA/Type 170 actuated intersection controllers using stop-line loop presence sensing.
- **Parameters:**
  - `min_green`: 10.0 seconds
  - `max_green`: 50.0 seconds
  - `gap_threshold`: 3.0 seconds
- **Operational Logic:**
  1. Once a green phase is active, it is guaranteed to run for at least `min_green` (10s).
  2. The controller monitors arriving vehicles on the active green approach. If vehicles pass the stop-line detectors within the `gap_threshold` ($< 3.0$s headway), the green phase is extended.
  3. If a headway gap $> 3.0$s occurs (**gap-out**) or `time_in_green` reaches 50s (**max-out**), the green terminates and switches to the conflicting approach displaying the highest pending queue.

---

## 4. Max-Pressure Controller (PressLight Heuristic)
- **Module:** `src/traffic_ai/control/max_pressure.py`
- **Theoretical Basis:** Varaiya (2013); Wei et al. (KDD 2019).
- **Mechanism:** Calculates traffic "pressure" as the queue differential between upstream incoming approaches and downstream outgoing lanes.
- **Formulation:**
  For each movement $(l, m)$ served by phase $p$:
  $$w(l, m) = x_l - x_m$$
  where $x_l$ is the number of queued vehicles on upstream lane $l$, and $x_m$ is the downstream burden on exit lane $m$.
  The total pressure of phase $p$ is:
  $$P(p) = \sum_{(l, m) \in \mathcal{M}(p)} \max(0, x_l - x_m)$$
- **Decision Epochs:** Every 5.0 seconds, the controller selects:
  $$p^* = \arg\max_{p \in \{0, 1, 2, 3\}} P(p)$$
  If all pressures are zero, the active phase is maintained to prevent unnecessary switching.

---

## 5. Deep Q-Network (DQN) Controller
- **Module:** `src/traffic_ai/control/dqn_policy.py` & `src/traffic_ai/training/`
- **Framework:** Stable-Baselines3 with PyTorch backend.
- **Network Architecture:**
  - Policy: `MlpPolicy`
  - Hidden Layers: 2 fully-connected layers of 128 units each with ReLU activations (`net_arch=[128, 128]`).
  - Output Layer: 4 linear heads corresponding to $Q(s, a)$ for each green phase.

### 25-Dimensional Normalized Observation Vector $\mathbf{s}_t$

| Indices | Feature Description | Scaling & Normalization |
| :---: | :--- | :--- |
| **0 – 4** | North: Count, Queue, Speed, Wait, Occupancy | $N/30$, $Q/30$, $v/13.89$, $W/600$, $\text{Occ} \in [0, 1]$ |
| **5 – 9** | South: Count, Queue, Speed, Wait, Occupancy | $N/30$, $Q/30$, $v/13.89$, $W/600$, $\text{Occ} \in [0, 1]$ |
| **10 – 14** | East: Count, Queue, Speed, Wait, Occupancy | $N/30$, $Q/30$, $v/13.89$, $W/600$, $\text{Occ} \in [0, 1]$ |
| **15 – 19** | West: Count, Queue, Speed, Wait, Occupancy | $N/30$, $Q/30$, $v/13.89$, $W/600$, $\text{Occ} \in [0, 1]$ |
| **20 – 23** | Active Green Phase One-Hot | $[1, 0, 0, 0]$, $[0, 1, 0, 0]$, etc. |
| **24** | Normalized Green Elapsed Timer | $\min(1.0, t_{green} / 60.0)$ |

### Multi-Component Reward Formulation
$$r_t = w_q \cdot (Q_{t-1} - Q_t) + w_w \cdot \frac{W_{t-1} - W_t}{10.0} + w_t \cdot \Delta Thr - w_s \cdot \mathbb{I}_{switch} - w_{starv} \cdot \frac{\max(0, W_{max} - 60.0)}{60.0}$$

- $w_q = 1.0$: Direct reward for reducing total intersection queue.
- $w_w = 0.05$: Smooth reward for reducing accumulated active waiting burden.
- $w_t = 2.0$: Positive bonus for each completed vehicle exiting the network.
- $w_s = 2.0$: Penalty incurred when a phase transition is requested, discouraging rapid signal oscillation.
- $w_{starv} = 1.5$: Penalty applied when any vehicle experiences waiting times exceeding 60.0 seconds.

### Hyperparameters Summary

| Hyperparameter | Value | Rationale |
| :--- | :---: | :--- |
| Learning Rate ($\alpha$) | $0.0005$ | Stable gradient descent steps on Adam optimizer |
| Discount Factor ($\gamma$) | $0.99$ | Long-term horizon planning across decision epochs |
| Replay Buffer Size | $20,000$ | Bounded for memory efficiency (16 GB RAM) |
| Batch Size | $64$ | Balanced mini-batch sample efficiency |
| Exploration ($\epsilon$) | $1.0 \to 0.05$ | Linear decay across initial 30% of training steps |
| Target Update Interval | $500$ steps | Periodic hard Polyak target network synchronization |
| Decision Interval | $5.0$ seconds | Allows physical queue discharge dynamics to unfold |
