from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class SignalColor(StrEnum):
    GREEN = "green"
    YELLOW = "yellow"


class DecisionAction(StrEnum):
    KEEP = "keep"
    SWITCH = "switch"


@dataclass(frozen=True)
class Lane:
    id: str
    approach: str
    service_rate: int = 1


@dataclass(frozen=True)
class Phase:
    id: str
    allowed_lanes: tuple[str, ...]
    min_green: int
    max_green: int
    yellow_duration: int


@dataclass(frozen=True)
class IntersectionConfig:
    id: str
    name: str
    lanes: tuple[Lane, ...]
    phases: tuple[Phase, ...]
    wait_limit: int = 40
    queue_difference: int = 5

    @property
    def lane_by_id(self) -> dict[str, Lane]:
        return {lane.id: lane for lane in self.lanes}

    @property
    def approaches(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(lane.approach for lane in self.lanes))


@dataclass(frozen=True)
class TrafficSegment:
    start: int
    end: int
    arrivals_per_minute: dict[str, float]


@dataclass(frozen=True)
class ScenarioConfig:
    id: str
    duration: int
    seed: int
    segments: tuple[TrafficSegment, ...]


@dataclass
class Vehicle:
    id: int
    lane_id: str
    created_at: int
    wait_time: int = 0


@dataclass(frozen=True)
class Decision:
    action: DecisionAction
    target_phase: str | None
    rule_id: str
    explanation: str


@dataclass(frozen=True)
class SensorFacts:
    current_phase: str
    phase_elapsed: int
    min_green_passed: bool
    max_green_reached: bool
    queue_by_phase: dict[str, int]
    max_wait_by_phase: dict[str, int]
    total_queue: int


@dataclass
class RunMetrics:
    controller: str
    scenario: str
    intersection: str
    served_vehicles: int = 0
    total_wait: int = 0
    max_wait: int = 0
    max_queue: int = 0
    phase_changes: int = 0
    snapshots: list[dict[str, object]] = field(default_factory=list)

    def summary(self, remaining_vehicles: int, duration: int) -> dict[str, object]:
        return {
            "controller": self.controller,
            "scenario": self.scenario,
            "intersection": self.intersection,
            "duration_seconds": duration,
            "served_vehicles": self.served_vehicles,
            "remaining_vehicles": remaining_vehicles,
            "average_wait_seconds": round(self.total_wait / self.served_vehicles, 2) if self.served_vehicles else 0.0,
            "max_wait_seconds": self.max_wait,
            "max_queue": self.max_queue,
            "phase_changes": self.phase_changes,
            "throughput_per_minute": round(self.served_vehicles * 60 / duration, 2) if duration else 0.0,
        }
