# TASK

Persist official GG tournament summary results and surface high-weight deep-run context after Hero uploads mixed hand-history / summary dumps.

# WHAT I CHANGED

- Added `TournamentResultRecord` as a canonical result-context model.
- Added `tournament_results` storage to SQLite and Postgres schemas.
- Added repository methods to upsert, fetch one, and fetch recent tournament results.
- Extended GG summary parsing to extract:
  - tournament id
  - title
  - buy-in
  - player count
  - prize pool
  - started time
  - Hero finish place
  - Hero total received
- Updated summary-only ingest so it still does not create fake sessions or fake hands, but it now persists official tournament result context.
- Updated duplicate summary handling so re-uploaded summary-only files can repair missing result rows instead of ending at duplicate skip.
- Added linked `result_context` to Review / Session Lab.
- Added `tournament_result_signals` to Brain so the product can detect top result outcomes across a dump, not only the latest session.
- Added `docs/tournament_result_truth.md`.
- Updated `DECISIONS_LOG.md` with the result-context truth rule.

# ARCHITECTURE IMPACT

This creates a separate official result truth layer without contaminating hand-level strategic evidence.

The important separation is now:

- raw source: GG hand history or GG tournament summary
- normalized session/hands: parsed decisions only when hand blocks exist
- official result context: tournament summary outcome linked by `player_id + tournament_id`
- derived interpretation: Review / Brain can prioritize deep runs while still separating execution from run-good

# DECISIONS MADE

- Summary-only exports remain `skipped_summary_only` for hand parsing.
- Official summary rows are still valuable and now persist as canonical result context.
- Big cash / top-three signals are high-weight review context, not automatic evidence that Hero played perfectly.
- Re-uploading duplicate summary files may upsert missing official result context using the existing ingest file as provenance.

# RISKS / OPEN QUESTIONS

- This does not yet calculate luck, EV, bounty EV, or ICM.
- Current `Top Result Signals` uses deterministic result heuristics: finish rank, cash amount, and ticket/entry text.
- The product can now say “this was a high-weight deep run,” but operator review still needs to mark which hands were repeatable execution versus run-good.

# OUT OF SCOPE

- Full tournament ROI dashboard.
- Exact PKO / bounty equity modeling.
- Hand-level EV attribution.
- Consumer-facing polish beyond exposing the new backend meaning in Review / Brain.

# TEST / VALIDATION

- `python3 -m py_compile core/parsing/gg_parser.py core/ingest/file_ingest.py core/storage/models.py core/storage/sqlite_repository.py core/storage/postgres_repository.py core/surfaces/session_lab.py`
- `python3 tests/v2_smoke_tests.py`
- Backfilled the newly uploaded summary ZIP locally. All 68 files were duplicate-skipped, but duplicate repair populated official result context.
- Verified tournament `6408385` persisted:
  - `Mini Thursday Throwdown $25 [Bounty], Hold'em No Limit`
  - `2nd place`
  - `$1,098.28`
  - `406` players
  - `$9,662.8` prize pool

# RECOMMENDED NEXT STEP

Next two approved tasks should be:

1. Build a Big-Win Review surface for tournament `6408385` that ranks the most important hands / evidence from that 296-hand run.
2. Add an operator correction workflow to tag deep-run spots as `repeatable_execution`, `run_good`, `cooler`, or `unclear` so Brain can learn from the win without overfitting to the result.
