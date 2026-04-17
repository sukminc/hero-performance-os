from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from core.ingest.duplicate_guard import compute_file_hash, find_duplicate_file_id
from core.evidence.session_evidence_pipeline import build_session_evidence, persist_session_evidence
from core.memory.memory_updater import update_memory_from_session_evidence
from core.parsing.gg_parser import parse_gg_text_file
from core.parsing.hand_normalizer import normalize_hands
from core.parsing.session_builder import build_session_record
from core.storage.models import IngestFileRecord
from core.storage.repositories import V2Repository


@dataclass(slots=True)
class IngestResult:
    ingest_file_id: str
    session_id: str | None
    status: str
    duplicate_of_file_id: str | None = None
    parsed_hand_count: int = 0
    evidence_count: int = 0
    memory_count: int = 0


def _now() -> datetime:
    return datetime.now(timezone.utc)


def ingest_gg_file(path: Path, repository: V2Repository, player_id: str) -> IngestResult:
    repository.ensure_schema()
    file_hash = compute_file_hash(path)
    duplicate_of_file_id = find_duplicate_file_id(repository, file_hash)
    ingest_file_id = f"ingest-{uuid4()}"

    if duplicate_of_file_id:
        return IngestResult(
            ingest_file_id=ingest_file_id,
            session_id=None,
            status="duplicate_skipped",
            duplicate_of_file_id=duplicate_of_file_id,
            parsed_hand_count=0,
            evidence_count=0,
            memory_count=0,
        )

    repository.create_ingest_file(
        IngestFileRecord(
            id=ingest_file_id,
            player_id=player_id,
            source_type="gg_txt",
            file_hash=file_hash,
            original_filename=path.name,
            source_path=str(path),
            status="processing",
            uploaded_at=_now(),
        )
    )

    parsed_packet = parse_gg_text_file(path)
    if not parsed_packet.hands:
        repository.update_ingest_status(
            ingest_file_id,
            "failed_zero_hands",
            {"parse_quality": parsed_packet.parse_quality, "source_path": str(path)},
        )
        return IngestResult(
            ingest_file_id=ingest_file_id,
            session_id=None,
            status="failed_zero_hands",
            parsed_hand_count=0,
            evidence_count=0,
            memory_count=0,
        )

    session_id = f"session-{uuid4()}"
    session_record = build_session_record(player_id, ingest_file_id, session_id, parsed_packet)
    hand_records = normalize_hands(session_id, parsed_packet)
    evidence_candidates = build_session_evidence(hand_records)

    repository.create_session(session_record)
    repository.create_hands(hand_records)
    evidence_records = persist_session_evidence(repository, session_id, evidence_candidates)
    memory_records = update_memory_from_session_evidence(repository, player_id, session_id)
    repository.update_ingest_status(
        ingest_file_id,
        "ingested",
        {
            "parse_quality": parsed_packet.parse_quality,
            "session_id": session_id,
            "parsed_hand_count": len(hand_records),
            "evidence_count": len(evidence_records),
            "memory_count": len(memory_records),
        },
    )

    return IngestResult(
        ingest_file_id=ingest_file_id,
        session_id=session_id,
        status="ingested",
        parsed_hand_count=len(hand_records),
        evidence_count=len(evidence_records),
        memory_count=len(memory_records),
    )
