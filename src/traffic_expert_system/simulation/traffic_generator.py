from __future__ import annotations

import random

from traffic_expert_system.domain.models import IntersectionConfig, ScenarioConfig, Vehicle


class TrafficGenerator:
    def __init__(self, intersection: IntersectionConfig, scenario: ScenarioConfig) -> None:
        self.intersection = intersection
        self.scenario = scenario
        self.random = random.Random(scenario.seed)
        self.lanes_by_approach = {
            approach: [lane for lane in intersection.lanes if lane.approach == approach]
            for approach in intersection.approaches
        }

    def _rates_at(self, time: int) -> dict[str, float]:
        for segment in self.scenario.segments:
            if segment.start <= time < segment.end:
                return segment.arrivals_per_minute
        return {}

    def generate(self, time: int, next_vehicle_id) -> list[Vehicle]:
        vehicles: list[Vehicle] = []
        for approach, rate_per_minute in self._rates_at(time).items():
            if approach not in self.lanes_by_approach:
                continue
            if self.random.random() < rate_per_minute / 60:
                lane = self.random.choice(self.lanes_by_approach[approach])
                vehicles.append(Vehicle(id=next_vehicle_id(), lane_id=lane.id, created_at=time))
        return vehicles
