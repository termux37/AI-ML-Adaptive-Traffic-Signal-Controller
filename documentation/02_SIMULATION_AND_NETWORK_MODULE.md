# Module 02: Simulation & Road Network Specification

## 1. Microscopic Simulation Mechanics
Adaptive Traffic Control System simulates vehicular traffic at the microscopic scale using **Eclipse SUMO 1.27.1**.
- **Car-Following Model:** Krauss model with stochastic driver imperfection ($\sigma = 0.5$).
- **Time Step Resolution:** $\Delta t = 1.0$ simulated second per tick.
- **Simulation Control:** Managed via TraCI (Traffic Control Interface) Python bindings.
- **Teleportation Policy:** `--time-to-teleport -1` (teleportation disabled to measure true gridlock if it occurs).

---

## 2. Road Network Geometry

The road network (`junction_center`) represents an urban arterial four-way signalized intersection located at coordinates $(250.0, 250.0)$.

```
                            |  ||  |
                            |  ||  |  North Approach (edge_n2c)
                            |  ||  |  2 Lanes, 250m Length
                            |  ||  |  [Stopline at 239.6m]
                     -------+--++--+-------
                     -------+--++--+-------
  West Approach             |  ||  |              East Approach
  (edge_w2c)                |  ||  |              (edge_e2c)
  2 Lanes, 250m             |  ||  |              2 Lanes, 250m
                     -------+--++--+-------
                     -------+--++--+-------
                            |  ||  |
                            |  ||  |  South Approach (edge_s2c)
                            |  ||  |  2 Lanes, 250m Length
                            |  ||  |  [Stopline at 239.6m]
```

### Approach Characteristics
- **Approaches:** North (`edge_n2c`), South (`edge_s2c`), East (`edge_e2c`), West (`edge_w2c`).
- **Outgoing Edges:** North (`edge_c2n`), South (`edge_c2s`), East (`edge_c2e`), West (`edge_c2w`).
- **Incoming Lanes:** 2 incoming lanes per approach (Lane width: 3.2m, Speed limit: 13.89 m/s = 50 km/h).
- **Lane Allocation:**
  - **Lane 0 (Outer / Right):** Through traffic + Right-turning traffic.
  - **Lane 1 (Inner / Left):** Through traffic + Protected Left-turning traffic.

---

## 3. Link Index & Movement Mapping (16 Links)

The traffic light logic controls 16 distinct movement connections:

| Link Index | From Lane | To Lane | Approach | Movement | Phase Allowed |
| :---: | :--- | :--- | :---: | :---: | :---: |
| **0** | `edge_n2c_0` | `edge_c2w_0` | North | Right Turn | Phase 0 (NS Thru/Right) |
| **1** | `edge_n2c_0` | `edge_c2s_0` | North | Straight Through | Phase 0 (NS Thru/Right) |
| **2** | `edge_n2c_1` | `edge_c2s_1` | North | Straight Through | Phase 0 (NS Thru/Right) |
| **3** | `edge_n2c_1` | `edge_c2e_1` | North | Protected Left Turn | Phase 1 (NS Left) |
| **4** | `edge_e2c_0` | `edge_c2n_0` | East | Right Turn | Phase 2 (EW Thru/Right) |
| **5** | `edge_e2c_0` | `edge_c2w_0` | East | Straight Through | Phase 2 (EW Thru/Right) |
| **6** | `edge_e2c_1` | `edge_c2w_1` | East | Straight Through | Phase 2 (EW Thru/Right) |
| **7** | `edge_e2c_1` | `edge_c2s_1` | East | Protected Left Turn | Phase 3 (EW Left) |
| **8** | `edge_s2c_0` | `edge_c2e_0` | South | Right Turn | Phase 0 (NS Thru/Right) |
| **9** | `edge_s2c_0` | `edge_c2n_0` | South | Straight Through | Phase 0 (NS Thru/Right) |
| **10** | `edge_s2c_1` | `edge_c2n_1` | South | Straight Through | Phase 0 (NS Thru/Right) |
| **11** | `edge_s2c_1` | `edge_c2w_1` | South | Protected Left Turn | Phase 1 (NS Left) |
| **12** | `edge_w2c_0` | `edge_c2s_0` | West | Right Turn | Phase 2 (EW Thru/Right) |
| **13** | `edge_w2c_0` | `edge_c2e_0` | West | Straight Through | Phase 2 (EW Thru/Right) |
| **14** | `edge_w2c_1` | `edge_c2e_1` | West | Straight Through | Phase 2 (EW Thru/Right) |
| **15** | `edge_w2c_1` | `edge_c2n_1` | West | Protected Left Turn | Phase 3 (EW Left) |

---

## 4. Induction Loop Detectors (E1 Detectors)

Induction loop detectors are defined in `simulation/network/detectors.add.xml` on every incoming lane:
1. **Stopline Detectors (`det_stop_*`):** Located at position $230.0$m (approx 9m before the stopline). Used for stopline vehicle presence sensing, queue counting, and actuation calls.
2. **Advance Detectors (`det_adv_*`):** Located at position $120.0$m (119.6m upstream from stopline). Used for advance arrival detection and queue growth monitoring.

---

## 5. Scenario Demand Profiles & Generation Mathematics

The `ScenarioManager` creates reproducible synthetic demand using exponential inter-arrival times:
$$\Delta t_{arrival} \sim \text{Exponential}\left(\lambda = \frac{\text{Rate (vph)}}{3600}\right)$$

### Predefined Scenarios

| Scenario Preset | North Demand | South Demand | East Demand | West Demand | Characteristic |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `low` | 180 vph | 180 vph | 180 vph | 180 vph | Off-peak light traffic |
| `balanced` | 420 vph | 420 vph | 420 vph | 420 vph | Moderate symmetrical demand |
| `heavy` | 750 vph | 750 vph | 750 vph | 750 vph | Near-capacity saturation |
| `north_south_dominant` | 720 vph | 680 vph | 160 vph | 160 vph | Severe directional corridor demand |
| `east_west_dominant` | 160 vph | 160 vph | 720 vph | 680 vph | Severe cross-street demand |
| `bursty` | 250 vph | 250 vph | 250 vph | 250 vph | 3.0x surge wave every 180s for 45s |
| `unseen_evaluation` | 620 vph | 280 vph | 480 vph | 210 vph | Asymmetrical evaluation profile |

### Vehicle Class Specifications

| Class ID | SUMO vClass | Length | Width | Max Speed | Acceleration | Deceleration | Proportion |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `veh_passenger` | `passenger` | 4.5m | 1.8m | 13.89 m/s | 2.6 m/s² | 4.5 m/s² | 75% |
| `veh_bus` | `bus` | 12.0m | 2.5m | 11.11 m/s | 1.6 m/s² | 3.5 m/s² | 8% |
| `veh_truck` | `truck` | 8.5m | 2.4m | 10.00 m/s | 1.4 m/s² | 3.2 m/s² | 12% |
| `veh_motorcycle`| `motorcycle`| 2.2m | 0.9m | 15.00 m/s | 3.5 m/s² | 5.0 m/s² | 5% |
