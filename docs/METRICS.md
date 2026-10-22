# AI & ML Based Adaptive Traffic Control System - Metrics and Experimental Measurement

## 1. Metric Definitions

### 1.1 Throughput (Vehicles / Hour)
- **Definition:** Total completed trips departing the intersection during the scored interval, scaled to an hourly rate:
  $$\text{Throughput (vph)} = \frac{N_{completed}}{\Delta t_{scored} / 3600}$$
- **Units:** Vehicles per hour (`vph`).
- **Higher is better.**

### 1.2 Average Queue Length
- **Definition:** The time-weighted average number of halted vehicles across all 4 incoming approaches. A vehicle is considered queued when its instantaneous speed is below 0.1 m/s:
  $$\bar{Q} = \frac{1}{T} \sum_{t=1}^T \sum_{app \in \{N,S,E,W\}} Q_{app}(t)$$
- **Units:** Vehicles (`veh`).
- **Lower is better.**

### 1.3 Average Waiting Time
- **Definition:** Accumulated waiting time experienced by active vehicles currently on incoming approaches:
  $$\bar{W} = \frac{1}{T} \sum_{t=1}^T W_{total}(t)$$
- **Units:** Seconds (`s`).
- **Lower is better.**

### 1.4 Phase Switching Frequency
- **Definition:** Number of signal phase transitions initiated per 1,000 simulated seconds:
  $$\text{Freq}_{switch} = \frac{N_{switches}}{\Delta t_{scored}} \times 1000$$
- **Units:** Switches per 1,000 seconds.
- **Lower is better (avoids hunting / chatter).**

### 1.5 Jain's Fairness Index
- **Definition:** Evaluates waiting time equality across the 4 physical approaches:
  $$\mathcal{J}(w_1, w_2, w_3, w_4) = \frac{\left(\sum_{i=1}^4 w_i\right)^2}{4 \cdot \sum_{i=1}^4 w_i^2}$$
  where $w_i$ is the average waiting time on approach $i$.
- **Bounds:** Bound between $0.25$ (extreme starvation where 1 approach incurs all waiting) and $1.0$ (perfectly balanced waiting across approaches).
- **Higher is better.**

## 2. Baseline Comparison Formula
For metrics where **lower is better** (queue length, delay, waiting time):
$$\text{Improvement (\%)} = 100 \times \frac{\text{Baseline Value} - \text{Proposed Value}}{\text{Baseline Value}}$$

For metrics where **higher is better** (throughput, fairness):
$$\text{Improvement (\%)} = 100 \times \frac{\text{Proposed Value} - \text{Baseline Value}}{\text{Baseline Value}}$$

## 3. Exclusion of Warmup Interval
To prevent initial network loading transients (empty road network at $t=0$) from biasing steady-state performance metrics, a configurable warm-up period (default 30 to 300 seconds) is excluded from all scored metrics calculations.
