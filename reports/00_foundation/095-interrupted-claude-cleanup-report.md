# Task 095: Interrupted Claude Cleanup

## TASK

Clean up the repository after Claude stopped mid-run with a large mixed working tree.

## WHAT I CHANGED

- Restored deleted canonical root docs:
  - `AGENTS.md`
  - `PROJECT_MASTER_CONTEXT.md`
  - `WORKFLOW.md`
  - `DECISIONS_LOG.md`
- Restored deleted live docs and historical report files in their original locations.
- Removed interrupted-agent noise:
  - `.claude/`
  - `docs/_archive/`
  - `reports/_archive/`
- Added `.claude/` to `.gitignore`.
- Kept useful compact docs:
  - `STATUS.md`
  - `DECISIONS.md`
- Edited `README.md`, `docs/README.md`, `STATUS.md`, and `DECISIONS.md` so compact docs supplement rather than replace canonical repo truth.
- Updated `docs/active_task.md`, `docs/current_state.md`, and `docs/next_up.md` to reflect the cleanup state and next architecture decision.

## ARCHITECTURE IMPACT

No schema, parser, or runtime architecture changed.

This cleanup preserves repository truth boundaries. The useful Claude UI/product changes remain available for review, while the risky deletion/archive rewrite has been undone.

## DECISIONS MADE

- Do not accept deletion of canonical docs or report history.
- Do keep `STATUS.md` and `DECISIONS.md` as compact entrypoints.
- Do not accept `Codex no longer used` or `reports dropped` as durable process truth.
- Treat production architecture for external beta as the highest-priority next decision because frontend reads still depend on local SQLite plus Python subprocesses.

## RISKS / OPEN QUESTIONS

- Remaining implementation changes still need review as a coherent batch.
- Frontend humanization work may need browser verification.
- External beta remains blocked until the production truth architecture is decided.

## OUT OF SCOPE

- No commit was made.
- No user-facing product behavior was intentionally changed by this cleanup.
- No production architecture implementation was attempted.

## TEST / VALIDATION

- Passed `python3 tests/v2_smoke_tests.py`.
- Passed `python3 tests/legacy_corpus_tests.py`.
- Passed `npm run build`.

## RECOMMENDED NEXT STEP

Review the remaining implementation diff. Since validation passes, decide whether to commit the cleaned batch as one checkpoint or split it into smaller commits.
