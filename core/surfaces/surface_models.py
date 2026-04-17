from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TodayAdjustment:
    label: str
    reason: str
    confidence: float
    memory_id: str


@dataclass(slots=True)
class TodaySurface:
    player_id: str
    current_state: str
    headline: str
    adjustments: list[TodayAdjustment] = field(default_factory=list)
    supporting_memory: list[dict[str, Any]] = field(default_factory=list)
    confidence_summary: dict[str, Any] = field(default_factory=dict)

