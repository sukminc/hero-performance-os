# Task 096: Production Architecture Decision For External Beta

## TASK

Decide how OPB should read and write canonical poker truth before any real external beta user is added.

## WHAT I CHANGED

- Audited the current frontend-to-backend paths.
- Documented the production architecture decision in `DECISIONS.md`.
- Added the fixed decision to `DECISIONS_LOG.md`.
- Updated `STATUS.md` so the next concrete steps no longer treat the production path as undecided.
- Updated `docs/next_up.md` with the next implementation packet.

## ARCHITECTURE IMPACT

The selected path is managed Postgres plus an explicit Python backend service boundary.

Next.js remains the app shell, public/app UI, auth UI, and operator UI. It should not spawn `python3` during page render for external beta traffic. The existing Python engine remains the source of parsing, evidence, memory, and derived surface behavior, but it must be called through a service/API boundary and backed by managed Postgres.

The local SQLite plus Python subprocess path remains valid only for Hero-local development, deterministic smoke tests, corpus migration, and operator iteration before external beta.

## DECISIONS MADE

- Choose managed Postgres as the external-beta canonical store.
- Choose a Python backend service boundary, such as FastAPI or a worker API, as the first production boundary.
- Preserve the current Python interpretation engine rather than rewriting derived poker logic in Node.
- Treat direct `execFile("python3", ...)` page-render reads as dev-only.
- Prove the migration with one vertical slice before migrating every surface.

## RISKS / OPEN QUESTIONS

- `core/storage/postgres_repository.py` exists but may not yet cover every method used by all current surfaces and operator actions.
- Some `app/api/*` modules still query SQLite directly through `get_sqlite_connection()`, so they must either move through `V2Repository` or be replaced by service endpoints.
- The service host, deployment target, auth token strategy, and local run command still need implementation.
- Supabase remains auth/provider plumbing only; it must not become canonical player/session/memory truth.

## OUT OF SCOPE

- No broad frontend polish.
- No billing checkout implementation.
- No external beta Supabase project wiring.
- No all-surface migration in this task.
- No Node-side rewrite of poker interpretation logic.

## TEST / VALIDATION

- Repository audit confirmed current direct Python subprocess paths in:
  - `frontend/lib/public-surfaces/read.ts`
  - `frontend/lib/viewer/session.ts`
  - `frontend/lib/uploads/ingest.ts`
  - `frontend/lib/uploads/status.ts`
  - `frontend/lib/operator/demo-applications.ts`
  - `frontend/app/operator/demo-actions.ts`
  - `frontend/app/demo-apply/actions.ts`
- Audit confirmed direct SQLite reads remain in selected Python API wrappers:
  - `app/api/field_ecology.py`
  - `app/api/hand_matrix.py`
  - `app/api/hud_trend.py`
- Documentation-only change; no backend or frontend test suite was required for behavioral validation.

## RECOMMENDED NEXT STEP

Execute Task 097: create a backend service boundary skeleton for one vertical slice, preferably Today or operator Matrix, with a service endpoint that returns the same payload shape as the existing Python function and a Next.js helper that uses the service when configured while preserving local dev fallback.
