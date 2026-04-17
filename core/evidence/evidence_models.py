from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class EvidenceCandidate:
    evidence_type: str
    entity_scope: str
    entity_key: str
    direction: str
    strength_score: float | None
    confidence: float | None
    sample_size: int | None
    explanation: str
    source_hand_ids: list[str] = field(default_factory=list)

