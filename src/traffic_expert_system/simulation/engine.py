from __future__ import annotations

from traffic_expert_system.controllers.base import BaseController
from traffic_expert_system.domain.models import DecisionAction, ScenarioConfig, SignalColor
from traffic_expert_system.simulation.state import TrafficState
from traffic_expert_system.simulation.traffic_generator import TrafficGenerator


class SimulationEngine:
    def __init__(self, intersection, scenario: ScenarioConfig, controller: BaseController) -> None:
        self.intersection = intersection
        self.scenario = scenario
        self.controller = controller
        self.state = TrafficState(intersection, controller.name, scenario.id)
        self.generator = TrafficGenerator(intersection, scenario)

    @property
    def finished(self) -> bool:
        return self.state.time >= self.scenario.duration

    def _next_vehicle_id(self) -> int:
        self.state.vehicle_sequence += 1
        return self.state.vehicle_sequence

    def _add_arrivals(self) -> None:
        for vehicle in self.generator.generate(self.state.time, self._next_vehicle_id):
            self.state.queues[vehicle.lane_id].append(vehicle)

    def _start_yellow(self, target_phase: str) -> None:
        self.state.signal_color = SignalColor.YELLOW
        self.state.phase_elapsed = 0
        self.state.yellow_target_index = self.state.phase_index_by_id(target_phase)
        self.state.metrics.phase_changes += 1

    def _advance_signal(self) -> None:
        if self.state.signal_color == SignalColor.YELLOW:
            self.state.phase_elapsed += 1
            if self.state.phase_elapsed >= self.state.current_phase.yellow_duration:
                self.state.phase_index = (
                    self.state.yellow_target_index
                    if self.state.yellow_target_index is not None
                    else self.state.next_phase_index()
                )
                self.state.signal_color = SignalColor.GREEN
                self.state.phase_elapsed = 0
                self.state.yellow_target_index = None
            return

        decision = self.controller.decide(self.state)
        self.state.last_decision = decision
        if decision.action == DecisionAction.SWITCH and decision.target_phase and decision.target_phase != self.state.current_phase.id:
            self._start_yellow(decision.target_phase)

    def _serve_vehicles(self) -> None:
        if self.state.signal_color != SignalColor.GREEN:
            return
        for lane_id in self.state.current_phase.allowed_lanes:
            lane = self.intersection.lane_by_id[lane_id]
            queue = self.state.queues[lane_id]
            for _ in range(min(lane.service_rate, len(queue))):
                vehicle = queue.popleft()
                self.state.metrics.served_vehicles += 1
                self.state.metrics.total_wait += vehicle.wait_time
                self.state.metrics.max_wait = max(self.state.metrics.max_wait, vehicle.wait_time)

    def _increase_waits(self) -> None:
        for queue in self.state.queues.values():
            for vehicle in queue:
                vehicle.wait_time += 1

    def _record_snapshot(self) -> None:
        queues = self.state.queue_length_by_approach()
        row: dict[str, object] = {
            "time": self.state.time,
            "phase": self.state.current_phase.id,
            "color": self.state.signal_color.value,
            "served_vehicles": self.state.metrics.served_vehicles,
            "total_queue": self.state.remaining_vehicles,
            "rule_id": self.state.last_decision.rule_id if self.state.last_decision else "yellow_transition",
        }
        row.update({f"queue_{approach}": count for approach, count in queues.items()})
        self.state.metrics.snapshots.append(row)
        self.state.metrics.max_queue = max(self.state.metrics.max_queue, self.state.remaining_vehicles)

    def step(self) -> TrafficState:
        if self.finished:
            return self.state
        self._add_arrivals()
        self._advance_signal()
        self._serve_vehicles()
        self._increase_waits()
        self._record_snapshot()
        if self.state.signal_color == SignalColor.GREEN:
            self.state.phase_elapsed += 1
        self.state.time += 1
        return self.state

    def run(self) -> TrafficState:
        while not self.finished:
            self.step()
        return self.state
