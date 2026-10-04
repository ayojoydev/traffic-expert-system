from __future__ import annotations

import csv
import json
from pathlib import Path

from traffic_expert_system.controllers.expert_controller import ExpertController
from traffic_expert_system.controllers.fixed_time import FixedTimeController
from traffic_expert_system.simulation.engine import SimulationEngine


def run_controller(intersection, scenario, controller):
    engine = SimulationEngine(intersection, scenario, controller)
    state = engine.run()
    return state.metrics, state.metrics.summary(state.remaining_vehicles, scenario.duration)


def compare_controllers(intersection, scenario):
    fixed_metrics, fixed_summary = run_controller(intersection, scenario, FixedTimeController())
    expert_metrics, expert_summary = run_controller(intersection, scenario, ExpertController())
    baseline = fixed_summary["average_wait_seconds"]
    expert_summary["wait_improvement_percent"] = round(
        (baseline - expert_summary["average_wait_seconds"]) * 100 / baseline, 2
    ) if baseline else 0.0
    fixed_summary["wait_improvement_percent"] = 0.0
    return (fixed_metrics, fixed_summary), (expert_metrics, expert_summary)


def write_results(output_dir: str | Path, metrics, summaries: list[dict[str, object]]) -> None:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    with (output_path / "summary.json").open("w", encoding="utf-8") as file:
        json.dump(summaries, file, ensure_ascii=False, indent=2)
    with (output_path / "summary.csv").open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(summaries[0]))
        writer.writeheader()
        writer.writerows(summaries)
    for metric in metrics:
        if not metric.snapshots:
            continue
        with (output_path / f"timeline_{metric.controller}_{metric.scenario}.csv").open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=list(metric.snapshots[0]))
            writer.writeheader()
            writer.writerows(metric.snapshots)
