from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
from uuid import uuid4

from core.ingest.duplicate_guard import compute_file_hash, find_duplicate_file_id
from core.evidence.session_evidence_pipeline import build_session_evidence, persist_session_evidence
from core.memory.memory_updater import update_memory_from_session_evidence
from core.parsing.gg_parser import parse_gg_text_file
from core.parsing.hand_normalizer import normalize_hands
from core.parsing.session_builder import build_session_record
from core.storage.models import IngestFileRecord, TournamentResultRecord
from core.storage.repositories import V2Repository


@dataclass(slots=True)
class IngestResult:
    ingest_file_id: str
    session_id: str | None
    status: str
    duplicate_of_file_id: str | None = None
    duplicate_of_status: str | None = None
    parsed_hand_count: int = 0
    evidence_count: int = 0
    memory_count: int = 0


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _summary_result_record(
    *,
    player_id: str,
    ingest_file_id: str,
    metadata: dict,
) -> TournamentResultRecord | None:
    tournament_id = str(metadata.get("tournament_id") or "").strip()
    if not tournament_id:
        return None
    return TournamentResultRecord(
        id=f"tournament-result-{uuid4()}",
        player_id=player_id,
        tournament_id=tournament_id,
        source_ingest_file_id=ingest_file_id,
        site="gg",
        title=str(metadata.get("title") or "").strip() or None,
        started_at=str(metadata.get("tournament_started_at") or "").strip() or None,
        buy_in=str(metadata.get("buy-in") or "").strip() or None,
        player_count=int(metadata["player_count"]) if metadata.get("player_count") is not None else None,
        prize_pool=str(metadata.get("total prize pool") or "").strip() or None,
        finish_place=str(metadata.get("finish_place") or "").strip() or None,
        total_received=str(metadata.get("total_received") or "").strip() or None,
        result_payload={
            "source": "gg_tournament_summary",
            "summary_format": bool(metadata.get("summary_format")),
            "hero_result_line": metadata.get("hero_result_line"),
            "raw_metadata": metadata,
        },
    )


def ingest_gg_file(path: Path, repository: V2Repository, player_id: str) -> IngestResult:
    repository.ensure_schema()
    file_hash = compute_file_hash(path)
    duplicate_of_file_id = find_duplicate_file_id(repository, file_hash)
    ingest_file_id = f"ingest-{uuid4()}"

    if duplicate_of_file_id:
        existing = repository.get_ingest_file_by_id(duplicate_of_file_id)
        if existing and str(existing.get("status") or "") == "skipped_summary_only":
            parsed_packet = parse_gg_text_file(path)
            official_result = _summary_result_record(
                player_id=player_id,
                ingest_file_id=str(existing.get("id") or duplicate_of_file_id),
                metadata=parsed_packet.metadata,
            )
            if official_result is not None:
                repository.upsert_tournament_result(official_result)
        return IngestResult(
            ingest_file_id=ingest_file_id,
            session_id=None,
            status="duplicate_skipped",
            duplicate_of_file_id=duplicate_of_file_id,
            duplicate_of_status=str(existing.get("status")) if existing else None,
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
        parse_mode = parsed_packet.parse_quality.get("parser_mode")
        ingest_status = "skipped_summary_only" if parse_mode == "tournament_summary_only" else "failed_zero_hands"
        official_result = _summary_result_record(
            player_id=player_id,
            ingest_file_id=ingest_file_id,
            metadata=parsed_packet.metadata,
        )
        if official_result is not None and ingest_status == "skipped_summary_only":
            repository.upsert_tournament_result(official_result)
        repository.update_ingest_status(
            ingest_file_id,
            ingest_status,
            {
                "parse_quality": parsed_packet.parse_quality,
                "source_path": str(path),
                "official_tournament_result_id": official_result.id if official_result else None,
            },
        )
        return IngestResult(
            ingest_file_id=ingest_file_id,
            session_id=None,
            status=ingest_status,
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
