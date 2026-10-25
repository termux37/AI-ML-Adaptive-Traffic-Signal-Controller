"""Metrics collection, time-series logging, and run manifest generation."""

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

from traffic_ai.control.safety_manager import DecisionRecord
from traffic_ai.state.schemas import TrafficState


class MetricsCollector:
    """Collects real-time step metrics and computes end-of-run performance aggregates."""

    def __init__(self, run_id: str, warmup_seconds: float = 300.0, output_dir: Path = Path("data/runs")):
        self.run_id = run_id
        self.warmup_seconds = warmup_seconds
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.step_records: List[Dict[str, Any]] = []
        self.completed_trip_durations: List[float] = []
        self.completed_trip_delays: List[float] = []
        self.phase_switches: int = 0
        self.last_phase: Optional[int] = None

    def record_step(self, state: TrafficState, decision: DecisionRecord) -> None:
        """Records traffic and decision state for the current simulation step."""
        sim_time = state.timestamp

        # Track phase changes
        if self.last_phase is not None and state.current_green_id != self.last_phase and not state.is_in_transition:
            self.phase_switches += 1
        self.last_phase = state.current_green_id

        # Approach-specific queues and waits
        q_n = state.approaches.get("north").queue_length if "north" in state.approaches else 0
        q_s = state.approaches.get("south").queue_length if "south" in state.approaches else 0
        q_e = state.approaches.get("east").queue_length if "east" in state.approaches else 0
        q_w = state.approaches.get("west").queue_length if "west" in state.approaches else 0

        w_n = state.approaches.get("north").total_waiting_time_s if "north" in state.approaches else 0.0
        w_s = state.approaches.get("south").total_waiting_time_s if "south" in state.approaches else 0.0
        w_e = state.approaches.get("east").total_waiting_time_s if "east" in state.approaches else 0.0
        w_w = state.approaches.get("west").total_waiting_time_s if "west" in state.approaches else 0.0

        max_w_n = state.approaches.get("north").max_wait_time_s if "north" in state.approaches else 0.0
        max_w_s = state.approaches.get("south").max_wait_time_s if "south" in state.approaches else 0.0
        max_w_e = state.approaches.get("east").max_wait_time_s if "east" in state.approaches else 0.0
        max_w_w = state.approaches.get("west").max_wait_time_s if "west" in state.approaches else 0.0

        speeds = [app.mean_speed_mps for app in state.approaches.values() if app.vehicle_count > 0]
        mean_spd = float(np.mean(speeds)) if speeds else 13.89

        record = {
            "timestamp": sim_time,
            "active_vehicles": state.total_vehicles,
            "total_queue": state.total_queue,
            "total_waiting_time": state.total_waiting_time,
            "mean_speed_mps": mean_spd,
            "throughput_step": state.completed_vehicles_step,
            "cumulative_throughput": state.total_completed_vehicles,
            "current_green_id": state.current_green_id,
            "is_in_transition": int(state.is_in_transition),
            "signal_state": str(decision.signal_state.value),
            "requested_phase": decision.requested_phase if decision.requested_phase is not None else -1,
            "action_accepted": int(decision.accepted),
            "decision_reason": str(decision.reason.value),
            "queue_north": q_n,
            "queue_south": q_s,
            "queue_east": q_e,
            "queue_west": q_w,
            "waiting_north": w_n,
            "waiting_south": w_s,
            "waiting_east": w_e,
            "waiting_west": w_w,
            "max_wait_north": max_w_n,
            "max_wait_south": max_w_s,
            "max_wait_east": max_w_e,
            "max_wait_west": max_w_w,
            "max_waiting_any": state.max_waiting_time,
        }
        self.step_records.append(record)

    def record_completed_trip(self, duration: float, delay: float) -> None:
        """Records trip metrics for an arrived vehicle."""
        self.completed_trip_durations.append(duration)
        self.completed_trip_delays.append(delay)

    def compute_summary_metrics(self) -> Dict[str, Any]:
        """Calculates final aggregate metrics, excluding the warmup duration."""
        if not self.step_records:
            return {}

        df = pd.DataFrame(self.step_records)
        scored_df = df[df["timestamp"] >= self.warmup_seconds]
        if scored_df.empty:
            scored_df = df

        scored_duration_s = float(scored_df["timestamp"].iloc[-1] - scored_df["timestamp"].iloc[0] + 1.0)
        scored_duration_h = scored_duration_s / 3600.0 if scored_duration_s > 0 else 1.0

        throughput_scored = int(scored_df["throughput_step"].sum())
        throughput_vph = round(throughput_scored / scored_duration_h, 2)

        mean_travel_time = (
            float(np.mean(self.completed_trip_durations))
            if self.completed_trip_durations else 0.0
        )
        mean_delay = (
            float(np.mean(self.completed_trip_delays))
            if self.completed_trip_delays else 0.0
        )

        avg_queue = float(scored_df["total_queue"].mean())
        max_queue = int(scored_df["total_queue"].max())
        avg_wait = float(scored_df["total_waiting_time"].mean())
        max_wait_observed = float(scored_df["max_waiting_any"].max())

        # Switching frequency (switches per 1000 simulated seconds)
        switch_freq = round((self.phase_switches / scored_duration_s) * 1000.0, 2) if scored_duration_s > 0 else 0.0

        # Approach-level mean waiting times for fairness index
        app_waits = [
            float(scored_df["waiting_north"].mean()),
            float(scored_df["waiting_south"].mean()),
            float(scored_df["waiting_east"].mean()),
            float(scored_df["waiting_west"].mean()),
        ]
        sum_w = sum(app_waits)
        sum_w_sq = sum(w ** 2 for w in app_waits)
        jains_index = (sum_w ** 2) / (4.0 * sum_w_sq) if sum_w_sq > 0 else 1.0

        return {
            "scored_duration_seconds": scored_duration_s,
            "total_completed_vehicles": int(df["cumulative_throughput"].iloc[-1]),
            "scored_throughput_vehicles": throughput_scored,
            "throughput_vph": throughput_vph,
            "mean_travel_time_seconds": round(mean_travel_time, 2),
            "mean_delay_seconds": round(mean_delay, 2),
            "average_queue_length": round(avg_queue, 2),
            "max_queue_length": max_queue,
            "average_waiting_time_seconds": round(avg_wait, 2),
            "max_wait_time_seconds": round(max_wait_observed, 2),
            "phase_switches_total": self.phase_switches,
            "switching_frequency_per_1000s": switch_freq,
            "jains_fairness_index": round(float(jains_index), 4),
            "approach_avg_queues": {
                "north": round(float(scored_df["queue_north"].mean()), 2),
                "south": round(float(scored_df["queue_south"].mean()), 2),
                "east":  round(float(scored_df["queue_east"].mean()), 2),
                "west":  round(float(scored_df["queue_west"].mean()), 2),
            },
        }

    def save_run_artifacts(self, metadata: Dict[str, Any]) -> Tuple[Path, Path]:
        """Saves time series CSV and JSON run manifest."""
        csv_path = self.output_dir / f"{self.run_id}_timeseries.csv"
        manifest_path = self.output_dir / f"{self.run_id}_manifest.json"

        df = pd.DataFrame(self.step_records)
        df.to_csv(csv_path, index=False)

        summary = self.compute_summary_metrics()

        manifest = {
            "run_id": self.run_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "metadata": metadata,
            "summary_metrics": summary,
            "artifacts": {
                "timeseries_csv": str(csv_path),
            },
        }

        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

        return csv_path, manifest_path
