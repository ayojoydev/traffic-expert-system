from __future__ import annotations

import json
from pathlib import Path

from .models import IntersectionConfig, Lane, Phase, ScenarioConfig, TrafficSegment


def _read_json(path: str | Path) -> dict:
    with Path(path).open(encoding="utf-8") as file:
        return json.load(file)


def load_intersection(path: str | Path) -> IntersectionConfig:
    raw = _read_json(path)
    lanes = tuple(Lane(**lane) for lane in raw["lanes"])
    lane_ids = {lane.id for lane in lanes}
    phases = tuple(
        Phase(
            id=phase["id"],
            allowed_lanes=tuple(phase["allowed_lanes"]),
            min_green=phase["min_green"],
            max_green=phase["max_green"],
            yellow_duration=phase["yellow_duration"],
        )
        for phase in raw["phases"]
    )
    if len(phases) < 2:
        raise ValueError("Перекресток должен иметь как минимум две фазы.")
    if any(not set(phase.allowed_lanes).issubset(lane_ids) for phase in phases):
        raise ValueError("Фаза содержит неизвестную полосу.")
    if any(phase.min_green <= 0 or phase.max_green < phase.min_green for phase in phases):
        raise ValueError("Некорректные ограничения длительности зеленого сигнала.")
    expert = raw.get("expert", {})
    return IntersectionConfig(
        id=raw["id"], name=raw["name"], lanes=lanes, phases=phases,
        wait_limit=expert.get("wait_limit", 40), queue_difference=expert.get("queue_difference", 5),
    )


def load_scenario(path: str | Path) -> ScenarioConfig:
    raw = _read_json(path)
    segments = tuple(TrafficSegment(**segment) for segment in raw["segments"])
    if not segments or any(segment.start >= segment.end for segment in segments):
        raise ValueError("Сценарий должен содержать корректные временные сегменты.")
    return ScenarioConfig(id=raw["id"], duration=raw["duration"], seed=raw["seed"], segments=segments)
