CREATE TABLE IF NOT EXISTS core.ingest_files (
    id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    file_hash TEXT NOT NULL UNIQUE,
    original_filename TEXT NOT NULL,
    source_path TEXT,
    status TEXT NOT NULL,
    duplicate_of_file_id TEXT,
    raw_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    uploaded_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS core.sessions (
    id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL,
    ingest_file_id TEXT NOT NULL REFERENCES core.ingest_files(id),
    session_key TEXT NOT NULL UNIQUE,
    started_at TEXT,
    ended_at TEXT,
    site TEXT NOT NULL,
    buyin_band TEXT,
    currency TEXT,
    parse_status TEXT NOT NULL,
    hand_count INTEGER NOT NULL,
    confidence_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    session_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS core.hands (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES core.sessions(id) ON DELETE CASCADE,
    hand_external_id TEXT NOT NULL,
    tournament_id TEXT,
    hero_position TEXT,
    effective_stack_bb DOUBLE PRECISION,
    phase_proxy TEXT,
    bounty_proxy TEXT,
    players_to_flop INTEGER,
    board_texture_summary TEXT,
    result_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    header_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    raw_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS core.session_evidence (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES core.sessions(id) ON DELETE CASCADE,
    evidence_type TEXT NOT NULL,
    entity_scope TEXT NOT NULL,
    entity_key TEXT NOT NULL,
    direction TEXT NOT NULL,
    strength_score DOUBLE PRECISION,
    confidence DOUBLE PRECISION,
    sample_size INTEGER,
    explanation TEXT,
    source_hand_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS core.memory_items (
    id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL,
    memory_type TEXT NOT NULL,
    memory_key TEXT NOT NULL,
    status TEXT NOT NULL,
    first_seen_session_id TEXT,
    last_seen_session_id TEXT,
    evidence_count INTEGER NOT NULL DEFAULT 0,
    confidence DOUBLE PRECISION,
    summary TEXT,
    suggested_adjustment TEXT,
    memory_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    UNIQUE (player_id, memory_type, memory_key)
);

CREATE TABLE IF NOT EXISTS core.style_snapshots (
    id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL,
    window_type TEXT NOT NULL,
    window_start TIMESTAMPTZ,
    window_end TIMESTAMPTZ,
    aggression_profile JSONB NOT NULL DEFAULT '{}'::jsonb,
    passive_compliance_score DOUBLE PRECISION,
    pressure_application_score DOUBLE PRECISION,
    showdown_threshold_score DOUBLE PRECISION,
    discipline_score DOUBLE PRECISION,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS core.field_snapshots (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL REFERENCES core.sessions(id) ON DELETE CASCADE,
    limp_density DOUBLE PRECISION,
    multiway_frequency DOUBLE PRECISION,
    donk_frequency DOUBLE PRECISION,
    showdown_stickiness DOUBLE PRECISION,
    chaos_index DOUBLE PRECISION,
    buyin_softness_index DOUBLE PRECISION,
    snapshot_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS core.surface_snapshots (
    id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL,
    session_id TEXT,
    surface_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    confidence_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
    generated_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS operator.operator_reviews (
    id TEXT PRIMARY KEY,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    review_type TEXT NOT NULL,
    decision TEXT NOT NULL,
    notes TEXT,
    review_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE INDEX IF NOT EXISTS operator_reviews_target_idx
ON operator.operator_reviews (target_type, target_id, review_type, created_at DESC);
