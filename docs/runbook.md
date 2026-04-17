# Runbook

## Smoke test

```bash
python3 tests/v2_smoke_tests.py
python3 tests/legacy_corpus_tests.py
```

Expected result:

- `V2 smoke tests passed.`

## Thin local shell

```bash
python3 app/dev_server.py
```

Then open:

- `http://127.0.0.1:8765`

## Legacy corpus inventory

This repo can reuse the old local GG hand-history archive from the previous repo.

Inventory only:

```bash
python3 scripts/backfill_legacy_gg_corpus.py
```

Inventory a specific old repo root:

```bash
python3 scripts/backfill_legacy_gg_corpus.py --old-repo-root /Users/chrisyoon/GitHub/opb-poker
```

Recommended canonical local SQLite path:

```bash
export SQLITE_DB_PATH=/Users/chrisyoon/GitHub/opb-poker/data/hero-v2/hero_v2.sqlite3
```

Apply the backfill into the configured V2 Postgres database:

```bash
python3 scripts/backfill_legacy_gg_corpus.py --apply
```

Apply only a small controlled batch:

```bash
python3 scripts/backfill_legacy_gg_corpus.py --apply --limit 10
```

## App entrypoints

- `python3 app/api/today.py`
- `python3 app/api/command_center.py`
- `python3 app/api/session_lab.py`
- `python3 app/api/memory_graph.py`

## Frontend public shell

Install:

```bash
cd frontend
npm install
```

Build check:

```bash
npm run build
```

## Launch ops references

Read before any limited beta release:

1. `docs/launch_readiness_checklist.md`
2. `docs/launch_ops_runbook.md`
3. `docs/private_beta_checklist.md`

## Resuming work later

Read in this order:

1. `README.md`
2. `docs/current_state.md`
3. `docs/active_task.md`
4. `docs/next_up.md`
5. `docs/master_plan.md`

Then inspect the files named in `docs/active_task.md` and continue that one task.

## Handoff rule

After every meaningful task:

1. write a report under `reports/`
2. update `docs/current_state.md` if the project state changed
3. update `docs/active_task.md` if the active task changed
4. update `docs/next_up.md` if the next task changed

Do not leave the repo in a state where the next session has to reconstruct the plan from chat memory.

## Notes

- This repo is local-first
- The smoke test uses an in-memory repository double, not live Postgres
- Live Postgres-backed integration checks can be added later once schema and scoring settle further
- The default storage backend is now SQLite, so backfill can run without a separate database server
- Set `V2_STORAGE_BACKEND=postgres` if you explicitly want Postgres
- Supabase is not required for the legacy hand-history path
- The current canonical local handoff doc is `docs/legacy_data_handoff.md`
