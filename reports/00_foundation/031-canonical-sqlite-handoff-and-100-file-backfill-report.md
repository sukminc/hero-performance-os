# TASK

Push the migration forward so the new V2 repo can keep using Hero's historical raw data without chat confusion, and fix one canonical local truth path for resumed work.

# WHAT I CHANGED

- fixed the canonical local V2 SQLite path to:
  - `/Users/chrisyoon/GitHub/opb-poker/data/hero-v2/hero_v2.sqlite3`
- ran a controlled 100-file historical backfill batch into that SQLite store
- added `docs/legacy_data_handoff.md` to make resume/handoff rules explicit for future chats
- updated `README.md`, `docs/current_state.md`, `docs/runbook.md`, `docs/active_task.md`, and `docs/next_up.md` so the project state matches reality

# ARCHITECTURE IMPACT

- the old repo is now clearly the raw-corpus source, not the active product repo
- the new repo is now clearly the V2 logic and surface repo
- the canonical local truth store for migration work is now a single SQLite file instead of an implied ephemeral DB

# DECISIONS MADE

- preferred one explicit SQLite path over temporary `/tmp` storage for resumed work
- kept replaying raw GG hand histories into V2 rather than importing V1 derived summaries
- moved reentry guidance to lead with handoff/state docs before broader architecture docs

# RISKS / OPEN QUESTIONS

- the full raw corpus has not been backfilled yet
- duplicate archive trees still exist in the old repo, so larger batches should keep being controlled and observed
- some sessions still generate only thin watch-stage memory, which is expected but limits Today aggressiveness

# OUT OF SCOPE

- full historical backfill
- Review / Brain expansion
- operator correction flows
- UI changes for migration control

# TEST / VALIDATION

- `python3 tests/legacy_corpus_tests.py`
- `python3 tests/v2_smoke_tests.py`
- `SQLITE_DB_PATH=/Users/chrisyoon/GitHub/opb-poker/data/hero-v2/hero_v2.sqlite3 python3 scripts/backfill_legacy_gg_corpus.py --apply --limit 100`
- `PYTHONPATH=. SQLITE_DB_PATH=/Users/chrisyoon/GitHub/opb-poker/data/hero-v2/hero_v2.sqlite3 python3 app/api/today.py`
- `PYTHONPATH=. SQLITE_DB_PATH=/Users/chrisyoon/GitHub/opb-poker/data/hero-v2/hero_v2.sqlite3 python3 app/api/command_center.py`

# RECOMMENDED NEXT STEP

Apply the next controlled historical batch, then inspect which memory items are nearing promotion so Review / Brain can start from real longitudinal signals rather than seed-level thin evidence.
