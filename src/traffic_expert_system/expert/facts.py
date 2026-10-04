from __future__ import annotations

from traffic_expert_system.domain.models import SensorFacts, SignalColor
from traffic_expert_system.simulation.state import TrafficState


def collect_facts(state: TrafficState) -> SensorFacts:
    return SensorFacts(
        current_phase=state.current_phase.id,
        phase_elapsed=state.phase_elapsed,
        min_green_passed=state.phase_elapsed >= state.current_phase.min_green,
        max_green_reached=state.phase_elapsed >= state.current_phase.max_green,
        queue_by_phase={phase.id: state.queue_length_for_phase(phase.id) for phase in state.intersection.phases},
        max_wait_by_phase={phase.id: state.max_wait_for_phase(phase.id) for phase in state.intersection.phases},
        total_queue=state.remaining_vehicles,
    )
