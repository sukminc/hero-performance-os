from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
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
from core.storage.sqlite import get_sqlite_connection


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json_load(value: Any, default: Any) -> Any:
    if value in (None, ""):
        return default
    if isinstance(value, (dict, list)):
        return value
    return json.loads(value)


def _row_to_dict(row: Any) -> dict[str, Any]:
    return dict(row) if row is not None else {}


class SQLiteV2Repository:
    def ensure_schema(self) -> None:
        schema_sql = """
                CREATE TABLE IF NOT EXISTS ingest_files (
                    id TEXT PRIMARY KEY,
                    player_id TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    file_hash TEXT NOT NULL UNIQUE,
                    original_filename TEXT NOT NULL,
                    source_path TEXT,
                    status TEXT NOT NULL,
                    duplicate_of_file_id TEXT,
                    raw_metadata TEXT NOT NULL DEFAULT '{}',
                    uploaded_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    player_id TEXT NOT NULL,
                    ingest_file_id TEXT NOT NULL,
                    session_key TEXT NOT NULL UNIQUE,
                    started_at TEXT,
                    ended_at TEXT,
                    site TEXT NOT NULL,
                    buyin_band TEXT,
                    currency TEXT,
                    parse_status TEXT NOT NULL,
                    hand_count INTEGER NOT NULL,
                    confidence_summary TEXT NOT NULL DEFAULT '{}',
                    session_metadata TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS hands (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    hand_external_id TEXT NOT NULL,
                    tournament_id TEXT,
                    hero_position TEXT,
                    effective_stack_bb REAL,
                    phase_proxy TEXT,
                    bounty_proxy TEXT,
                    players_to_flop INTEGER,
                    board_texture_summary TEXT,
                    result_summary TEXT NOT NULL DEFAULT '{}',
                    header_metadata TEXT NOT NULL DEFAULT '{}',
                    raw_payload TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS tournament_results (
                    id TEXT PRIMARY KEY,
                    player_id TEXT NOT NULL,
                    tournament_id TEXT NOT NULL,
                    source_ingest_file_id TEXT NOT NULL,
                    site TEXT NOT NULL,
                    title TEXT,
                    started_at TEXT,
                    buy_in TEXT,
                    player_count INTEGER,
                    prize_pool TEXT,
                    finish_place TEXT,
                    total_received TEXT,
                    result_payload TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE (player_id, tournament_id)
                );

                CREATE INDEX IF NOT EXISTS tournament_results_player_idx
                ON tournament_results (player_id, started_at DESC, tournament_id);

                CREATE TABLE IF NOT EXISTS session_evidence (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    evidence_type TEXT NOT NULL,
                    entity_scope TEXT NOT NULL,
                    entity_key TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    strength_score REAL,
                    confidence REAL,
                    sample_size INTEGER,
                    explanation TEXT,
                    source_hand_ids TEXT NOT NULL DEFAULT '[]',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS memory_items (
                    id TEXT PRIMARY KEY,
                    player_id TEXT NOT NULL,
                    memory_type TEXT NOT NULL,
                    memory_key TEXT NOT NULL,
                    status TEXT NOT NULL,
                    first_seen_session_id TEXT,
                    last_seen_session_id TEXT,
                    evidence_count INTEGER NOT NULL DEFAULT 0,
                    confidence REAL,
                    summary TEXT,
                    suggested_adjustment TEXT,
                    memory_payload TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE (player_id, memory_type, memory_key)
                );

                CREATE TABLE IF NOT EXISTS surface_snapshots (
                    id TEXT PRIMARY KEY,
                    player_id TEXT NOT NULL,
                    session_id TEXT,
                    surface_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    confidence_summary TEXT NOT NULL DEFAULT '{}',
                    generated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS user_accounts (
                    id TEXT PRIMARY KEY,
                    auth_provider TEXT NOT NULL,
                    auth_provider_user_id TEXT NOT NULL UNIQUE,
                    email TEXT,
                    status TEXT NOT NULL DEFAULT 'active',
                    account_metadata TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE UNIQUE INDEX IF NOT EXISTS user_accounts_email_unique_idx
                ON user_accounts (LOWER(email));

                CREATE TABLE IF NOT EXISTS user_player_access (
                    id TEXT PRIMARY KEY,
                    user_account_id TEXT NOT NULL,
                    player_id TEXT NOT NULL,
                    access_role TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    granted_by_user_account_id TEXT,
                    granted_reason TEXT,
                    access_metadata TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE (user_account_id, player_id, access_role)
                );

                CREATE INDEX IF NOT EXISTS user_player_access_user_idx
                ON user_player_access (user_account_id, status, access_role);

                CREATE INDEX IF NOT EXISTS user_player_access_player_idx
                ON user_player_access (player_id, status, access_role);

                CREATE TABLE IF NOT EXISTS user_global_roles (
                    id TEXT PRIMARY KEY,
                    user_account_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active',
                    granted_by_user_account_id TEXT,
                    role_metadata TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE (user_account_id, role)
                );

                CREATE INDEX IF NOT EXISTS user_global_roles_user_idx
                ON user_global_roles (user_account_id, status, role);

                CREATE TABLE IF NOT EXISTS demo_applications (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL,
                    games TEXT NOT NULL,
                    help_goal TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'new',
                    source TEXT NOT NULL DEFAULT 'public_demo_apply',
                    application_metadata TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS demo_applications_status_idx
                ON demo_applications (status, created_at DESC);

                CREATE INDEX IF NOT EXISTS demo_applications_email_idx
                ON demo_applications (LOWER(email), created_at DESC);

                CREATE TABLE IF NOT EXISTS operator_reviews (
                    id TEXT PRIMARY KEY,
                    target_type TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    review_type TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    notes TEXT,
                    review_payload TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS operator_reviews_target_idx
                ON operator_reviews (target_type, target_id, review_type, created_at DESC);
                """
        try:
            with get_sqlite_connection() as conn:
                conn.executescript(schema_sql)
        except sqlite3.OperationalError as exc:
            if "readonly" not in str(exc).lower():
                raise
            with get_sqlite_connection() as conn:
                existing_tables = {
                    row["name"]
                    for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall()
                }
            required_tables = {
                "ingest_files",
                "sessions",
                "hands",
                "tournament_results",
                "session_evidence",
                "memory_items",
                "surface_snapshots",
                "user_accounts",
                "user_player_access",
                "user_global_roles",
                "demo_applications",
            }
            if not required_tables.issubset(existing_tables):
                raise

    def get_ingest_file_by_hash(self, file_hash: str) -> dict[str, Any] | None:
        with get_sqlite_connection() as conn:
            row = conn.execute(
                """
                SELECT id, player_id, source_type, file_hash, original_filename, status, duplicate_of_file_id
                FROM ingest_files
                WHERE file_hash = ?
                ORDER BY uploaded_at DESC
                LIMIT 1
                """,
                (file_hash,),
            ).fetchone()
        return dict(row) if row else None

    def get_ingest_file_by_id(self, ingest_file_id: str) -> dict[str, Any] | None:
        with get_sqlite_connection() as conn:
            row = conn.execute(
                """
                SELECT id, player_id, source_type, file_hash, original_filename, status, duplicate_of_file_id, raw_metadata, uploaded_at
                FROM ingest_files
                WHERE id = ?
                LIMIT 1
                """,
                (ingest_file_id,),
            ).fetchone()
        if not row:
            return None
        payload = dict(row)
        payload["raw_metadata"] = _json_load(payload.get("raw_metadata"), {})
        return payload

    def create_ingest_file(self, record: IngestFileRecord) -> None:
        with get_sqlite_connection() as conn:
            conn.execute(
                """
                INSERT INTO ingest_files (
                    id, player_id, source_type, file_hash, original_filename, source_path,
                    status, duplicate_of_file_id, raw_metadata, uploaded_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    str(record.uploaded_at),
                    _now(),
                ),
            )

    def update_ingest_status(self, ingest_file_id: str, status: str, raw_metadata: dict[str, Any] | None = None) -> None:
        with get_sqlite_connection() as conn:
            if raw_metadata is None:
                conn.execute(
                    "UPDATE ingest_files SET status = ?, updated_at = ? WHERE id = ?",
                    (status, _now(), ingest_file_id),
                )
            else:
                conn.execute(
                    "UPDATE ingest_files SET status = ?, raw_metadata = ?, updated_at = ? WHERE id = ?",
                    (status, json.dumps(raw_metadata), _now(), ingest_file_id),
                )

    def create_session(self, record: SessionRecord) -> None:
        with get_sqlite_connection() as conn:
            conn.execute(
                """
                INSERT INTO sessions (
                    id, player_id, ingest_file_id, session_key, started_at, ended_at, site,
                    buyin_band, currency, parse_status, hand_count, confidence_summary,
                    session_metadata, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

    def fetch_session(self, session_id: str) -> dict[str, Any] | None:
        with get_sqlite_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    id, player_id, ingest_file_id, session_key, started_at, ended_at, site,
                    buyin_band, currency, parse_status, hand_count, confidence_summary, session_metadata
                FROM sessions
                WHERE id = ?
                LIMIT 1
                """,
                (session_id,),
            ).fetchone()
        if not row:
            return None
        payload = dict(row)
        payload["confidence_summary"] = _json_load(payload.get("confidence_summary"), {})
        payload["session_metadata"] = _json_load(payload.get("session_metadata"), {})
        return payload

    def fetch_session_by_tournament_id(self, player_id: str, tournament_id: str) -> dict[str, Any] | None:
        with get_sqlite_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    id, player_id, ingest_file_id, session_key, started_at, ended_at, site,
                    buyin_band, currency, parse_status, hand_count, confidence_summary, session_metadata
                FROM sessions
                WHERE player_id = ? AND json_extract(session_metadata, '$.tournament_id') = ?
                ORDER BY hand_count DESC, created_at DESC
                LIMIT 1
                """,
                (player_id, tournament_id),
            ).fetchone()
        if not row:
            return None
        payload = dict(row)
        payload["confidence_summary"] = _json_load(payload.get("confidence_summary"), {})
        payload["session_metadata"] = _json_load(payload.get("session_metadata"), {})
        return payload

    def fetch_hands_for_session(self, session_id: str, limit: int = 20) -> list[dict[str, Any]]:
        with get_sqlite_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    id, session_id, hand_external_id, tournament_id, hero_position,
                    effective_stack_bb, phase_proxy, bounty_proxy, players_to_flop,
                    board_texture_summary, result_summary, header_metadata, raw_payload
                FROM hands
                WHERE session_id = ?
                ORDER BY created_at, id
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()
        results: list[dict[str, Any]] = []
        for row in rows:
            payload = dict(row)
            payload["result_summary"] = _json_load(payload.get("result_summary"), {})
            payload["header_metadata"] = _json_load(payload.get("header_metadata"), {})
            payload["raw_payload"] = _json_load(payload.get("raw_payload"), {})
            results.append(payload)
        return results

    def fetch_hands_for_player(self, player_id: str, limit: int = 50000) -> list[dict[str, Any]]:
        with get_sqlite_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    h.id, h.session_id, h.hand_external_id, h.tournament_id, h.hero_position,
                    h.effective_stack_bb, h.phase_proxy, h.bounty_proxy, h.players_to_flop,
                    h.board_texture_summary, h.result_summary, h.header_metadata, h.raw_payload,
                    s.buyin_band, s.session_metadata
                FROM hands h
                JOIN sessions s ON s.id = h.session_id
                WHERE s.player_id = ?
                ORDER BY h.created_at, h.id
                LIMIT ?
                """,
                (player_id, limit),
            ).fetchall()
        results: list[dict[str, Any]] = []
        for row in rows:
            payload = dict(row)
            payload["result_summary"] = _json_load(payload.get("result_summary"), {})
            payload["header_metadata"] = _json_load(payload.get("header_metadata"), {})
            payload["raw_payload"] = _json_load(payload.get("raw_payload"), {})
            payload["session_metadata"] = _json_load(payload.get("session_metadata"), {})
            results.append(payload)
        return results

    def create_hands(self, hands: list[HandRecord]) -> None:
        if not hands:
            return
        with get_sqlite_connection() as conn:
            conn.executemany(
                """
                INSERT INTO hands (
                    id, session_id, hand_external_id, tournament_id, hero_position,
                    effective_stack_bb, phase_proxy, bounty_proxy, players_to_flop,
                    board_texture_summary, result_summary, header_metadata, raw_payload, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
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
                    )
                    for hand in hands
                ],
            )

    def upsert_tournament_result(self, record: TournamentResultRecord) -> None:
        with get_sqlite_connection() as conn:
            conn.execute(
                """
                INSERT INTO tournament_results (
                    id, player_id, tournament_id, source_ingest_file_id, site, title,
                    started_at, buy_in, player_count, prize_pool, finish_place,
                    total_received, result_payload, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(player_id, tournament_id)
                DO UPDATE SET
                    source_ingest_file_id=excluded.source_ingest_file_id,
                    site=excluded.site,
                    title=excluded.title,
                    started_at=excluded.started_at,
                    buy_in=excluded.buy_in,
                    player_count=excluded.player_count,
                    prize_pool=excluded.prize_pool,
                    finish_place=excluded.finish_place,
                    total_received=excluded.total_received,
                    result_payload=excluded.result_payload,
                    updated_at=excluded.updated_at
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

    def get_tournament_result(self, player_id: str, tournament_id: str) -> dict[str, Any] | None:
        with get_sqlite_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    id, player_id, tournament_id, source_ingest_file_id, site, title,
                    started_at, buy_in, player_count, prize_pool, finish_place,
                    total_received, result_payload
                FROM tournament_results
                WHERE player_id = ? AND tournament_id = ?
                LIMIT 1
                """,
                (player_id, tournament_id),
            ).fetchone()
        if not row:
            return None
        payload = dict(row)
        payload["result_payload"] = _json_load(payload.get("result_payload"), {})
        return payload

    def fetch_tournament_results(self, player_id: str, limit: int = 20) -> list[dict[str, Any]]:
        with get_sqlite_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    id, player_id, tournament_id, source_ingest_file_id, site, title,
                    started_at, buy_in, player_count, prize_pool, finish_place,
                    total_received, result_payload
                FROM tournament_results
                WHERE player_id = ?
                ORDER BY started_at DESC, tournament_id DESC
                LIMIT ?
                """,
                (player_id, limit),
            ).fetchall()
        results: list[dict[str, Any]] = []
        for row in rows:
            payload = dict(row)
            payload["result_payload"] = _json_load(payload.get("result_payload"), {})
            results.append(payload)
        return results

    def create_session_evidence(self, evidence_rows: list[SessionEvidenceRecord]) -> None:
        if not evidence_rows:
            return
        with get_sqlite_connection() as conn:
            conn.executemany(
                """
                INSERT INTO session_evidence (
                    id, session_id, evidence_type, entity_scope, entity_key, direction,
                    strength_score, confidence, sample_size, explanation, source_hand_ids, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
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
                    )
                    for row in evidence_rows
                ],
            )

    def fetch_session_evidence(self, session_id: str) -> list[dict[str, Any]]:
        with get_sqlite_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    id, session_id, evidence_type, entity_scope, entity_key, direction,
                    strength_score, confidence, sample_size, explanation, source_hand_ids
                FROM session_evidence
                WHERE session_id = ?
                ORDER BY created_at, id
                """,
                (session_id,),
            ).fetchall()
        results: list[dict[str, Any]] = []
        for row in rows:
            payload = dict(row)
            payload["source_hand_ids"] = _json_load(payload.get("source_hand_ids"), [])
            results.append(payload)
        return results

    def get_memory_item(self, player_id: str, memory_type: str, memory_key: str) -> dict[str, Any] | None:
        with get_sqlite_connection() as conn:
            row = conn.execute(
                """
                SELECT
                    id, player_id, memory_type, memory_key, status, first_seen_session_id,
                    last_seen_session_id, evidence_count, confidence, summary,
                    suggested_adjustment, memory_payload
                FROM memory_items
                WHERE player_id = ? AND memory_type = ? AND memory_key = ?
                LIMIT 1
                """,
                (player_id, memory_type, memory_key),
            ).fetchone()
        if not row:
            return None
        payload = dict(row)
        payload["memory_payload"] = _json_load(payload.get("memory_payload"), {})
        return payload

    def upsert_memory_item(self, record: MemoryItemRecord) -> None:
        with get_sqlite_connection() as conn:
            conn.execute(
                """
                INSERT INTO memory_items (
                    id, player_id, memory_type, memory_key, status, first_seen_session_id,
                    last_seen_session_id, evidence_count, confidence, summary,
                    suggested_adjustment, memory_payload, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(player_id, memory_type, memory_key)
                DO UPDATE SET
                    status=excluded.status,
                    first_seen_session_id=COALESCE(memory_items.first_seen_session_id, excluded.first_seen_session_id),
                    last_seen_session_id=excluded.last_seen_session_id,
                    evidence_count=excluded.evidence_count,
                    confidence=excluded.confidence,
                    summary=excluded.summary,
                    suggested_adjustment=excluded.suggested_adjustment,
                    memory_payload=excluded.memory_payload,
                    updated_at=excluded.updated_at
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

    def fetch_memory_items(self, player_id: str, statuses: list[str] | None = None) -> list[dict[str, Any]]:
        query = """
            SELECT
                id, player_id, memory_type, memory_key, status, first_seen_session_id,
                last_seen_session_id, evidence_count, confidence, summary,
                suggested_adjustment, memory_payload
            FROM memory_items
            WHERE player_id = ?
        """
        params: list[Any] = [player_id]
        if statuses:
            placeholders = ",".join("?" for _ in statuses)
            query += f" AND status IN ({placeholders})"
            params.extend(statuses)
        query += """
            ORDER BY
                CASE status
                    WHEN 'active' THEN 1
                    WHEN 'baseline' THEN 2
                    WHEN 'watch' THEN 3
                    WHEN 'resolved' THEN 4
                    ELSE 5
                END,
                evidence_count DESC,
                confidence DESC,
                updated_at DESC
        """
        with get_sqlite_connection() as conn:
            rows = conn.execute(query, params).fetchall()
        results: list[dict[str, Any]] = []
        for row in rows:
            payload = dict(row)
            payload["memory_payload"] = _json_load(payload.get("memory_payload"), {})
            results.append(payload)
        return results

    def create_surface_snapshot(
        self,
        snapshot_id: str,
        player_id: str,
        session_id: str | None,
        surface_type: str,
        payload: dict[str, Any],
        confidence_summary: dict[str, Any],
    ) -> None:
        with get_sqlite_connection() as conn:
            conn.execute(
                """
                INSERT INTO surface_snapshots (
                    id, player_id, session_id, surface_type, payload, confidence_summary, generated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
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

    def fetch_latest_surface_snapshot(self, player_id: str, surface_type: str) -> dict[str, Any] | None:
        with get_sqlite_connection() as conn:
            row = conn.execute(
                """
                SELECT id, player_id, session_id, surface_type, payload, confidence_summary, generated_at
                FROM surface_snapshots
                WHERE player_id = ? AND surface_type = ?
                ORDER BY generated_at DESC, id DESC
                LIMIT 1
                """,
                (player_id, surface_type),
            ).fetchone()
        if not row:
            return None
        payload = dict(row)
        payload["payload"] = _json_load(payload.get("payload"), {})
        payload["confidence_summary"] = _json_load(payload.get("confidence_summary"), {})
        return payload

    def fetch_latest_session_id(self, player_id: str) -> str | None:
        with get_sqlite_connection() as conn:
            row = conn.execute(
                """
                SELECT id
                FROM sessions
                WHERE player_id = ?
                ORDER BY created_at DESC, id DESC
                LIMIT 1
                """,
                (player_id,),
            ).fetchone()
        return str(row["id"]) if row else None

    def fetch_memory_items_for_session(self, player_id: str, session_id: str) -> list[dict[str, Any]]:
        with get_sqlite_connection() as conn:
            rows = conn.execute(
                """
                SELECT
                    id, player_id, memory_type, memory_key, status, first_seen_session_id,
                    last_seen_session_id, evidence_count, confidence, summary,
                    suggested_adjustment, memory_payload
                FROM memory_items
                WHERE player_id = ? AND last_seen_session_id = ?
                ORDER BY
                    CASE status
                        WHEN 'active' THEN 1
                        WHEN 'baseline' THEN 2
                        WHEN 'watch' THEN 3
                        WHEN 'resolved' THEN 4
                        ELSE 5
                    END,
                    evidence_count DESC,
                    confidence DESC,
                    updated_at DESC
                """,
                (player_id, session_id),
            ).fetchall()
        results: list[dict[str, Any]] = []
        for row in rows:
            payload = dict(row)
            payload["memory_payload"] = _json_load(payload.get("memory_payload"), {})
            results.append(payload)
        return results

    def create_operator_review(self, record: OperatorReviewRecord) -> None:
        with get_sqlite_connection() as conn:
            conn.execute(
                """
                INSERT INTO operator_reviews (
                    id, target_type, target_id, review_type, decision, notes, review_payload, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.id,
                    record.target_type,
                    record.target_id,
                    record.review_type,
                    record.decision,
                    record.notes,
                    json.dumps(record.review_payload),
                    record.created_at.isoformat() if record.created_at else _now(),
                ),
            )

    def fetch_operator_reviews(self, target_type: str, target_id: str, review_type: str | None = None) -> list[dict[str, Any]]:
        query = """
            SELECT id, target_type, target_id, review_type, decision, notes, review_payload, created_at
            FROM operator_reviews
            WHERE target_type = ? AND target_id = ?
        """
        params: list[Any] = [target_type, target_id]
        if review_type is not None:
            query += " AND review_type = ?"
            params.append(review_type)
        query += " ORDER BY created_at DESC, id DESC"
        try:
            with get_sqlite_connection() as conn:
                rows = conn.execute(query, params).fetchall()
        except sqlite3.OperationalError as exc:
            if "no such table" in str(exc).lower() and "operator_reviews" in str(exc).lower():
                return []
            raise
        results = []
        for row in rows:
            payload = dict(row)
            payload["review_payload"] = _json_load(payload.get("review_payload"), {})
            results.append(payload)
        return results

    def get_user_account_by_provider_identity(
        self, auth_provider: str, auth_provider_user_id: str
    ) -> dict[str, Any] | None:
        with get_sqlite_connection() as conn:
            row = conn.execute(
                """
                SELECT id, auth_provider, auth_provider_user_id, email, status, account_metadata
                FROM user_accounts
                WHERE auth_provider = ? AND auth_provider_user_id = ?
                LIMIT 1
                """,
                (auth_provider, auth_provider_user_id),
            ).fetchone()
        if not row:
            return None
        payload = dict(row)
        payload["account_metadata"] = _json_load(payload.get("account_metadata"), {})
        return payload

    def get_user_account_by_email(self, email: str) -> dict[str, Any] | None:
        with get_sqlite_connection() as conn:
            row = conn.execute(
                """
                SELECT id, auth_provider, auth_provider_user_id, email, status, account_metadata
                FROM user_accounts
                WHERE LOWER(email) = LOWER(?)
                LIMIT 1
                """,
                (email,),
            ).fetchone()
        if not row:
            return None
        payload = dict(row)
        payload["account_metadata"] = _json_load(payload.get("account_metadata"), {})
        return payload

    def upsert_user_account(self, record: UserAccountRecord) -> None:
        with get_sqlite_connection() as conn:
            conn.execute(
                """
                INSERT INTO user_accounts (
                    id, auth_provider, auth_provider_user_id, email, status, account_metadata, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(auth_provider_user_id)
                DO UPDATE SET
                    email=excluded.email,
                    status=excluded.status,
                    account_metadata=excluded.account_metadata,
                    updated_at=excluded.updated_at
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

    def upsert_user_player_access(self, record: UserPlayerAccessRecord) -> None:
        with get_sqlite_connection() as conn:
            conn.execute(
                """
                INSERT INTO user_player_access (
                    id, user_account_id, player_id, access_role, status, granted_by_user_account_id,
                    granted_reason, access_metadata, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_account_id, player_id, access_role)
                DO UPDATE SET
                    status=excluded.status,
                    granted_by_user_account_id=excluded.granted_by_user_account_id,
                    granted_reason=excluded.granted_reason,
                    access_metadata=excluded.access_metadata,
                    updated_at=excluded.updated_at
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

    def upsert_user_global_role(self, record: UserGlobalRoleRecord) -> None:
        with get_sqlite_connection() as conn:
            conn.execute(
                """
                INSERT INTO user_global_roles (
                    id, user_account_id, role, status, granted_by_user_account_id, role_metadata, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_account_id, role)
                DO UPDATE SET
                    status=excluded.status,
                    granted_by_user_account_id=excluded.granted_by_user_account_id,
                    role_metadata=excluded.role_metadata,
                    updated_at=excluded.updated_at
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

    def fetch_active_user_player_access(self, user_account_id: str) -> list[dict[str, Any]]:
        with get_sqlite_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, user_account_id, player_id, access_role, status, granted_by_user_account_id, granted_reason, access_metadata
                FROM user_player_access
                WHERE user_account_id = ? AND status = 'active'
                ORDER BY
                    CASE access_role WHEN 'owner' THEN 1 WHEN 'operator' THEN 2 ELSE 3 END,
                    created_at DESC
                """,
                (user_account_id,),
            ).fetchall()
        results = []
        for row in rows:
            payload = dict(row)
            payload["access_metadata"] = _json_load(payload.get("access_metadata"), {})
            results.append(payload)
        return results

    def fetch_active_user_global_roles(self, user_account_id: str) -> list[dict[str, Any]]:
        with get_sqlite_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, user_account_id, role, status, granted_by_user_account_id, role_metadata
                FROM user_global_roles
                WHERE user_account_id = ? AND status = 'active'
                ORDER BY created_at DESC
                """,
                (user_account_id,),
            ).fetchall()
        results = []
        for row in rows:
            payload = dict(row)
            payload["role_metadata"] = _json_load(payload.get("role_metadata"), {})
            results.append(payload)
        return results

    def create_demo_application(self, record: DemoApplicationRecord) -> None:
        with get_sqlite_connection() as conn:
            conn.execute(
                """
                INSERT INTO demo_applications (
                    id, name, email, games, help_goal, status, source, application_metadata, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

    def fetch_demo_applications(self, status: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
        query = """
            SELECT id, name, email, games, help_goal, status, source, application_metadata, created_at, updated_at
            FROM demo_applications
        """
        params: list[Any] = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY created_at DESC, id DESC LIMIT ?"
        params.append(limit)
        with get_sqlite_connection() as conn:
            rows = conn.execute(query, params).fetchall()
        results = []
        for row in rows:
            payload = dict(row)
            payload["application_metadata"] = _json_load(payload.get("application_metadata"), {})
            results.append(payload)
        return results

    def get_demo_application(self, application_id: str) -> dict[str, Any] | None:
        with get_sqlite_connection() as conn:
            row = conn.execute(
                """
                SELECT id, name, email, games, help_goal, status, source, application_metadata, created_at, updated_at
                FROM demo_applications
                WHERE id = ?
                LIMIT 1
                """,
                (application_id,),
            ).fetchone()
        if not row:
            return None
        payload = dict(row)
        payload["application_metadata"] = _json_load(payload.get("application_metadata"), {})
        return payload

    def update_demo_application_status(
        self, application_id: str, status: str, application_metadata: dict[str, Any] | None = None
    ) -> None:
        with get_sqlite_connection() as conn:
            if application_metadata is None:
                conn.execute(
                    "UPDATE demo_applications SET status = ?, updated_at = ? WHERE id = ?",
                    (status, _now(), application_id),
                )
            else:
                conn.execute(
                    "UPDATE demo_applications SET status = ?, application_metadata = ?, updated_at = ? WHERE id = ?",
                    (status, json.dumps(application_metadata), _now(), application_id),
                )
