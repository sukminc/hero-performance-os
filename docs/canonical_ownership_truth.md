# Canonical Ownership Truth

## Purpose

Define the smallest durable auth/access truth layer that can replace Hero-first env mapping without polluting canonical poker truth.

This layer should answer:

- which authenticated human is this?
- which player model can they access?
- are they an owner or an operator?
- should they resolve any player data at all?

It should not answer:

- what poker interpretation is true?
- what memory items exist?
- what Today / Review / Brain outputs are true?

Those remain in canonical poker tables keyed by `player_id`.

## Core Rule

Do not move poker truth into auth tables.
Do not move auth ambiguity into poker tables.

The ownership/auth layer should be a thin access boundary in front of the existing `player_id`-centric backend.

## Design Goals

1. preserve current Hero-first behavior safely
2. support one-player-per-user first
3. support operator/admin review without exposing Hero data accidentally
4. keep unmapped users safely unscoped
5. avoid schema decisions that would need rework when post-Hero beta starts

## Smallest Useful Entity Set

### `auth.user_accounts`

One row per authenticated human account.

Purpose:

- stable internal account id
- map external auth provider identity into durable local truth
- hold account lifecycle state

Required fields:

- internal `id`
- `auth_provider`
- `auth_provider_user_id`
- normalized `email`
- `status`
- `created_at`
- `updated_at`

This is not a poker table.
It is an identity table.

### `auth.user_player_access`

One row per user-to-player relationship.

Purpose:

- declare which player a user may access
- declare whether they are the owner or a non-owner reviewer
- provide the single canonical ownership/access lookup for public shell reads

Required fields:

- internal `id`
- `user_account_id`
- `player_id`
- `access_role`
- `status`
- `granted_by_user_account_id`
- `granted_reason`
- `created_at`
- `updated_at`

Recommended first allowed `access_role` values:

- `owner`
- `operator`

Recommended first allowed `status` values:

- `active`
- `revoked`

This is the key bridge table.

### `auth.user_global_roles`

One row per user/global-role assignment.

Purpose:

- answer whether a user may enter operator-only routes at all
- keep global operator/admin rights separate from player-specific ownership

Required fields:

- internal `id`
- `user_account_id`
- `role`
- `status`
- `granted_by_user_account_id`
- `created_at`
- `updated_at`

Recommended first allowed `role` values:

- `operator_admin`

Recommended first allowed `status` values:

- `active`
- `revoked`

This table should stay small.
Do not turn it into a generic permissions matrix yet.

## Why Three Tables, Not More

This is the smallest split that keeps the truth clean:

- `user_accounts` answers identity
- `user_player_access` answers ownership/player-scoped access
- `user_global_roles` answers global operator/admin access

If global operator rights are stored only in `user_player_access`, the model gets muddy when an operator needs to inspect multiple players.
If ownership is stored only in `user_accounts`, one-user-one-player becomes too rigid and later expansion becomes awkward.

## What Stays Out Of Scope

Do not add these yet:

- coach sharing
- many role types
- team/workspace/org models
- billing entitlements in the same tables
- fine-grained per-surface permissions
- row-level policy complexity beyond the minimum needed for safe reads

## Access Resolution Rules

### Public authenticated surfaces

To resolve `/app`, `/app/today`, `/app/review`, `/app/brain`, `/app/upload`:

1. resolve authenticated user from hosted auth provider
2. look up `auth.user_accounts`
3. look up active `auth.user_player_access`
4. if one active `owner` row exists, use that `player_id`
5. if no active owner row exists, return authenticated-but-unscoped blank state

### Operator routes

To resolve `/operator`:

1. resolve authenticated user from hosted auth provider
2. look up `auth.user_accounts`
3. require active `auth.user_global_roles.role = operator_admin`
4. if absent, redirect away from operator routes

### Operator viewing a player

Operator player access should still be explicit.

Recommended first rule:

- operator/admin may access operator routes globally
- operator player inspection still resolves through `auth.user_player_access`
- first implementation may seed a broad operator-to-Hero access row explicitly rather than implying universal player access

This preserves auditability.

## Migration Path From Current Env Mapping

### Phase 1. Mirror current truth

Seed:

- one `user_accounts` row for Hero
- one `user_accounts` row for each operator/admin
- one `user_player_access` row mapping Hero user -> Hero player as `owner`
- one `user_player_access` row per operator -> Hero player as `operator`
- one `user_global_roles` row per operator/admin

Current env variables remain allowed only as bootstrap input.

### Phase 2. Read canonical truth first

Viewer resolution should:

1. prefer canonical auth tables
2. fall back to env mapping only if canonical rows are absent
3. preserve blank-state behavior for unmapped users

### Phase 3. Remove env fallback

After bootstrap rows are stable:

- stop reading Hero/operator mappings from env
- keep only generic auth env needed for provider configuration

## Why This Fits Repo Rules

- it models by entities, not vendors
- it keeps auth/access separate from poker truth
- it preserves `player_id` as the canonical join key for poker memory/surfaces
- it does not pretend Supabase is the canonical source of poker truth
- it strengthens operator review without weakening ownership boundaries

## First Implementation Notes

The first implementation should keep the backend assumptions simple:

- one active owner per user
- one primary player per public beta user
- zero implicit ownership when mapping is missing
- explicit operator grants only

The viewer context contract can stay close to the current shape:

- `role`
- `playerScope`
- `playerId`
- `canSeeOperatorDepth`
- `ownershipResolved`
- `ownershipSource`

Only the source of truth changes.

## Acceptance Criteria

This ownership model is good enough for first implementation if it allows:

- Hero to see Hero data
- operator/admin to access operator routes
- operator/admin to inspect Hero explicitly
- unmapped authenticated users to remain blank/unscoped
- future non-Hero beta users to be added without env edits
