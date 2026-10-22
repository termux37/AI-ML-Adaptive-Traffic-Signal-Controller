# AI & ML Based Adaptive Traffic Control System - Research Notes & Literature Review

## 1. Literature Overview & Core Themes

Adaptive traffic signal control has evolved across three primary engineering paradigms:
1. **Rule-Based & Time-of-Day Control (Webster, 1958; Akcelik, 1981):** Static signal splits calculated from historical demand surveys. While simple and reliable, fixed-time plans fail to accommodate stochastic surge events or changing travel patterns.
2. **Vehicle-Actuated Control (Gordon & Tighe, 2005):** Stop-line and advance presence detectors dynamically extend green phases based on measured gaps between arriving vehicles. Gap-out thresholds and maximum green timers prevent indefinite green extension.
3. **Max-Pressure Control (Varaiya, 2013):** A decentralized feedback policy proving network-wide queue stability without requiring knowledge of origin-destination arrival rates.
4. **Deep Reinforcement Learning (Wei et al., 2018; 2019):** Deep neural networks parameterized as Q-networks or policy gradients trained in microscopic simulators to optimize complex composite objectives.

## 2. Theoretical Grounding: PressLight (KDD 2019)
The design of Adaptive Traffic Control System's state representation, pressure baseline, and reward function is directly informed by:

> **PressLight: Learning Max Pressure Control to Coordinate Traffic Signals in Arterial Networks**  
> *Hua Wei, Chacha Chen, Guanjie Zheng, Kan Wu, Vikash Gayah, Kaidi Xu, Zhenhui Li.*  
> *ACM SIGKDD Conference on Knowledge Discovery and Data Mining (KDD), 2019.*  
> *DOI: 10.1145/3292500.3330949*

### Relationship between Max-Pressure and Reinforcement Learning
In traditional Max-Pressure theory (Varaiya 2013), the pressure of movement $(l, m)$ from incoming lane $l$ to outgoing lane $m$ is defined as the queue differential:
$$w(l, m) = x_l - x_m$$
Where $x_l$ is the queue burden on lane $l$ and $x_m$ is the downstream burden on lane $m$. A phase $p$ is assigned pressure $P(p) = \sum_{(l, m) \in \mathcal{M}(p)} w(l, m)$.

PressLight bridges Max-Pressure and Deep Q-Learning by demonstrating that if the RL reward function is formulated around minimizing pressure changes:
$$r_t = -\sum_{l} x_l(t)$$
the learned policy naturally aligns with the Lyapunov stability guarantees of Max-Pressure, while retaining the capacity to anticipate non-linear vehicle arrival dynamics and turning movements.

### Differences in Adaptive Traffic Control System Implementation
- **Scale:** While PressLight evaluates multi-intersection arterial networks, Adaptive Traffic Control System concentrates on a single high-fidelity 4-way intersection to ensure deterministic safety verification and real-time vision integration.
- **Safety Manager:** PressLight operates with simplified phase switching. Adaptive Traffic Control System introduces a strict `DeterministicSafetyManager` that decouples the policy from clearance and transition logic.

## 3. Microscopic Simulation and TraCI Foundation
> **Microscopic Traffic Simulation using SUMO**  
> *P. A. Lopez, M. Behrisch, L. Bieker-Walz, J. Erdmann, Y.-P. Flotterod, R. Hilbrich, L. Lucken, J. Rummel, P. Wagner, E. WieBner.*  
> *IEEE Intelligent Transportation Systems Conference (ITSC), 2018.*

SUMO provides microscopic car-following models (Krauss 1998) with stochastic driver imperfection ($\sigma = 0.5$). TraCI provides socket-based IPC allowing TraCI clients to query lane halting numbers, mean speeds, and vehicle coordinates, and actuate traffic lights synchronously.

## 4. Empirical Literature on Computer Vision in Traffic Control
Pretrained object detectors (such as Ultralytics YOLOv8) provide rapid inference ($< 40$ms on commodity hardware) for multi-class vehicle identification. However, applying vision to closed-loop traffic control presents unique challenges:
- **Perspective Occlusion:** In oblique camera views, high-profile vehicles (e.g. buses, semi-trucks) obscure smaller passenger cars or motorcycles behind them.
- **Approximation of Queues:** Bounding box centroids must be mapped to geometric road polygons to estimate approach demand, which introduces spatial quantization noise compared to inductive loops.
