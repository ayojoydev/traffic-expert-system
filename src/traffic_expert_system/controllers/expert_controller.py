from __future__ import annotations

from traffic_expert_system.controllers.base import BaseController
from traffic_expert_system.domain.models import Decision
from traffic_expert_system.expert.inference import InferenceEngine
from traffic_expert_system.simulation.state import TrafficState


class ExpertController(BaseController):
    name = "expert"

    def __init__(self, inference_engine: InferenceEngine | None = None) -> None:
        self.inference_engine = inference_engine or InferenceEngine()

    def decide(self, state: TrafficState) -> Decision:
        return self.inference_engine.decide(state)
