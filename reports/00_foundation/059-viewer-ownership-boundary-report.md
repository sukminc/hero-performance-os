# Viewer Ownership Boundary Report

## TASK

Connect `frontend/lib/viewer/session.ts` to real auth identity resolution so the public shell enforces player ownership boundaries instead of always reading Hero data.

## WHAT I CHANGED

- replaced the hardcoded Hero viewer scope with auth-aware viewer resolution in `frontend/lib/viewer/session.ts`
- added env-driven Hero ownership mapping via:
  - `OPB_HERO_SUPABASE_USER_ID`
  - `OPB_HERO_SUPABASE_EMAIL`
  - `OPB_OPERATOR_SUPABASE_USER_IDS`
  - `OPB_OPERATOR_EMAILS`
- kept local dev-login fallback only when `OPB_ENABLE_DEV_LOGIN=1`
- changed public surface readers to require a resolved `playerId` instead of embedding a hardcoded Hero player id
- updated dashboard / Today / Review / Brain pages to show safe blank states when the auth identity is not mapped to a player ownership record
- updated operator page to read through the same viewer ownership resolution path
- refreshed active task docs to reflect the new beta-hardening focus

## ARCHITECTURE IMPACT

- the public shell now uses a viewer-ownership boundary before reading player-specific surfaces
- auth identity resolution remains an edge/frontend concern, while canonical poker truth still lives in the backend data model
- current implementation supports Hero-first beta hardening without pretending that a full multi-user player-account model already exists

## DECISIONS MADE

- chose explicit env-driven ownership mapping instead of inventing a premature database-backed account model
- treated unmapped authenticated users as authenticated-but-unscoped rather than implicitly falling back to Hero
- reused the same viewer resolution path for operator/public surfaces to avoid diverging access semantics

## RISKS / OPEN QUESTIONS

- operator route protection in `frontend/proxy.ts` still relies on the `opb_role` cookie and is not yet derived from verified Supabase claims
- full production auth hardening will still need a canonical user-to-player ownership table or equivalent backend truth source
- current Hero ownership mapping is intentionally Hero-first and will need a more general model before non-Hero onboarding

## OUT OF SCOPE

- full Supabase sign-in action wiring
- production-grade RBAC claims
- generalized multi-player ownership storage
- billing/checkout changes

## TEST / VALIDATION

- `cd frontend && npm run lint`
- `cd frontend && npm run build`

## RECOMMENDED NEXT STEP

Move operator route authorization off the display cookie and onto the same verified auth identity model, then define the smallest canonical user-to-player ownership record for post-Hero beta users.
