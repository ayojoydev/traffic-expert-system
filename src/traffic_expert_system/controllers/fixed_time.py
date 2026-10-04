from __future__ import annotations

from traffic_expert_system.controllers.base import BaseController
from traffic_expert_system.domain.models import Decision, DecisionAction
from traffic_expert_system.simulation.state import TrafficState


class FixedTimeController(BaseController):
    name = "fixed_time"

    def __init__(self, green_duration: int = 25) -> None:
        self.green_duration = green_duration

    def decide(self, state: TrafficState) -> Decision:
        if state.phase_elapsed >= self.green_duration:
            target = state.intersection.phases[state.next_phase_index()].id
            return Decision(
                action=DecisionAction.SWITCH,
                target_phase=target,
                rule_id="fixed_cycle",
                explanation=f"Фиксированный цикл: фаза длится {self.green_duration} с.",
            )
        return Decision(
            action=DecisionAction.KEEP,
            target_phase=None,
            rule_id="fixed_cycle",
            explanation="Фиксированный цикл продолжается.",
        )
