CREATE SCHEMA IF NOT EXISTS auth;

CREATE TABLE IF NOT EXISTS auth.user_accounts (
    id TEXT PRIMARY KEY,
    auth_provider TEXT NOT NULL,
    auth_provider_user_id TEXT NOT NULL UNIQUE,
    email TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    account_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT user_accounts_status_check CHECK (status IN ('active', 'disabled'))
);

CREATE UNIQUE INDEX IF NOT EXISTS user_accounts_email_unique_idx
ON auth.user_accounts (LOWER(email))
WHERE email IS NOT NULL;

CREATE TABLE IF NOT EXISTS auth.user_player_access (
    id TEXT PRIMARY KEY,
    user_account_id TEXT NOT NULL REFERENCES auth.user_accounts(id),
    player_id TEXT NOT NULL,
    access_role TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    granted_by_user_account_id TEXT REFERENCES auth.user_accounts(id),
    granted_reason TEXT,
    access_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT user_player_access_role_check CHECK (access_role IN ('owner', 'operator')),
    CONSTRAINT user_player_access_status_check CHECK (status IN ('active', 'revoked')),
    CONSTRAINT user_player_access_unique_active UNIQUE (user_account_id, player_id, access_role)
);

CREATE INDEX IF NOT EXISTS user_player_access_user_idx
ON auth.user_player_access (user_account_id, status, access_role);

CREATE INDEX IF NOT EXISTS user_player_access_player_idx
ON auth.user_player_access (player_id, status, access_role);

CREATE TABLE IF NOT EXISTS auth.user_global_roles (
    id TEXT PRIMARY KEY,
    user_account_id TEXT NOT NULL REFERENCES auth.user_accounts(id),
    role TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    granted_by_user_account_id TEXT REFERENCES auth.user_accounts(id),
    role_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT user_global_roles_role_check CHECK (role IN ('operator_admin')),
    CONSTRAINT user_global_roles_status_check CHECK (status IN ('active', 'revoked')),
    CONSTRAINT user_global_roles_unique_active UNIQUE (user_account_id, role)
);

CREATE INDEX IF NOT EXISTS user_global_roles_user_idx
ON auth.user_global_roles (user_account_id, status, role);

CREATE TABLE IF NOT EXISTS auth.demo_applications (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    games TEXT NOT NULL,
    help_goal TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new',
    source TEXT NOT NULL DEFAULT 'public_demo_apply',
    application_metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT demo_applications_status_check CHECK (status IN ('new', 'screening', 'approved', 'rejected', 'provisioned'))
);

CREATE INDEX IF NOT EXISTS demo_applications_status_idx
ON auth.demo_applications (status, created_at DESC);

CREATE INDEX IF NOT EXISTS demo_applications_email_idx
ON auth.demo_applications (LOWER(email), created_at DESC);

-- Bootstrap seed pattern for Hero-first beta:
-- 1. insert Hero into auth.user_accounts
-- 2. insert Hero owner mapping into auth.user_player_access
-- 3. insert operator/admin accounts into auth.user_accounts
-- 4. insert explicit operator -> Hero access rows into auth.user_player_access
-- 5. insert operator_admin rows into auth.user_global_roles
