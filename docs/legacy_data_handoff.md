# Legacy Data Handoff

## Purpose

This document fixes the canonical local bridge between:

- the old raw GG hand-history corpus in `opb-poker`
- the standalone V2 repo `hero-performance-os`

Use this file when resuming from a new chat so the migration context does not have to be reconstructed from memory.

## Canonical local paths

Old raw corpus root:

- `/Users/chrisyoon/GitHub/opb-poker`

Canonical local V2 SQLite file:

- `/Users/chrisyoon/GitHub/opb-poker/data/hero-v2/hero_v2.sqlite3`

This SQLite file is the current local canonical V2 store for legacy backfill work.

## What has already been done

- V2 storage now supports SQLite by default.
- Legacy corpus discovery now filters for real raw GG hand-history files that actually contain `Poker Hand #`.
- The full currently discovered historical corpus replay has been applied into the canonical SQLite file above.

## Verified current state

After the full discovered-corpus replay:

- Command Center reads real cumulative memory
- Today reads real cumulative memory
- Session Lab reads real backfilled sessions

Observed from the verified full replay:

- `5531` selected raw files
- `268` unique ingested sessions
- `5263` duplicate-skipped files
- `18442` hands in canonical V2 storage
- `1039` session evidence rows
- `34` cumulative memory items
- current Today state reached `stable`
- current Today headline:
  - `Baseline is holding. Carry session_survival_discipline forward without over-adjusting.`

## Required env when resuming

Always set:

```bash
export PYTHONPATH=.
export SQLITE_DB_PATH=/Users/chrisyoon/GitHub/opb-poker/data/hero-v2/hero_v2.sqlite3
```

Optional:

```bash
export V2_STORAGE_BACKEND=sqlite
```

## Resume commands

Inventory the old raw corpus:

```bash
python3 scripts/backfill_legacy_gg_corpus.py --limit 20
```

Replay the full currently discovered corpus again safely:

```bash
python3 scripts/backfill_legacy_gg_corpus.py --apply
```

Read current surfaces:

```bash
python3 app/api/today.py
python3 app/api/command_center.py
python3 app/api/session_lab.py
python3 app/api/memory_graph.py
```

Run the thin shell:

```bash
python3 app/dev_server.py
```

## Working rule

When continuing from another chat:

1. treat the SQLite file above as the current V2 truth store
2. treat the old repo only as the raw corpus source
3. keep replaying raw hand histories into V2 rather than importing V1 derived summaries
4. expect duplicate archives to be skipped safely on replays
5. update this file if the canonical DB path or replay status changes
