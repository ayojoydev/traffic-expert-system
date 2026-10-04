from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from traffic_expert_system.domain.models import Decision, DecisionAction, SensorFacts
from traffic_expert_system.simulation.state import TrafficState


@dataclass(frozen=True)
class Rule:
    id: str
    priority: int
    applies: Callable[[SensorFacts, TrafficState], bool]
    make_decision: Callable[[SensorFacts, TrafficState], Decision]


def best_alternative_phase(facts: SensorFacts, state: TrafficState) -> str:
    alternatives = [phase.id for phase in state.intersection.phases if phase.id != facts.current_phase]
    return max(
        alternatives,
        key=lambda phase_id: (facts.max_wait_by_phase[phase_id], facts.queue_by_phase[phase_id]),
    )


def _switch(rule_id: str, explanation: Callable[[SensorFacts, TrafficState, str], str]):
    def decision(facts: SensorFacts, state: TrafficState) -> Decision:
        target = best_alternative_phase(facts, state)
        return Decision(DecisionAction.SWITCH, target, rule_id, explanation(facts, state, target))
    return decision


def default_rules() -> tuple[Rule, ...]:
    return (
        Rule(
            id="max_green_reached",
            priority=100,
            applies=lambda facts, state: facts.max_green_reached,
            make_decision=_switch(
                "max_green_reached",
                lambda facts, state, target: (
                    f"Фаза {facts.current_phase} достигла максимальной длительности "
                    f"{state.current_phase.max_green} с; переход к {target}."
                ),
            ),
        ),
        Rule(
            id="excessive_wait",
            priority=90,
            applies=lambda facts, state: facts.min_green_passed and any(
                facts.max_wait_by_phase[phase.id] >= state.intersection.wait_limit
                for phase in state.intersection.phases if phase.id != facts.current_phase
            ),
            make_decision=_switch(
                "excessive_wait",
                lambda facts, state, target: (
                    f"Ожидание в фазе {target}: {facts.max_wait_by_phase[target]} с; "
                    f"лимит {state.intersection.wait_limit} с превышен."
                ),
            ),
        ),
        Rule(
            id="current_phase_empty",
            priority=80,
            applies=lambda facts, state: facts.min_green_passed and facts.queue_by_phase[facts.current_phase] == 0 and any(
                facts.queue_by_phase[phase.id] > 0 for phase in state.intersection.phases if phase.id != facts.current_phase
            ),
            make_decision=_switch(
                "current_phase_empty",
                lambda facts, state, target: f"В текущей фазе нет машин; очередь фазы {target}: {facts.queue_by_phase[target]}.",
            ),
        ),
        Rule(
            id="queue_imbalance",
            priority=70,
            applies=lambda facts, state: facts.min_green_passed and (
                max(facts.queue_by_phase[phase.id] for phase in state.intersection.phases if phase.id != facts.current_phase)
                >= facts.queue_by_phase[facts.current_phase] + state.intersection.queue_difference
            ),
            make_decision=_switch(
                "queue_imbalance",
                lambda facts, state, target: (
                    f"Очередь {target} ({facts.queue_by_phase[target]}) существенно больше "
                    f"текущей ({facts.queue_by_phase[facts.current_phase]})."
                ),
            ),
        ),
        Rule(
            id="keep_phase",
            priority=0,
            applies=lambda facts, state: True,
            make_decision=lambda facts, state: Decision(
                DecisionAction.KEEP,
                None,
                "keep_phase",
                "Оснований для смены фазы нет; текущий зеленый сигнал сохраняется.",
            ),
        ),
    )
