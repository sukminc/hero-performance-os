from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class MemoryUpdateCandidate:
    memory_type: str
    memory_key: str
    status: str
    confidence: float
    summary: str
    suggested_adjustment: str | None
    memory_payload: dict[str, Any] = field(default_factory=dict)

