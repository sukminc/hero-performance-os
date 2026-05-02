# Canonical Ownership Truth Plan Report

## TASK

Design and document the smallest canonical user-to-player ownership and operator authorization truth layer that can replace Hero-first env mapping without corrupting canonical poker truth.

## WHAT I CHANGED

- added `docs/canonical_ownership_truth.md` to define the minimum durable auth/access entity model
- added `docs/sql_drafts/canonical_ownership_truth.sql` with a minimal Postgres-oriented schema draft for:
  - `auth.user_accounts`
  - `auth.user_player_access`
  - `auth.user_global_roles`
- updated `docs/auth_and_access_architecture.md` to align the broader access architecture with this more concrete ownership-truth model

## ARCHITECTURE IMPACT

- the proposed design keeps poker truth keyed by `player_id` in canonical backend tables and adds only a thin identity/access boundary in front of it
- ownership and operator authorization are separated cleanly:
  - player-scoped access lives in `auth.user_player_access`
  - global operator/admin route access lives in `auth.user_global_roles`
- this avoids baking Hero-first env mapping into the long-term product model while still preserving the current safe blank-state behavior

## DECISIONS MADE

- chose three small auth/access tables instead of a larger generalized account model
- kept one-player-per-user as the initial public-beta assumption
- kept operator/admin rights separate from ownership so operator routing does not become entangled with player ownership semantics
- chose documentation plus SQL draft first instead of immediately mutating runtime schema, because this step changes durable truth boundaries and should be reviewed before implementation

## RISKS / OPEN QUESTIONS

- `player_id` currently lives in canonical poker tables without a dedicated `players` table in the repo schema; implementation may either introduce a true `core.players` table or continue treating player ids as externally seeded canonical identifiers for one more phase
- the first implementation still needs a bootstrap path that mirrors current env truth into canonical auth rows safely
- if future beta needs coach/shared access quickly, `user_player_access` can absorb it, but the first shipped version should resist adding more roles early

## OUT OF SCOPE

- runtime migration/application of the schema
- viewer-resolution code changes to read the new tables
- Supabase RLS or claims rollout
- demo lead capture backend
- billing integration changes

## TEST / VALIDATION

- verified current backend truth remains `player_id`-centric in `core.storage.schema.sql`
- verified current frontend viewer model can consume canonical ownership truth later without changing its public contract materially
- verified the proposed schema preserves safe handling for unmapped authenticated users

## RECOMMENDED NEXT STEP

Implement the bootstrap path and read order:

1. add the canonical auth tables
2. seed Hero/operator rows from current env mapping
3. update viewer resolution to prefer canonical auth rows and fall back to env only when canonical rows are absent
4. keep unmapped users blank/unscoped until explicit access is granted
