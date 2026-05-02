from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class IngestFileRecord:
    id: str
    player_id: str
    source_type: str
    file_hash: str
    original_filename: str
    status: str
    uploaded_at: datetime
    duplicate_of_file_id: str | None = None
    source_path: str | None = None
    raw_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SessionRecord:
    id: str
    player_id: str
    ingest_file_id: str
    session_key: str
    site: str
    parse_status: str
    hand_count: int
    started_at: str | None = None
    ended_at: str | None = None
    buyin_band: str | None = None
    currency: str | None = None
    confidence_summary: dict[str, Any] = field(default_factory=dict)
    session_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TournamentResultRecord:
    id: str
    player_id: str
    tournament_id: str
    source_ingest_file_id: str
    site: str
    title: str | None = None
    started_at: str | None = None
    buy_in: str | None = None
    player_count: int | None = None
    prize_pool: str | None = None
    finish_place: str | None = None
    total_received: str | None = None
    result_payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class HandRecord:
    id: str
    session_id: str
    hand_external_id: str
    tournament_id: str | None
    hero_position: str | None
    effective_stack_bb: float | None
    phase_proxy: str | None
    bounty_proxy: str | None
    players_to_flop: int | None
    board_texture_summary: str | None
    result_summary: dict[str, Any] = field(default_factory=dict)
    header_metadata: dict[str, Any] = field(default_factory=dict)
    raw_payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SessionEvidenceRecord:
    id: str
    session_id: str
    evidence_type: str
    entity_scope: str
    entity_key: str
    direction: str
    strength_score: float | None = None
    confidence: float | None = None
    sample_size: int | None = None
    explanation: str | None = None
    source_hand_ids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class MemoryItemRecord:
    id: str
    player_id: str
    memory_type: str
    memory_key: str
    status: str
    first_seen_session_id: str | None = None
    last_seen_session_id: str | None = None
    evidence_count: int = 0
    confidence: float | None = None
    summary: str | None = None
    suggested_adjustment: str | None = None
    memory_payload: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class OperatorReviewRecord:
    id: str
    target_type: str
    target_id: str
    review_type: str
    decision: str
    notes: str | None = None
    review_payload: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None


@dataclass(slots=True)
class UserAccountRecord:
    id: str
    auth_provider: str
    auth_provider_user_id: str
    email: str | None = None
    status: str = "active"
    account_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class UserPlayerAccessRecord:
    id: str
    user_account_id: str
    player_id: str
    access_role: str
    status: str = "active"
    granted_by_user_account_id: str | None = None
    granted_reason: str | None = None
    access_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class UserGlobalRoleRecord:
    id: str
    user_account_id: str
    role: str
    status: str = "active"
    granted_by_user_account_id: str | None = None
    role_metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class DemoApplicationRecord:
    id: str
    name: str
    email: str
    games: str
    help_goal: str
    status: str = "new"
    source: str = "public_demo_apply"
    application_metadata: dict[str, Any] = field(default_factory=dict)
