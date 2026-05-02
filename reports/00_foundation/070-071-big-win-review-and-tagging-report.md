# TASK

Implement Task 70 and Task 71:

- Task 70: Build a Big-Win Review surface for tournament `6408385`.
- Task 71: Add operator tagging for deep-run spots as `repeatable_execution`, `run_good`, `cooler`, or `unclear`.

# WHAT I CHANGED

- Added `core/surfaces/big_win_review.py`.
- Added deterministic candidate spot scoring for the `Mini Thursday Throwdown $25 [Bounty]` deep run.
- Linked the official result row to the 296-hand session through `tournament_id`.
- Added top candidate hand snippets with:
  - hand id
  - score
  - selection reasons
  - Hero actions
  - Hero summary
  - stack / board context where available
- Added `tag_big_win_spot(...)` to write operator tag overlays through `operator_reviews`.
- Added `getBigWinReview(...)` to the frontend Python bridge.
- Added operator-page UI for the big-win review and tag form.
- Added `docs/big_win_review_operator_loop.md`.
- Updated `DECISIONS_LOG.md` with the rule that big-win candidates must be tagged before becoming durable positive execution memory.
- Fixed a SQLite repository bug where `fetch_operator_reviews(...)` did not return rows after recent auth/operator work.

# ARCHITECTURE IMPACT

The deep-run workflow now follows the intended truth separation:

- official tournament result is canonical result context,
- hand-history session remains canonical decision source,
- candidate spots are deterministic derived review suggestions,
- operator tags are separate review overlays,
- durable Hero memory promotion remains a later explicit step.

This protects Brain from over-learning a run-good tournament while still letting the product recognize that the session matters.

# DECISIONS MADE

- Candidate scoring is deterministic and intentionally simple for MVP.
- Tags are stored as `operator_reviews` with `target_type = deep_run_spot`.
- Tags do not mutate raw hand records, session evidence, official results, or memory items.
- The first implementation is centered on tournament `6408385` because it is the newly confirmed high-weight Hero deep run.

# RISKS / OPEN QUESTIONS

- The current candidate scorer is not yet strategic-quality scoring. It prioritizes high-impact hands by all-in pressure, chip movement, Hero action, and result visibility.
- A hand tagged `repeatable_execution` does not yet automatically update positive execution memory.
- The operator UI is functional but visually rough; the user correctly noted the logged-in app needs a design pass after backend behavior is stable.

# OUT OF SCOPE

- EV / ICM / PKO luck calculation.
- Automatic promotion of tagged spots into memory.
- Full design refresh.
- Full hand replayer.

# TEST / VALIDATION

- `python3 -m py_compile core/surfaces/big_win_review.py core/surfaces/tournament_result_signals.py core/parsing/gg_parser.py core/ingest/file_ingest.py core/storage/sqlite_repository.py core/storage/postgres_repository.py`
- `python3 tests/v2_smoke_tests.py`
- `npm run typecheck`
- `npm run build`
- Verified `#6408385` big-win review is ready:
  - linked session: `gg20260424-0141-mini-thursday-throwdown-25-bounty`
  - candidate spots: `12`
  - top candidate hand: `TM101480097`
  - result: `2nd place`, `$1,098.28`
- Verified operator tag write/readback works, then removed the smoke-test tag so no fake operator judgment remains.

# RECOMMENDED NEXT STEP

Next two tasks:

1. Promote reviewed `repeatable_execution` tags into positive execution memory only after operator approval.
2. Run a focused design pass on logged-in `/app`, `/app/review`, `/app/brain`, and `/operator` so text contrast, hierarchy, and standout cards are much easier to read.
