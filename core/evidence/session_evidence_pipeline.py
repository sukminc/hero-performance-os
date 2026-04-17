from __future__ import annotations

from uuid import uuid4

from core.evidence.contamination_evidence import build_contamination_evidence
from core.evidence.evidence_models import EvidenceCandidate
from core.evidence.field_distortion_evidence import build_field_distortion_evidence
from core.evidence.hand_class_evidence import build_hand_class_evidence
from core.evidence.stable_strength_evidence import build_stable_strength_evidence
from core.evidence.style_drift_evidence import build_style_drift_evidence
from core.storage.models import HandRecord, SessionEvidenceRecord
from core.storage.repositories import V2Repository


def build_session_evidence(hands: list[HandRecord]) -> list[EvidenceCandidate]:
    candidates: list[EvidenceCandidate] = []
    candidates.extend(build_hand_class_evidence(hands))
    candidates.extend(build_style_drift_evidence(hands))
    candidates.extend(build_stable_strength_evidence(hands))
    candidates.extend(build_field_distortion_evidence(hands))
    candidates.extend(build_contamination_evidence(hands))
    return candidates


def persist_session_evidence(
    repository: V2Repository,
    session_id: str,
    candidates: list[EvidenceCandidate],
) -> list[SessionEvidenceRecord]:
    records = [
        SessionEvidenceRecord(
            id=f"evidence-{uuid4()}",
            session_id=session_id,
            evidence_type=candidate.evidence_type,
            entity_scope=candidate.entity_scope,
            entity_key=candidate.entity_key,
            direction=candidate.direction,
            strength_score=candidate.strength_score,
            confidence=candidate.confidence,
            sample_size=candidate.sample_size,
            explanation=candidate.explanation,
            source_hand_ids=candidate.source_hand_ids,
        )
        for candidate in candidates
    ]
    repository.create_session_evidence(records)
    return records
