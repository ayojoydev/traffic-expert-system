from __future__ import annotations

from abc import ABC, abstractmethod

from traffic_expert_system.domain.models import Decision
from traffic_expert_system.simulation.state import TrafficState


class BaseController(ABC):
    name: str

    @abstractmethod
    def decide(self, state: TrafficState) -> Decision:
        """Return the next signal action for the current simulation state."""
