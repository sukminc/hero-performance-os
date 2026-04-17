from __future__ import annotations

from uuid import uuid4

from core.memory.memory_models import MemoryUpdateCandidate
from core.memory.memory_queries import build_memory_key
from core.memory.memory_status import next_memory_status
from core.storage.models import MemoryItemRecord
from core.storage.repositories import V2Repository


def _maturity_label(evidence_count: int, status: str) -> str:
    if status in {"baseline", "active"} and evidence_count >= 3:
        return "established"
    if status in {"baseline", "active"} and evidence_count >= 2:
        return "repeated"
    return "emerging"


def _adjustment_for(memory_type: str, entity_key: str, direction: str) -> str | None:
    if memory_type == "hand_class_underperformance":
        return f"Review {entity_key} as a hand-class baseline leak candidate before the next session."
    if memory_type == "style_drift_candidate" and direction == "negative":
        return "Re-anchor baseline discipline before adapting further to this session texture."
    if memory_type == "field_distortion_candidate":
        return "Treat this field texture as context, but avoid inheriting its chaos without evidence."
    if memory_type == "contamination_risk_candidate":
        return "Look for spots where pool adaptation is turning into bad-habit absorption."
    return None


def _summary_for(memory_type: str, entity_key: str, status: str, maturity: str, explanation: str) -> str:
    return f"{memory_type} [{entity_key}] is currently {status} ({maturity}). {explanation}"


def build_memory_update_candidates(
    session_evidence_rows: list[dict],
    repository: V2Repository,
    player_id: str,
) -> list[MemoryUpdateCandidate]:
    candidates: list[MemoryUpdateCandidate] = []
    for row in session_evidence_rows:
        memory_type = str(row["evidence_type"])
        entity_key = str(row["entity_key"])
        direction = str(row["direction"])
        confidence = float(row.get("confidence") or 0.0)
        memory_key = build_memory_key(memory_type, str(row["entity_scope"]), entity_key)
        existing = repository.get_memory_item(player_id, memory_type, memory_key)
        prior_count = int(existing["evidence_count"]) if existing else 0
        next_count = prior_count + 1
        status = next_memory_status(
            evidence_count=next_count,
            confidence=confidence,
            direction=direction,
            existing_status=str(existing["status"]) if existing else None,
        )
        maturity = _maturity_label(next_count, status)
        summary = _summary_for(memory_type, entity_key, status, maturity, str(row.get("explanation") or ""))
        suggested_adjustment = _adjustment_for(memory_type, entity_key, direction) if status == "active" else None
        candidates.append(
            MemoryUpdateCandidate(
                memory_type=memory_type,
                memory_key=memory_key,
                status=status,
                confidence=max(confidence, float(existing["confidence"])) if existing and existing.get("confidence") is not None else confidence,
                summary=summary,
                suggested_adjustment=suggested_adjustment,
                memory_payload={
                    "entity_scope": row.get("entity_scope"),
                    "entity_key": entity_key,
                    "direction": direction,
                    "maturity": maturity,
                    "latest_evidence_id": row.get("id"),
                    "latest_explanation": row.get("explanation"),
                    "source_hand_ids": row.get("source_hand_ids") or [],
                },
            )
        )
    return candidates


def persist_memory_updates(
    repository: V2Repository,
    player_id: str,
    session_id: str,
    candidates: list[MemoryUpdateCandidate],
) -> list[MemoryItemRecord]:
    records: list[MemoryItemRecord] = []
    for candidate in candidates:
        existing = repository.get_memory_item(player_id, candidate.memory_type, candidate.memory_key)
        record = MemoryItemRecord(
            id=str(existing["id"]) if existing else f"memory-{uuid4()}",
            player_id=player_id,
            memory_type=candidate.memory_type,
            memory_key=candidate.memory_key,
            status=candidate.status,
            first_seen_session_id=str(existing["first_seen_session_id"]) if existing and existing.get("first_seen_session_id") else session_id,
            last_seen_session_id=session_id,
            evidence_count=(int(existing["evidence_count"]) if existing else 0) + 1,
            confidence=candidate.confidence,
            summary=candidate.summary,
            suggested_adjustment=candidate.suggested_adjustment,
            memory_payload=candidate.memory_payload,
        )
        repository.upsert_memory_item(record)
        records.append(record)
    return records


def update_memory_from_session_evidence(
    repository: V2Repository,
    player_id: str,
    session_id: str,
) -> list[MemoryItemRecord]:
    evidence_rows = repository.fetch_session_evidence(session_id)
    candidates = build_memory_update_candidates(evidence_rows, repository, player_id)
    return persist_memory_updates(repository, player_id, session_id, candidates)
