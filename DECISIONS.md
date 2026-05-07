# DECISIONS

Durable product and architecture decisions. Append new decisions at the top with a date.

---

## 2026-05-05

**External beta production path: managed Postgres + Python backend service boundary.** For any real non-Hero beta user, canonical poker/player/session/memory truth must live in managed Postgres, and the existing Python interpretation engine should be exposed through an explicit backend service boundary such as FastAPI or a worker API. Next.js may remain the app shell, auth UI, and operator UI, but it must call this backend boundary instead of spawning `python3` during page render.

**Local SQLite + Python subprocess is dev/Hero-local only.** The current `execFile("python3", ...)` + `data/hero_v2.sqlite3` pattern remains acceptable for local Hero/operator iteration and deterministic smoke testing. It is not an external-beta architecture because it is not serverless-safe, does not handle concurrent users or writes cleanly, and hides backend failures behind page-render fallbacks.

**Do not rewrite derived poker logic in Node as the first production fix.** The Python parsing/evidence/memory/surface code is the strongest current backend asset. The first production migration should preserve that engine, wire it to Postgres, and expose typed read/write endpoints before considering any Node-side read-model optimization.

## Product

**OPB is post-hoc, not real-time.** Inputs are GG `.txt` session packets uploaded after play. The product reads, remembers, interprets, and proposes the next adjustment. It is not RTA, not a live advisor, not a hand-history browser, not a solver clone, not a stateless review tool.

**A GG `.txt` is a session packet.** Many hands, one session identity, contributes to cumulative per-player memory. Different files must not collapse into the same session. Duplicate files must not process twice. Zero-hand parses must not emit fake summaries.

**Three surfaces:** Today (next-session focus), Review (latest session story), Brain (long-term cumulative read). These are the MVP. Operator surfaces (`/operator/*`) sit alongside, not as user-facing product.

**Hero first.** Single-user backend hardening came before multi-user. Everything still defaults to Hero's player ID until real Supabase auth lands.

**Adjustment, not judgment.** Surfaces emphasize next adjustment direction over GTO grading. Positive execution memory is first-class alongside leak memory.

**Truth layers:** raw / normalized / derived / reviewed-overlay. Operator review never mutates source truth — overlays are separate and inspectable.

**Confidence-aware, not fake-precise.** Where exact ICM/PKO/satellite truth is unavailable, prefer explicit proxy language over fabricated certainty.

## Architecture

**Canonical store today is `data/hero_v2.sqlite3`.** Managed Postgres is the required canonical store before external beta. Vector/RAG is secondary retrieval only, not source of truth.

**Two module trees coexist:** `core/` (engine: parsing, evidence, memory, surfaces) and `app/api/` (operator-style API wrappers). Frontend reads via both. This is debt — should converge.

**Frontend → backend uses `execFile("python3", ...)`.** Each page render spawns Python and reads SQLite directly. Acceptable for single-user local dev; **not** deployable to serverless and not acceptable for external beta. The production path is a Python backend service boundary backed by managed Postgres.

**Auth provider: Supabase.** Canonical access tables (`user_accounts`, `user_player_access`, `user_global_roles`) live in the same SQLite as poker truth. Bootstrapping happens from env vars (`OPB_HERO_SUPABASE_USER_ID`, `OPB_OPERATOR_EMAILS`) on first authenticated request.

**Billing provider: Stripe.** Foundation only. Plans live in `frontend/lib/billing/plans.ts`. Current plan stored in `opb_plan` cookie. Checkout not yet implemented.

**LLMs are not source of truth.** They can summarize, explain, or coach in language layers, but never decide official scores or drive memory state.

## Process

**Agent handoff must preserve repo truth.** Claude and Codex may both work on this repo. The active source of truth is the repository, especially `AGENTS.md`, `PROJECT_MASTER_CONTEXT.md`, `WORKFLOW.md`, `DECISIONS_LOG.md`, `STATUS.md`, and task reports. Do not rely on chat memory alone.

**Compact entrypoints:** `README.md`, `STATUS.md`, and `DECISIONS.md` are quick-start summaries. They supplement, but do not replace, the canonical context docs and the report-first workflow.

---

## Historical decisions worth preserving

These were made earlier and remain in force unless superseded above.

- Tournament-scoped opponent identity. GG anonymized IDs are not valid cross-tournament keys; opponents are tournament-scoped ephemeral identity plus longer-horizon archetype memory.
- Smart HUD is snapshot/delta/trend based, not static cumulative.
- Hero analysis is decision-node and hand-class based, not result-only.
- Tournament segmentation, relevance weighting, and alpha surfaces read from canonical tables, not local JSON mirrors.
- AOF v1/v2, 13×13 matrix analysis, EV/actual-result analysis are first-class operator surfaces — they build Hero's personal baseline rather than testing GTO recall.
- Frontend was previously blocked until backend was trustworthy. As of 2026-05 the backend is trustworthy enough; frontend humanization is now in scope.
