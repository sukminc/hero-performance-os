# 052 Auth Provider And App Shell Foundation Report

## TASK

Choose the auth provider for the public MVP and scaffold the first authenticated app shell with protected routes.

## WHAT I CHANGED

- chose `Supabase Auth` as the Phase 1 provider
- added a new `frontend/` Next.js app shell scaffold
- added public routes:
  - `/`
  - `/login`
  - `/signup`
  - `/pricing`
- added protected shell routes:
  - `/app`
  - `/app/upload`
  - `/app/today`
  - `/app/review`
  - `/app/brain`
  - `/app/account`
- added operator placeholder route:
  - `/operator`
- added Supabase environment scaffold in `frontend/.env.example`
- added middleware-based route protection and operator-role gating
- added `docs/phase_1_auth_foundation.md`

## ARCHITECTURE IMPACT

- introduces the first real public-app code path without mutating canonical poker truth
- keeps auth as an edge concern while preserving backend truth boundaries
- creates a stable route map so future upload and interpretation work can be layered without navigation churn

## DECISIONS MADE

- Supabase Auth is the chosen Phase 1 provider
- public MVP app shell will live under `frontend/`
- route protection is enforced in middleware
- operator gating is separate from normal authenticated access

## RISKS / OPEN QUESTIONS

- live auth actions are not wired yet
- cookie naming may need refinement once the exact Supabase auth flow is implemented
- user-to-player linking is still a later phase
- this scaffold does not yet prove production deploy readiness

## OUT OF SCOPE

- upload pipeline
- Today / Review / Brain public reads
- billing
- account-to-player linking

## TEST / VALIDATION

- static scaffold created
- route structure and auth config files exist
- middleware protection logic exists
- build/install validation still requires frontend dependencies to be installed

## RECOMMENDED NEXT STEP

Install frontend dependencies, wire real Supabase login/signup actions, and verify the protected shell locally before starting Phase 2 upload service work.
