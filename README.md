# OPB — One Percent Better Poker

Post-hoc poker performance system for serious GG Poker Ontario MTT players.
First user is Hero. Inputs are GG `.txt` session packets.
Outputs are three surfaces: **Today**, **Review**, **Brain**.

## Read these first

- [`AGENTS.md`](AGENTS.md) — operating rules for implementation agents.
- [`STATUS.md`](STATUS.md) — current state, what's done, what's next.
- [`DECISIONS.md`](DECISIONS.md) — durable product and architecture decisions.
- [`PROJECT_MASTER_CONTEXT.md`](PROJECT_MASTER_CONTEXT.md), [`WORKFLOW.md`](WORKFLOW.md), and [`DECISIONS_LOG.md`](DECISIONS_LOG.md) — canonical product/workflow context.
- [`docs/`](docs/) — reference specs, runbooks, active task packets, and planning material.

`STATUS.md` and `DECISIONS.md` are compact entrypoints. They do not replace the canonical context docs or the report requirement in `WORKFLOW.md`.

## Run

```bash
# Backend smoke
python3 tests/v2_smoke_tests.py
python3 tests/legacy_corpus_tests.py

# Frontend (Next.js)
cd frontend
npm install
npm run dev          # http://localhost:3000
npm run build        # build verify
```

Dev login (Hero impersonation): set `OPB_ENABLE_DEV_LOGIN=1` and visit `/auth/dev-login?role=operator`.

## Layout

```
core/         Python engine: parsing, evidence, memory, surfaces
app/api/      Operator-facing Python API wrappers (legacy split — see DECISIONS.md)
frontend/     Next.js app — public surfaces + operator console
data/         SQLite canonical store (hero_v2.sqlite3)
docs/         Reference specs, active task packets, and runbooks
tests/        Smoke + legacy corpus tests
```

## Surfaces

**Public** (`/app/*`):
- `/app/today` — next-session focus and patterns being watched.
- `/app/review` — latest session story, official tournament result, evidence breakdown.
- `/app/brain` — long-term cumulative read, hero standard, persistent pressures, deep-run results.
- `/app/upload` — drop GG `.txt` or `.zip` packets.
- `/app/account` — plan and access scope.

**Operator** (`/operator/*`, gated):
- `/operator` — control room with demo applications + headline matrix preview.
- `/operator/matrix` — Hero baseline 13×13 with click-to-pin detail.
- `/operator/aof` — AOF analysis (short-stack decision quality).
- `/operator/big-win` — repeatable execution review for high-weight tournaments.

## Product rule

OPB answers six things over time:

- which hand classes are underperforming
- where Hero is drifting
- what stable strengths are holding or regressing
- what field distortions characterize the current pool
- where adaptation is becoming contamination
- what the next best adjustment is
