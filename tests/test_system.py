from __future__ import annotations

import unittest
from pathlib import Path

from traffic_expert_system.controllers.expert_controller import ExpertController
from traffic_expert_system.domain.config_loader import load_intersection, load_scenario
from traffic_expert_system.domain.models import DecisionAction
from traffic_expert_system.simulation.engine import SimulationEngine


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TrafficExpertSystemTests(unittest.TestCase):
    def setUp(self) -> None:
        self.intersection = load_intersection(PROJECT_ROOT / "configs" / "intersections" / "four_way.json")
        self.scenario = load_scenario(PROJECT_ROOT / "configs" / "scenarios" / "morning_peak.json")

    def test_intersection_configuration_is_valid(self) -> None:
        self.assertEqual(self.intersection.id, "four_way")
        self.assertEqual(len(self.intersection.phases), 2)
        self.assertEqual(set(self.intersection.approaches), {"north", "south", "east", "west"})

    def test_two_way_configuration_is_valid(self) -> None:
        two_way = load_intersection(PROJECT_ROOT / "configs" / "intersections" / "two_way.json")
        self.assertEqual(len(two_way.lanes), 2)
        self.assertEqual(len(two_way.phases), 2)

    def test_expert_switches_after_max_green(self) -> None:
        engine = SimulationEngine(self.intersection, self.scenario, ExpertController())
        engine.state.phase_elapsed = engine.state.current_phase.max_green
        decision = engine.controller.decide(engine.state)
        self.assertEqual(decision.action, DecisionAction.SWITCH)
        self.assertEqual(decision.rule_id, "max_green_reached")

    def test_simulation_records_metrics(self) -> None:
        engine = SimulationEngine(self.intersection, self.scenario, ExpertController())
        for _ in range(90):
            engine.step()
        self.assertEqual(engine.state.time, 90)
        self.assertEqual(len(engine.state.metrics.snapshots), 90)
        self.assertGreater(engine.state.metrics.max_queue, 0)

    def test_yellow_transition_can_return_to_first_phase(self) -> None:
        engine = SimulationEngine(self.intersection, self.scenario, ExpertController())
        engine.state.phase_index = 1
        engine._start_yellow("NS_GREEN")
        for _ in range(engine.state.current_phase.yellow_duration):
            engine._advance_signal()
        self.assertEqual(engine.state.phase_index, 0)


if __name__ == "__main__":
    unittest.main()
