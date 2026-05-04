# STATUS

Last updated: 2026-05-04

## What this is

OPB (One Percent Better Poker) is a post-hoc poker performance system for serious GG Poker Ontario MTT players. It ingests GG `.txt` session packets, builds cumulative per-player memory, and produces three surfaces: **Today** (next-session focus), **Review** (latest session story), **Brain** (long-term read).

First user is Hero (Chris). The product is operator-supervised: a small set of beta players upload sessions and receive interpretation; an operator approves applicants and reviews patterns.

## Where we are

**Backend (solid):** ingest -> evidence -> memory -> surfaces pipeline runs end-to-end. Canonical store is `data/hero_v2.sqlite3` with 553 sessions / 27,642 hands / 1,590 evidence rows / 43 memory items as of last sync. Smoke tests pass (`python3 tests/v2_smoke_tests.py`).

**Operator surfaces (working):** `/operator`, `/operator/matrix`, `/operator/aof`, `/operator/big-win`. Matrix has click-to-pin detail. AOF/Big Win have dedicated pages.

**Public surfaces (just rebuilt):** `/app/today`, `/app/review`, `/app/brain`, `/app` dashboard, `/app/account`. Were JSON dumps; now humanized UI with state badges, pattern cards, confidence bars, result rows.

**Auth (skeleton):** Supabase wired but env vars not set; canonical auth tables exist but empty. Hero runs through dev-login cookie. No external user has gone through end-to-end.

**Billing (foundation only):** Stripe config plumbing exists; checkout not implemented. Plan stored in `opb_plan` cookie; defaults to free_beta.

## Next concrete steps

In priority order (Claude is sole engineer; no Codex):

1. **Connect a real Supabase project** (env vars + first non-Hero account E2E test: signup → demo apply → operator approve → provision → upload → Today renders).
2. **Keep documentation aligned** (`STATUS.md` and `DECISIONS.md` are compact entrypoints; canonical docs and reports remain live).
3. **Remove `<pre>` JSON dumps from operator surfaces** (Matrix is fine; AOF and Big Win still have raw JSON in places — audit and humanize).
4. **Decide architecture for prod**: every page renders by spawning `python3` to read SQLite. Won't work on Vercel/serverless and won't survive concurrent users. Options: (a) FastAPI sidecar service, (b) move to Postgres + Node-side queries, (c) commit to local-only Hero tool. **Required before any external beta user.**
5. **Matrix operator approve/reject overlays** (was Codex's recommended Task 094). Lower priority than the above.
6. **Today/Review/Brain content quality**: backend produces honest output, but `headline` strings can still feel templated. Once #1 is real, revisit copy with actual user feedback.

## Out of scope right now

- Hand-level deep dives in Review (premium gate).
- Per-pattern timeline in Brain (premium gate).
- LLM-generated coaching language (deterministic only).
- Real-time / live assistance (this product is post-hoc by design).

## How to run

```bash
# backend smoke
python3 tests/v2_smoke_tests.py
python3 tests/legacy_corpus_tests.py

# frontend
cd frontend && npm install && npm run dev
# open http://localhost:3000

# build verify
cd frontend && npm run build
```

For dev-login (Hero impersonation): set `OPB_ENABLE_DEV_LOGIN=1` and visit `/auth/dev-login?role=operator`.

## Known gaps

- `user_accounts`, `user_player_access`, `user_global_roles`, `demo_applications` tables are all empty in current SQLite.
- No `.env` files in the repo. Auth env vars (`OPB_HERO_SUPABASE_USER_ID`, etc.) need to be configured per environment.
- Frontend → backend coupling uses `execFile("python3", ...)`. Acceptable locally; not deployable as-is.
- Tournament IDs hardcoded in some places (`6408385` for Big Win review default). Fine for Hero, surfaces if any other player joins.
- Two parallel module trees: `core/surfaces/*.py` and `app/api/*.py`. Boundary unclear. Worth merging.
