"""Scenario management and deterministic route generation."""

import math
import random
from pathlib import Path
from typing import Dict, List, Tuple
import xml.etree.ElementTree as ET

from traffic_ai.config.schemas import (
    ScenarioConfig,
    ScenarioName,
    VehicleClassMix,
)


class ScenarioManager:
    """Generates and manages reproducible SUMO demand scenarios."""

    ROUTE_DEFINITIONS = {
        "north": {
            "right":    ("edge_n2c", "edge_c2w"),
            "straight": ("edge_n2c", "edge_c2s"),
            "left":     ("edge_n2c", "edge_c2e"),
        },
        "south": {
            "right":    ("edge_s2c", "edge_c2e"),
            "straight": ("edge_s2c", "edge_c2n"),
            "left":     ("edge_s2c", "edge_c2w"),
        },
        "east": {
            "right":    ("edge_e2c", "edge_c2n"),
            "straight": ("edge_e2c", "edge_c2w"),
            "left":     ("edge_e2c", "edge_c2s"),
        },
        "west": {
            "right":    ("edge_w2c", "edge_c2s"),
            "straight": ("edge_w2c", "edge_c2e"),
            "left":     ("edge_w2c", "edge_c2n"),
        },
    }

    @staticmethod
    def get_preset_config(scenario_name: ScenarioName, seed: int = 42, duration: int = 3600) -> ScenarioConfig:
        """Returns standard configuration for predefined benchmark scenarios."""
        cfg = ScenarioConfig(name=scenario_name, seed=seed, duration_seconds=duration)

        if scenario_name == ScenarioName.LOW:
            cfg.north_arrival_rate_vph = 180.0
            cfg.south_arrival_rate_vph = 180.0
            cfg.east_arrival_rate_vph  = 180.0
            cfg.west_arrival_rate_vph  = 180.0

        elif scenario_name == ScenarioName.BALANCED:
            cfg.north_arrival_rate_vph = 420.0
            cfg.south_arrival_rate_vph = 420.0
            cfg.east_arrival_rate_vph  = 420.0
            cfg.west_arrival_rate_vph  = 420.0

        elif scenario_name == ScenarioName.HEAVY:
            cfg.north_arrival_rate_vph = 750.0
            cfg.south_arrival_rate_vph = 750.0
            cfg.east_arrival_rate_vph  = 750.0
            cfg.west_arrival_rate_vph  = 750.0

        elif scenario_name == ScenarioName.NORTH_SOUTH_DOMINANT:
            cfg.north_arrival_rate_vph = 720.0
            cfg.south_arrival_rate_vph = 680.0
            cfg.east_arrival_rate_vph  = 160.0
            cfg.west_arrival_rate_vph  = 160.0

        elif scenario_name == ScenarioName.EAST_WEST_DOMINANT:
            cfg.north_arrival_rate_vph = 160.0
            cfg.south_arrival_rate_vph = 160.0
            cfg.east_arrival_rate_vph  = 720.0
            cfg.west_arrival_rate_vph  = 680.0

        elif scenario_name == ScenarioName.BURSTY:
            cfg.north_arrival_rate_vph = 250.0
            cfg.south_arrival_rate_vph = 250.0
            cfg.east_arrival_rate_vph  = 250.0
            cfg.west_arrival_rate_vph  = 250.0
            cfg.burst_interval_seconds = 180
            cfg.burst_multiplier = 3.0

        elif scenario_name == ScenarioName.UNSEEN_EVALUATION:
            cfg.north_arrival_rate_vph = 620.0
            cfg.south_arrival_rate_vph = 280.0
            cfg.east_arrival_rate_vph  = 480.0
            cfg.west_arrival_rate_vph  = 210.0
            cfg.turn_ratios = {
                "north": [0.25, 0.50, 0.25],
                "south": [0.15, 0.70, 0.15],
                "east":  [0.30, 0.55, 0.15],
                "west":  [0.10, 0.60, 0.30],
            }

        return cfg

    @classmethod
    def generate_routes_file(cls, config: ScenarioConfig, output_path: Path) -> Path:
        """Generates a complete, deterministic SUMO route XML file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        rng = random.Random(config.seed)

        root = ET.Element("routes")
        root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        root.set("xsi:noNamespaceSchemaLocation", "http://sumo.dlr.de/xsd/routes_file.xsd")

        # Define Vehicle Types
        vtypes = [
            ("veh_passenger", "passenger", "4.5", "1.8", "13.89", "2.6", "4.5", "#3498db"),
            ("veh_bus",       "bus",       "12.0", "2.5", "11.11", "1.6", "3.5", "#e67e22"),
            ("veh_truck",     "truck",     "8.5", "2.4", "10.00", "1.4", "3.2", "#95a5a6"),
            ("veh_motorcycle","motorcycle","2.2", "0.9", "15.00", "3.5", "5.0", "#2ecc71"),
        ]
        for v_id, v_class, v_len, v_width, max_speed, accel, decel, color in vtypes:
            vt = ET.SubElement(root, "vType")
            vt.set("id", v_id)
            vt.set("vClass", v_class)
            vt.set("length", v_len)
            vt.set("width", v_width)
            vt.set("maxSpeed", max_speed)
            vt.set("accel", accel)
            vt.set("decel", decel)
            vt.set("color", color)
            vt.set("sigma", "0.5")  # human driver imperfection

        # Helper to sample vehicle class
        def sample_vtype() -> str:
            r = rng.random()
            mix = config.vehicle_mix
            if r < mix.passenger:
                return "veh_passenger"
            elif r < mix.passenger + mix.bus:
                return "veh_bus"
            elif r < mix.passenger + mix.bus + mix.truck:
                return "veh_truck"
            else:
                return "veh_motorcycle"

        # Generate vehicle arrivals per approach
        approaches = [
            ("north", config.north_arrival_rate_vph),
            ("south", config.south_arrival_rate_vph),
            ("east",  config.east_arrival_rate_vph),
            ("west",  config.west_arrival_rate_vph),
        ]

        all_vehicles = []
        veh_counter = 0

        for approach_name, base_rate_vph in approaches:
            current_time = 0.0
            turn_probs = config.turn_ratios.get(approach_name, [0.2, 0.65, 0.15])
            norm_turn_probs = [p / sum(turn_probs) for p in turn_probs]

            while current_time < config.duration_seconds:
                # Calculate instantaneous rate (handle burstiness)
                effective_rate = base_rate_vph
                if config.name == ScenarioName.BURSTY:
                    cycle_pos = current_time % config.burst_interval_seconds
                    if cycle_pos < 45.0:  # 45-second burst phase
                        effective_rate *= config.burst_multiplier

                lam = effective_rate / 3600.0  # arrivals per second
                if lam <= 0:
                    break

                # Exponential inter-arrival time
                inter_arrival = rng.expovariate(lam)
                current_time += inter_arrival
                if current_time >= config.duration_seconds:
                    break

                # Select turn movement
                tr = rng.random()
                if tr < norm_turn_probs[0]:
                    movement = "right"
                elif tr < norm_turn_probs[0] + norm_turn_probs[1]:
                    movement = "straight"
                else:
                    movement = "left"

                edges = cls.ROUTE_DEFINITIONS[approach_name][movement]
                v_type = sample_vtype()
                veh_counter += 1

                all_vehicles.append({
                    "id": f"veh_{approach_name}_{veh_counter:05d}",
                    "depart": round(current_time, 2),
                    "type": v_type,
                    "edges": f"{edges[0]} {edges[1]}",
                    "from_edge": edges[0],
                    "to_edge": edges[1],
                })

        # Sort all vehicles deterministically by depart time
        all_vehicles.sort(key=lambda v: (v["depart"], v["id"]))

        for v in all_vehicles:
            veh_el = ET.SubElement(root, "vehicle")
            veh_el.set("id", v["id"])
            veh_el.set("type", v["type"])
            veh_el.set("depart", f"{v['depart']:.2f}")
            veh_el.set("departLane", "best")
            veh_el.set("departSpeed", "max")

            route_el = ET.SubElement(veh_el, "route")
            route_el.set("edges", v["edges"])

        tree = ET.ElementTree(root)
        ET.indent(tree, space="    ")
        tree.write(str(output_path), encoding="utf-8", xml_declaration=True)
        return output_path
