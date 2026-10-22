"""Generates a demo video showcasing the virtual camera and YOLO perception pipeline."""

import argparse
from pathlib import Path
import traci

from traffic_ai.config.schemas import ScenarioConfig, ScenarioName, SimulationConfig
from traffic_ai.control.fixed_time import FixedTimeController
from traffic_ai.perception.video_pipeline import VideoPipeline
from traffic_ai.simulation.runner import SimulationRunner


def main():
    parser = argparse.ArgumentParser(description="Generate Perception Demo Video")
    parser.add_argument("--seconds", type=int, default=60, help="Simulation duration to record")
    parser.add_argument("--fps", type=float, default=10.0, help="Video recording frame rate")
    parser.add_argument(
        "--output",
        type=str,
        default="artifacts/videos/perception_demo.mp4",
        help="Path for output mp4 video",
    )
    args = parser.parse_args()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    scenario = ScenarioConfig(name=ScenarioName.BALANCED, seed=42, duration_seconds=args.seconds)
    sim_cfg = SimulationConfig(gui=False, output_dir="data/runs")

    pipeline = VideoPipeline(output_video_path=out_path)
    ctrl = FixedTimeController()

    print(f"Generating perception video: {args.seconds} simulated seconds -> {out_path}")

    with SimulationRunner(
        scenario_config=scenario,
        controller=ctrl,
        simulation_config=sim_cfg,
        run_id="perception_demo_run",
    ) as sim:
        sim.start()

        for step_idx in range(args.seconds):
            state = sim.step()
            raw_frame = pipeline.render_virtual_scene(
                signal_string=state.signal_string,
                sim_time=state.timestamp,
            )
            annotated_frame, summary = pipeline.process_and_annotate_frame(
                raw_frame=raw_frame,
                ground_truth=state.approaches,
                sim_time=state.timestamp,
            )
            pipeline.record_frame(annotated_frame, fps=args.fps)

            if (step_idx + 1) % 15 == 0:
                print(
                    f"Frame {step_idx+1}/{args.seconds} | "
                    f"Detections: {summary.total_detections} | "
                    f"FPS: {summary.fps} | "
                    f"MAE: {summary.mean_absolute_error}"
                )

        pipeline.close()

    print(f"Perception demo video completed and saved at: {out_path}")


if __name__ == "__main__":
    main()
