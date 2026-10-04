from __future__ import annotations

from traffic_expert_system.domain.models import Decision, SignalColor
from traffic_expert_system.expert.facts import collect_facts
from traffic_expert_system.expert.rules import Rule, default_rules
from traffic_expert_system.simulation.state import TrafficState


class InferenceEngine:
    def __init__(self, rules: tuple[Rule, ...] | None = None) -> None:
        self.rules = tuple(sorted(rules or default_rules(), key=lambda rule: rule.priority, reverse=True))

    def decide(self, state: TrafficState) -> Decision:
        if state.signal_color != SignalColor.GREEN:
            raise RuntimeError("Логический вывод выполняется только во время зеленой фазы.")
        facts = collect_facts(state)
        for rule in self.rules:
            if rule.applies(facts, state):
                return rule.make_decision(facts, state)
        raise RuntimeError("В базе правил отсутствует правило по умолчанию.")
