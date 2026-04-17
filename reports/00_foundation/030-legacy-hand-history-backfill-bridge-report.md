# TASK

Create the first V2 bridge that reuses the legacy local GG hand-history corpus from the old repo without depending on Supabase.

# WHAT I CHANGED

- Added `core/ingest/legacy_corpus.py` to discover raw GG `.txt` files inside the legacy local repo structure.
- Added `scripts/backfill_legacy_gg_corpus.py` to inventory or backfill the old corpus into the V2 ingest pipeline.
- Added `tests/legacy_corpus_tests.py` to validate discovery logic against a temporary fake corpus.
- Updated `docs/current_state.md` and `docs/runbook.md` so the next session can understand and run the backfill path quickly.

# ARCHITECTURE IMPACT

- V2 now has an explicit migration bridge from old local raw session files into canonical V2 ingest/evidence/memory truth.
- The bridge keeps the architecture aligned with the product direction:
  - raw corpus stays raw,
  - V2 parser replays the files,
  - V2 evidence and memory are rebuilt deterministically,
  - no Supabase dependency is required for this historical bootstrap path.

# DECISIONS MADE

- Preferred raw GG `.txt` replay over importing V1 derived summaries.
- Kept the bridge inventory-first by default and write-enabled only with `--apply`.
- Scoped the first bridge to the old local corpus, not cloud databases or Supabase state.

# RISKS / OPEN QUESTIONS

- Applying the backfill still requires a reachable Postgres `DATABASE_URL`.
- The old repo likely contains duplicate or debug archive trees; V2 duplicate-guard will help, but a later pass may still want stricter corpus curation.
- This packet does not yet expose the backfill flow inside the thin UI shell.

# OUT OF SCOPE

- Supabase migration
- importing V1 derived JSON as canonical V2 truth
- Review / Brain surface expansion
- operator UI for backfill management

# TEST / VALIDATION

- `python3 tests/legacy_corpus_tests.py`

# RECOMMENDED NEXT STEP

Run an inventory of the old corpus, then do a small `--apply --limit N` backfill into local Postgres and verify that Today / Command Center / Session Lab populate from real historical sessions.
