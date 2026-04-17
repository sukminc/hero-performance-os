from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.storage.models import (
    HandRecord,
    IngestFileRecord,
    MemoryItemRecord,
    OperatorReviewRecord,
    SessionEvidenceRecord,
    SessionRecord,
)
from core.storage.postgres import get_db_connection


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PostgresV2Repository:
    def ensure_schema(self) -> None:
        schema_path = Path(__file__).with_name("schema.sql")
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE SCHEMA IF NOT EXISTS core;")
                cur.execute("CREATE SCHEMA IF NOT EXISTS operator;")
                cur.execute(schema_path.read_text(encoding="utf-8"))
            conn.commit()

    def get_ingest_file_by_hash(self, file_hash: str) -> dict[str, Any] | None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, player_id, source_type, file_hash, original_filename, status, duplicate_of_file_id
                    FROM core.ingest_files
                    WHERE file_hash = %s
                    ORDER BY uploaded_at DESC
                    LIMIT 1
                    """,
                    (file_hash,),
                )
                row = cur.fetchone()
            conn.commit()
        return dict(row) if row else None

    def create_ingest_file(self, record: IngestFileRecord) -> None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO core.ingest_files (
                        id, player_id, source_type, file_hash, original_filename, source_path,
                        status, duplicate_of_file_id, raw_metadata, uploaded_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
                    """,
                    (
                        record.id,
                        record.player_id,
                        record.source_type,
                        record.file_hash,
                        record.original_filename,
                        record.source_path,
                        record.status,
                        record.duplicate_of_file_id,
                        json.dumps(record.raw_metadata),
                        record.uploaded_at,
                        _now(),
                    ),
                )
            conn.commit()

    def update_ingest_status(self, ingest_file_id: str, status: str, raw_metadata: dict[str, Any] | None = None) -> None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if raw_metadata is None:
                    cur.execute(
                        "UPDATE core.ingest_files SET status = %s, updated_at = %s WHERE id = %s",
                        (status, _now(), ingest_file_id),
                    )
                else:
                    cur.execute(
                        """
                        UPDATE core.ingest_files
                        SET status = %s, raw_metadata = %s::jsonb, updated_at = %s
                        WHERE id = %s
                        """,
                        (status, json.dumps(raw_metadata), _now(), ingest_file_id),
                    )
            conn.commit()

    def create_session(self, record: SessionRecord) -> None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO core.sessions (
                        id, player_id, ingest_file_id, session_key, started_at, ended_at, site,
                        buyin_band, currency, parse_status, hand_count, confidence_summary,
                        session_metadata, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s)
                    """,
                    (
                        record.id,
                        record.player_id,
                        record.ingest_file_id,
                        record.session_key,
                        record.started_at,
                        record.ended_at,
                        record.site,
                        record.buyin_band,
                        record.currency,
                        record.parse_status,
                        record.hand_count,
                        json.dumps(record.confidence_summary),
                        json.dumps(record.session_metadata),
                        _now(),
                        _now(),
                    ),
                )
            conn.commit()

    def fetch_session(self, session_id: str) -> dict[str, Any] | None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id, player_id, ingest_file_id, session_key, started_at, ended_at, site,
                        buyin_band, currency, parse_status, hand_count, confidence_summary, session_metadata
                    FROM core.sessions
                    WHERE id = %s
                    LIMIT 1
                    """,
                    (session_id,),
                )
                row = cur.fetchone()
            conn.commit()
        return dict(row) if row else None

    def fetch_hands_for_session(self, session_id: str, limit: int = 20) -> list[dict[str, Any]]:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id, session_id, hand_external_id, tournament_id, hero_position,
                        effective_stack_bb, phase_proxy, bounty_proxy, players_to_flop,
                        board_texture_summary, result_summary, header_metadata
                    FROM core.hands
                    WHERE session_id = %s
                    ORDER BY created_at, id
                    LIMIT %s
                    """,
                    (session_id, limit),
                )
                rows = cur.fetchall() or []
            conn.commit()
        return [dict(row) for row in rows]

    def create_hands(self, hands: list[HandRecord]) -> None:
        if not hands:
            return
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for hand in hands:
                    cur.execute(
                        """
                        INSERT INTO core.hands (
                            id, session_id, hand_external_id, tournament_id, hero_position,
                            effective_stack_bb, phase_proxy, bounty_proxy, players_to_flop,
                            board_texture_summary, result_summary, header_metadata, raw_payload,
                            created_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::jsonb, %s::jsonb, %s)
                        """,
                        (
                            hand.id,
                            hand.session_id,
                            hand.hand_external_id,
                            hand.tournament_id,
                            hand.hero_position,
                            hand.effective_stack_bb,
                            hand.phase_proxy,
                            hand.bounty_proxy,
                            hand.players_to_flop,
                            hand.board_texture_summary,
                            json.dumps(hand.result_summary),
                            json.dumps(hand.header_metadata),
                            json.dumps(hand.raw_payload),
                            _now(),
                        ),
                    )
            conn.commit()

    def create_session_evidence(self, evidence_rows: list[SessionEvidenceRecord]) -> None:
        if not evidence_rows:
            return
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for row in evidence_rows:
                    cur.execute(
                        """
                        INSERT INTO core.session_evidence (
                            id, session_id, evidence_type, entity_scope, entity_key, direction,
                            strength_score, confidence, sample_size, explanation, source_hand_ids, created_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                        """,
                        (
                            row.id,
                            row.session_id,
                            row.evidence_type,
                            row.entity_scope,
                            row.entity_key,
                            row.direction,
                            row.strength_score,
                            row.confidence,
                            row.sample_size,
                            row.explanation,
                            json.dumps(row.source_hand_ids),
                            _now(),
                        ),
                    )
            conn.commit()

    def fetch_session_evidence(self, session_id: str) -> list[dict[str, Any]]:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id, session_id, evidence_type, entity_scope, entity_key, direction,
                        strength_score, confidence, sample_size, explanation, source_hand_ids
                    FROM core.session_evidence
                    WHERE session_id = %s
                    ORDER BY created_at, id
                    """,
                    (session_id,),
                )
                rows = cur.fetchall() or []
            conn.commit()
        return [dict(row) for row in rows]

    def get_memory_item(self, player_id: str, memory_type: str, memory_key: str) -> dict[str, Any] | None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id, player_id, memory_type, memory_key, status, first_seen_session_id,
                        last_seen_session_id, evidence_count, confidence, summary,
                        suggested_adjustment, memory_payload
                    FROM core.memory_items
                    WHERE player_id = %s AND memory_type = %s AND memory_key = %s
                    LIMIT 1
                    """,
                    (player_id, memory_type, memory_key),
                )
                row = cur.fetchone()
            conn.commit()
        return dict(row) if row else None

    def upsert_memory_item(self, record: MemoryItemRecord) -> None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO core.memory_items (
                        id, player_id, memory_type, memory_key, status, first_seen_session_id,
                        last_seen_session_id, evidence_count, confidence, summary,
                        suggested_adjustment, memory_payload, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
                    ON CONFLICT (player_id, memory_type, memory_key)
                    DO UPDATE SET
                        status = EXCLUDED.status,
                        first_seen_session_id = COALESCE(core.memory_items.first_seen_session_id, EXCLUDED.first_seen_session_id),
                        last_seen_session_id = EXCLUDED.last_seen_session_id,
                        evidence_count = EXCLUDED.evidence_count,
                        confidence = EXCLUDED.confidence,
                        summary = EXCLUDED.summary,
                        suggested_adjustment = EXCLUDED.suggested_adjustment,
                        memory_payload = EXCLUDED.memory_payload,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (
                        record.id,
                        record.player_id,
                        record.memory_type,
                        record.memory_key,
                        record.status,
                        record.first_seen_session_id,
                        record.last_seen_session_id,
                        record.evidence_count,
                        record.confidence,
                        record.summary,
                        record.suggested_adjustment,
                        json.dumps(record.memory_payload),
                        _now(),
                        _now(),
                    ),
                )
            conn.commit()

    def fetch_memory_items(self, player_id: str, statuses: list[str] | None = None) -> list[dict[str, Any]]:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if statuses:
                    cur.execute(
                        """
                        SELECT
                            id, player_id, memory_type, memory_key, status, first_seen_session_id,
                            last_seen_session_id, evidence_count, confidence, summary,
                            suggested_adjustment, memory_payload
                        FROM core.memory_items
                        WHERE player_id = %s AND status = ANY(%s)
                        ORDER BY
                            CASE status
                                WHEN 'active' THEN 1
                                WHEN 'baseline' THEN 2
                                WHEN 'watch' THEN 3
                                WHEN 'resolved' THEN 4
                                ELSE 5
                            END,
                            evidence_count DESC,
                            confidence DESC NULLS LAST,
                            updated_at DESC
                        """,
                        (player_id, statuses),
                    )
                else:
                    cur.execute(
                        """
                        SELECT
                            id, player_id, memory_type, memory_key, status, first_seen_session_id,
                            last_seen_session_id, evidence_count, confidence, summary,
                            suggested_adjustment, memory_payload
                        FROM core.memory_items
                        WHERE player_id = %s
                        ORDER BY
                            CASE status
                                WHEN 'active' THEN 1
                                WHEN 'baseline' THEN 2
                                WHEN 'watch' THEN 3
                                WHEN 'resolved' THEN 4
                                ELSE 5
                            END,
                            evidence_count DESC,
                            confidence DESC NULLS LAST,
                            updated_at DESC
                        """,
                        (player_id,),
                    )
                rows = cur.fetchall() or []
            conn.commit()
        return [dict(row) for row in rows]

    def create_surface_snapshot(
        self,
        snapshot_id: str,
        player_id: str,
        session_id: str | None,
        surface_type: str,
        payload: dict[str, Any],
        confidence_summary: dict[str, Any],
    ) -> None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO core.surface_snapshots (
                        id, player_id, session_id, surface_type, payload, confidence_summary, generated_at
                    )
                    VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s)
                    """,
                    (
                        snapshot_id,
                        player_id,
                        session_id,
                        surface_type,
                        json.dumps(payload),
                        json.dumps(confidence_summary),
                        _now(),
                    ),
                )
            conn.commit()

    def fetch_latest_surface_snapshot(self, player_id: str, surface_type: str) -> dict[str, Any] | None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id, player_id, session_id, surface_type, payload, confidence_summary, generated_at
                    FROM core.surface_snapshots
                    WHERE player_id = %s AND surface_type = %s
                    ORDER BY generated_at DESC, id DESC
                    LIMIT 1
                    """,
                    (player_id, surface_type),
                )
                row = cur.fetchone()
            conn.commit()
        return dict(row) if row else None

    def fetch_latest_session_id(self, player_id: str) -> str | None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id
                    FROM core.sessions
                    WHERE player_id = %s
                    ORDER BY created_at DESC, id DESC
                    LIMIT 1
                    """,
                    (player_id,),
                )
                row = cur.fetchone()
            conn.commit()
        return str(row["id"]) if row else None

    def fetch_memory_items_for_session(self, player_id: str, session_id: str) -> list[dict[str, Any]]:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id, player_id, memory_type, memory_key, status, first_seen_session_id,
                        last_seen_session_id, evidence_count, confidence, summary,
                        suggested_adjustment, memory_payload
                    FROM core.memory_items
                    WHERE player_id = %s AND last_seen_session_id = %s
                    ORDER BY
                        CASE status
                            WHEN 'active' THEN 1
                            WHEN 'baseline' THEN 2
                            WHEN 'watch' THEN 3
                            WHEN 'resolved' THEN 4
                            ELSE 5
                        END,
                        evidence_count DESC,
                        confidence DESC NULLS LAST,
                        updated_at DESC
                    """,
                    (player_id, session_id),
                )
                rows = cur.fetchall() or []
            conn.commit()
        return [dict(row) for row in rows]

    def create_operator_review(self, record: OperatorReviewRecord) -> None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO operator.operator_reviews (
                        id, target_type, target_id, review_type, decision, notes, review_payload, created_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s::jsonb, %s)
                    """,
                    (
                        record.id,
                        record.target_type,
                        record.target_id,
                        record.review_type,
                        record.decision,
                        record.notes,
                        json.dumps(record.review_payload),
                        record.created_at or _now(),
                    ),
                )
            conn.commit()

    def fetch_operator_reviews(self, target_type: str, target_id: str, review_type: str | None = None) -> list[dict[str, Any]]:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if review_type is None:
                    cur.execute(
                        """
                        SELECT id, target_type, target_id, review_type, decision, notes, review_payload, created_at
                        FROM operator.operator_reviews
                        WHERE target_type = %s AND target_id = %s
                        ORDER BY created_at DESC, id DESC
                        """,
                        (target_type, target_id),
                    )
                else:
                    cur.execute(
                        """
                        SELECT id, target_type, target_id, review_type, decision, notes, review_payload, created_at
                        FROM operator.operator_reviews
                        WHERE target_type = %s AND target_id = %s AND review_type = %s
                        ORDER BY created_at DESC, id DESC
                        """,
                        (target_type, target_id, review_type),
                    )
                rows = cur.fetchall() or []
            conn.commit()
        return [dict(row) for row in rows]
