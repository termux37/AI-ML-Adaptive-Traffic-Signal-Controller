# AI & ML Based Adaptive Traffic Control System - Experiment & Benchmarking Protocol

## 1. Experimental Integrity Rules
To guarantee scientific validity, reproducibility, and prevent benchmark contamination:
1. **Identical Demand on Comparable Runs:** When comparing Fixed-Time, Actuated, Max-Pressure, and DQN, all controllers must be evaluated on the exact same road network, demand scenario, arrival parameters, and random seeds.
2. **Seed Separation:** Training seeds (e.g. 42, 101) are strictly separated from test evaluation seeds (e.g. 202, 303, 404).
3. **Warm-up Interval:** Initial network filling (empty intersection at $t=0$) is excluded from scored metrics.
4. **No Cherry-Picking:** All aggregate tables present the mean across all tested seeds, along with min/max or standard deviations.
5. **No Hallucinated Data:** Every entry in `data/processed/benchmark_results.csv` is produced directly by actual simulation runs via `scripts/evaluate_agent.py` or the dashboard benchmarking runner.

## 2. Standard Benchmark Scenarios

| Scenario ID | Primary Traffic Characteristic | North / South Demand | East / West Demand | Total Inflow |
| :--- | :--- | :--- | :--- | :--- |
| `low` | Light off-peak traffic | 180 vph | 180 vph | 720 vph |
| `balanced` | Moderate symmetrical traffic | 420 vph | 420 vph | 1,680 vph |
| `heavy` | High demand near intersection saturation | 750 vph | 750 vph | 3,000 vph |
| `north_south_dominant` | Severe directional imbalance (arterial corridor) | 720 / 680 vph | 160 / 160 vph | 1,720 vph |
| `east_west_dominant` | Severe directional imbalance (cross street) | 160 / 160 vph | 720 / 680 vph | 1,720 vph |
| `bursty` | Periodic vehicle platooning waves (3x surge) | 250 vph + bursts | 250 vph + bursts | Dynamic |
| `unseen_evaluation` | Asymmetrical demand with irregular turning ratios | 620 / 280 vph | 480 / 210 vph | 1,590 vph |

## 3. Benchmark Execution Command
To reproduce the full benchmark suite across all controllers:
```powershell
$env:PYTHONPATH = "src"
python scripts/evaluate_agent.py --duration 180 --seeds 101 202
```
Output results are exported to:
- `data/processed/benchmark_results.csv`
- `data/processed/benchmark_results.json`
