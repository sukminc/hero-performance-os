# Canonical Auth Bootstrap Implementation Report

## TASK

Implement the first runtime version of canonical ownership truth by adding auth/access tables, bootstrapping Hero/operator mappings into canonical rows, and making viewer resolution prefer canonical truth before env fallback.

## WHAT I CHANGED

- added canonical auth/access tables to the storage layer:
  - `user_accounts`
  - `user_player_access`
  - `user_global_roles`
- extended both SQLite and Postgres repositories with methods to:
  - upsert user accounts
  - upsert user-player access rows
  - upsert global operator roles
  - resolve user accounts by provider identity or email
  - fetch active player access and global roles
- added `core/auth/viewer_access.py` to:
  - bootstrap canonical auth rows from current Hero/operator env mapping
  - bootstrap the currently authenticated Supabase user into canonical truth when they match env-based Hero/operator mappings
  - resolve viewer access from canonical rows
- updated `frontend/lib/viewer/session.ts` so viewer resolution now:
  - checks canonical auth/access truth first through Python
  - returns canonical role/player scope when available
  - falls back only when canonical truth does not resolve the viewer
- refreshed handoff docs so the active task now moves on to durable demo lead capture

## ARCHITECTURE IMPACT

- auth/access truth is now a real backend layer instead of being only an env-driven frontend convention
- poker truth remains fully `player_id`-centric; the new auth layer only gates access to that truth
- the current Hero-first bridge remains usable, but it now seeds canonical auth rows rather than being the only source of truth

## DECISIONS MADE

- implemented the first canonical auth layer inside the existing storage backends instead of introducing a new service boundary
- kept canonical viewer resolution in Python so it can share the same repository logic as the rest of the backend
- preserved env fallback behavior for now, but only after canonical resolution is attempted
- kept the first model intentionally small: owner access, operator access, and one global operator_admin role

## RISKS / OPEN QUESTIONS

- SQLite stores the auth tables without schema namespaces while Postgres stores them under `auth.*`; the repository abstraction hides this, but future direct SQL usage must remember the difference
- the current bootstrap path is still Hero-first and assumes a single known Hero player id
- canonical auth rows are now seeded automatically, but there is not yet an operator-facing provisioning workflow for approved non-Hero users
- `npm run lint` remains affected by the existing generated `.next/types/validator.ts` issue and was not used as the success gate here

## OUT OF SCOPE

- self-serve onboarding
- durable lead capture backend
- claims/RBAC rollout
- billing/checkout changes
- broader multi-player ownership workflows

## TEST / VALIDATION

- `python3 -m py_compile core/auth/viewer_access.py core/storage/sqlite_repository.py core/storage/postgres_repository.py core/storage/models.py` ✅
- `python3 - <<'PY' ... resolve_viewer_access('supabase', None, None) ... PY` ✅ returned safe unscoped blank-state resolution
- `cd frontend && npm run build` ✅

## RECOMMENDED NEXT STEP

Replace the email-draft demo apply flow with durable lead capture, then connect approved-user intake to the new canonical ownership provisioning path without weakening the current blank-state safety.
