from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from core.storage.models import (
    DemoApplicationRecord,
    HandRecord,
    IngestFileRecord,
    MemoryItemRecord,
    OperatorReviewRecord,
    SessionEvidenceRecord,
    SessionRecord,
    TournamentResultRecord,
    UserAccountRecord,
    UserGlobalRoleRecord,
    UserPlayerAccessRecord,
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

    def fetch_session_by_tournament_id(self, player_id: str, tournament_id: str) -> dict[str, Any] | None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id, player_id, ingest_file_id, session_key, started_at, ended_at, site,
                        buyin_band, currency, parse_status, hand_count, confidence_summary, session_metadata
                    FROM core.sessions
                    WHERE player_id = %s AND session_metadata->>'tournament_id' = %s
                    ORDER BY hand_count DESC, created_at DESC
                    LIMIT 1
                    """,
                    (player_id, tournament_id),
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
                        board_texture_summary, result_summary, header_metadata, raw_payload
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

    def fetch_hands_for_player(self, player_id: str, limit: int = 50000) -> list[dict[str, Any]]:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        h.id, h.session_id, h.hand_external_id, h.tournament_id, h.hero_position,
                        h.effective_stack_bb, h.phase_proxy, h.bounty_proxy, h.players_to_flop,
                        h.board_texture_summary, h.result_summary, h.header_metadata, h.raw_payload,
                        s.buyin_band, s.session_metadata
                    FROM core.hands h
                    JOIN core.sessions s ON s.id = h.session_id
                    WHERE s.player_id = %s
                    ORDER BY h.created_at, h.id
                    LIMIT %s
                    """,
                    (player_id, limit),
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

    def upsert_tournament_result(self, record: TournamentResultRecord) -> None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO core.tournament_results (
                        id, player_id, tournament_id, source_ingest_file_id, site, title,
                        started_at, buy_in, player_count, prize_pool, finish_place,
                        total_received, result_payload, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
                    ON CONFLICT (player_id, tournament_id)
                    DO UPDATE SET
                        source_ingest_file_id = EXCLUDED.source_ingest_file_id,
                        site = EXCLUDED.site,
                        title = EXCLUDED.title,
                        started_at = EXCLUDED.started_at,
                        buy_in = EXCLUDED.buy_in,
                        player_count = EXCLUDED.player_count,
                        prize_pool = EXCLUDED.prize_pool,
                        finish_place = EXCLUDED.finish_place,
                        total_received = EXCLUDED.total_received,
                        result_payload = EXCLUDED.result_payload,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (
                        record.id,
                        record.player_id,
                        record.tournament_id,
                        record.source_ingest_file_id,
                        record.site,
                        record.title,
                        record.started_at,
                        record.buy_in,
                        record.player_count,
                        record.prize_pool,
                        record.finish_place,
                        record.total_received,
                        json.dumps(record.result_payload),
                        _now(),
                        _now(),
                    ),
                )
            conn.commit()

    def get_tournament_result(self, player_id: str, tournament_id: str) -> dict[str, Any] | None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id, player_id, tournament_id, source_ingest_file_id, site, title,
                        started_at, buy_in, player_count, prize_pool, finish_place,
                        total_received, result_payload
                    FROM core.tournament_results
                    WHERE player_id = %s AND tournament_id = %s
                    LIMIT 1
                    """,
                    (player_id, tournament_id),
                )
                row = cur.fetchone()
            conn.commit()
        return dict(row) if row else None

    def fetch_tournament_results(self, player_id: str, limit: int = 20) -> list[dict[str, Any]]:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id, player_id, tournament_id, source_ingest_file_id, site, title,
                        started_at, buy_in, player_count, prize_pool, finish_place,
                        total_received, result_payload
                    FROM core.tournament_results
                    WHERE player_id = %s
                    ORDER BY started_at DESC, tournament_id DESC
                    LIMIT %s
                    """,
                    (player_id, limit),
                )
                rows = cur.fetchall() or []
            conn.commit()
        return [dict(row) for row in rows]

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

    def get_user_account_by_provider_identity(
        self, auth_provider: str, auth_provider_user_id: str
    ) -> dict[str, Any] | None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, auth_provider, auth_provider_user_id, email, status, account_metadata
                    FROM auth.user_accounts
                    WHERE auth_provider = %s AND auth_provider_user_id = %s
                    LIMIT 1
                    """,
                    (auth_provider, auth_provider_user_id),
                )
                row = cur.fetchone()
            conn.commit()
        return dict(row) if row else None

    def get_user_account_by_email(self, email: str) -> dict[str, Any] | None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, auth_provider, auth_provider_user_id, email, status, account_metadata
                    FROM auth.user_accounts
                    WHERE LOWER(email) = LOWER(%s)
                    LIMIT 1
                    """,
                    (email,),
                )
                row = cur.fetchone()
            conn.commit()
        return dict(row) if row else None

    def upsert_user_account(self, record: UserAccountRecord) -> None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO auth.user_accounts (
                        id, auth_provider, auth_provider_user_id, email, status, account_metadata, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s)
                    ON CONFLICT (auth_provider_user_id)
                    DO UPDATE SET
                        email = EXCLUDED.email,
                        status = EXCLUDED.status,
                        account_metadata = EXCLUDED.account_metadata,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (
                        record.id,
                        record.auth_provider,
                        record.auth_provider_user_id,
                        record.email,
                        record.status,
                        json.dumps(record.account_metadata),
                        _now(),
                        _now(),
                    ),
                )
            conn.commit()

    def upsert_user_player_access(self, record: UserPlayerAccessRecord) -> None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO auth.user_player_access (
                        id, user_account_id, player_id, access_role, status, granted_by_user_account_id,
                        granted_reason, access_metadata, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
                    ON CONFLICT (user_account_id, player_id, access_role)
                    DO UPDATE SET
                        status = EXCLUDED.status,
                        granted_by_user_account_id = EXCLUDED.granted_by_user_account_id,
                        granted_reason = EXCLUDED.granted_reason,
                        access_metadata = EXCLUDED.access_metadata,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (
                        record.id,
                        record.user_account_id,
                        record.player_id,
                        record.access_role,
                        record.status,
                        record.granted_by_user_account_id,
                        record.granted_reason,
                        json.dumps(record.access_metadata),
                        _now(),
                        _now(),
                    ),
                )
            conn.commit()

    def upsert_user_global_role(self, record: UserGlobalRoleRecord) -> None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO auth.user_global_roles (
                        id, user_account_id, role, status, granted_by_user_account_id, role_metadata, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s)
                    ON CONFLICT (user_account_id, role)
                    DO UPDATE SET
                        status = EXCLUDED.status,
                        granted_by_user_account_id = EXCLUDED.granted_by_user_account_id,
                        role_metadata = EXCLUDED.role_metadata,
                        updated_at = EXCLUDED.updated_at
                    """,
                    (
                        record.id,
                        record.user_account_id,
                        record.role,
                        record.status,
                        record.granted_by_user_account_id,
                        json.dumps(record.role_metadata),
                        _now(),
                        _now(),
                    ),
                )
            conn.commit()

    def fetch_active_user_player_access(self, user_account_id: str) -> list[dict[str, Any]]:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, user_account_id, player_id, access_role, status, granted_by_user_account_id, granted_reason, access_metadata
                    FROM auth.user_player_access
                    WHERE user_account_id = %s AND status = 'active'
                    ORDER BY
                        CASE access_role WHEN 'owner' THEN 1 WHEN 'operator' THEN 2 ELSE 3 END,
                        created_at DESC
                    """,
                    (user_account_id,),
                )
                rows = cur.fetchall() or []
            conn.commit()
        return [dict(row) for row in rows]

    def fetch_active_user_global_roles(self, user_account_id: str) -> list[dict[str, Any]]:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, user_account_id, role, status, granted_by_user_account_id, role_metadata
                    FROM auth.user_global_roles
                    WHERE user_account_id = %s AND status = 'active'
                    ORDER BY created_at DESC
                    """,
                    (user_account_id,),
                )
                rows = cur.fetchall() or []
            conn.commit()
        return [dict(row) for row in rows]

    def create_demo_application(self, record: DemoApplicationRecord) -> None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO auth.demo_applications (
                        id, name, email, games, help_goal, status, source, application_metadata, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, %s)
                    """,
                    (
                        record.id,
                        record.name,
                        record.email,
                        record.games,
                        record.help_goal,
                        record.status,
                        record.source,
                        json.dumps(record.application_metadata),
                        _now(),
                        _now(),
                    ),
                )
            conn.commit()

    def fetch_demo_applications(self, status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if status:
                    cur.execute(
                        """
                        SELECT id, name, email, games, help_goal, status, source, application_metadata, created_at, updated_at
                        FROM auth.demo_applications
                        WHERE status = %s
                        ORDER BY created_at DESC, id DESC
                        LIMIT %s
                        """,
                        (status, limit),
                    )
                else:
                    cur.execute(
                        """
                        SELECT id, name, email, games, help_goal, status, source, application_metadata, created_at, updated_at
                        FROM auth.demo_applications
                        ORDER BY created_at DESC, id DESC
                        LIMIT %s
                        """,
                        (limit,),
                    )
                rows = cur.fetchall() or []
            conn.commit()
        return [dict(row) for row in rows]

    def get_demo_application(self, application_id: str) -> dict[str, Any] | None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name, email, games, help_goal, status, source, application_metadata, created_at, updated_at
                    FROM auth.demo_applications
                    WHERE id = %s
                    LIMIT 1
                    """,
                    (application_id,),
                )
                row = cur.fetchone()
            conn.commit()
        return dict(row) if row else None

    def update_demo_application_status(
        self, application_id: str, status: str, application_metadata: dict[str, Any] | None = None
    ) -> None:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                if application_metadata is None:
                    cur.execute(
                        "UPDATE auth.demo_applications SET status = %s, updated_at = %s WHERE id = %s",
                        (status, _now(), application_id),
                    )
                else:
                    cur.execute(
                        """
                        UPDATE auth.demo_applications
                        SET status = %s, application_metadata = %s::jsonb, updated_at = %s
                        WHERE id = %s
                        """,
                        (status, json.dumps(application_metadata), _now(), application_id),
                    )
            conn.commit()
