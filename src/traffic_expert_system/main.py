from __future__ import annotations

import argparse
from pathlib import Path

from traffic_expert_system.analytics.charts import create_charts
from traffic_expert_system.analytics.experiments import compare_controllers, run_controller, write_results
from traffic_expert_system.controllers.expert_controller import ExpertController
from traffic_expert_system.domain.config_loader import load_intersection, load_scenario
from traffic_expert_system.simulation.engine import SimulationEngine


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def config_path(kind: str, name: str) -> Path:
    return PROJECT_ROOT / "configs" / kind / f"{name}.json"


def run_experiment(intersection_name: str, scenario_name: str) -> list[dict[str, object]]:
    intersection = load_intersection(config_path("intersections", intersection_name))
    scenario = load_scenario(config_path("scenarios", scenario_name))
    (fixed_metrics, fixed_summary), (expert_metrics, expert_summary) = compare_controllers(intersection, scenario)
    result_dir = PROJECT_ROOT / "outputs" / f"{intersection_name}_{scenario_name}"
    write_results(result_dir, [fixed_metrics, expert_metrics], [fixed_summary, expert_summary])
    create_charts([fixed_metrics, expert_metrics], [fixed_summary, expert_summary], result_dir)
    for summary in (fixed_summary, expert_summary):
        print(summary)
    print(f"Результаты сохранены: {result_dir}")
    return [fixed_summary, expert_summary]


def main() -> None:
    parser = argparse.ArgumentParser(description="Экспертная система управления перекрестком")
    parser.add_argument("--intersection", default="four_way", choices=("two_way", "four_way"))
    parser.add_argument("--scenario", default="morning_peak", choices=("balanced", "morning_peak", "changing_flow"))
    parser.add_argument("--experiment", action="store_true", help="сравнить фиксированный и экспертный контроллеры")
    parser.add_argument("--visual", action="store_true", help="открыть Pygame-эмуляцию")
    args = parser.parse_args()

    if args.experiment:
        run_experiment(args.intersection, args.scenario)
        return

    intersection = load_intersection(config_path("intersections", args.intersection))
    scenario = load_scenario(config_path("scenarios", args.scenario))
    engine = SimulationEngine(intersection, scenario, ExpertController())
    if args.visual:
        from traffic_expert_system.visualization.pygame_view import PygameSimulationView
        PygameSimulationView(engine).run()
    else:
        state = engine.run()
        print(state.metrics.summary(state.remaining_vehicles, scenario.duration))


if __name__ == "__main__":
    main()
