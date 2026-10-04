from __future__ import annotations

from collections import deque

from traffic_expert_system.domain.models import (
    IntersectionConfig,
    RunMetrics,
    SignalColor,
    Vehicle,
)


class TrafficState:
    def __init__(self, intersection: IntersectionConfig, controller_name: str, scenario_id: str) -> None:
        self.intersection = intersection
        self.time = 0
        self.phase_index = 0
        self.signal_color = SignalColor.GREEN
        self.phase_elapsed = 0
        self.yellow_target_index: int | None = None
        self.queues: dict[str, deque[Vehicle]] = {lane.id: deque() for lane in intersection.lanes}
        self.vehicle_sequence = 0
        self.last_decision = None
        self.metrics = RunMetrics(controller=controller_name, scenario=scenario_id, intersection=intersection.id)

    @property
    def current_phase(self):
        return self.intersection.phases[self.phase_index]

    @property
    def remaining_vehicles(self) -> int:
        return sum(len(queue) for queue in self.queues.values())

    def next_phase_index(self) -> int:
        return (self.phase_index + 1) % len(self.intersection.phases)

    def phase_by_id(self, phase_id: str):
        return next(phase for phase in self.intersection.phases if phase.id == phase_id)

    def phase_index_by_id(self, phase_id: str) -> int:
        return next(index for index, phase in enumerate(self.intersection.phases) if phase.id == phase_id)

    def queue_length_for_phase(self, phase_id: str) -> int:
        phase = self.phase_by_id(phase_id)
        return sum(len(self.queues[lane_id]) for lane_id in phase.allowed_lanes)

    def max_wait_for_phase(self, phase_id: str) -> int:
        phase = self.phase_by_id(phase_id)
        waits = [vehicle.wait_time for lane_id in phase.allowed_lanes for vehicle in self.queues[lane_id]]
        return max(waits, default=0)

    def queue_length_by_approach(self) -> dict[str, int]:
        totals = {approach: 0 for approach in self.intersection.approaches}
        for lane in self.intersection.lanes:
            totals[lane.approach] += len(self.queues[lane.id])
        return totals

    def describe_queues(self) -> str:
        return ", ".join(f"{approach}: {count}" for approach, count in self.queue_length_by_approach().items())
