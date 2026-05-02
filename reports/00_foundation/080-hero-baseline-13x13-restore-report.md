# Task 80: Hero Baseline 13x13 Restore

## TASK

Restore the 13x13 hand-class actual BB matrix into the current Next/operator product surface so Hero can inspect practical hand performance such as `66`.

## WHAT I CHANGED

- Added `getHeroBaselineMatrix(...)` to the public surface read bridge.
- Reused the existing deterministic `app.api.hand_matrix.get_hand_matrix_payload(...)` implementation.
- Added a Hero Baseline section to `/operator`.
- Defaulted the selected-hand spotlight to `66`.
- Rendered all-history observations, distinct hand classes, selected-hand average BB/hand, actual BB net, suspicious hands, full 13x13 matrix, and selected-hand position breakdown.
- Added CSS for matrix cells, tone colors, and compact baseline rows.
- Added `docs/hero_baseline_13x13_matrix.md`.

## ARCHITECTURE IMPACT

This restores an existing derived surface without changing canonical storage or parser truth.

It keeps the matrix as deterministic actual-result analysis, not solver EV or all-in adjusted EV. The surface now fits the Hero Baseline product family and gives AOF a broader hand-class result companion.

## DECISIONS MADE

- Default selected hand is `66` because Hero explicitly called it out as the type of hand he wants to inspect.
- The matrix uses `window='all'` for baseline inspection instead of only recent 90 days.
- Raw actual BB result is visible, but the UI labels it carefully as actual result only.
- Suspicious hands are shown as a study queue rather than final truth.

## RISKS / OPEN QUESTIONS

- Actual BB result can be distorted by antes, coolers, all-in runouts, and tournament format.
- The old hand-matrix implementation still reads SQLite directly through `app/api/hand_matrix.py`; a future cleanup should move it into `core/surfaces`.
- The current product read does not yet isolate stack band plus decision node for each suspicious combo.

## OUT OF SCOPE

- No new database schema.
- No solver chart ingestion.
- No all-in adjusted EV.
- No operator approve/reject overlay for matrix cards yet.
- No consumer-facing Baseline page yet.

## TEST / VALIDATION

Run:

- `python3 -m py_compile app/api/hand_matrix.py`
- `npm run typecheck` from `frontend/`
- `npm run build` from `frontend/`

## RECOMMENDED NEXT STEP

Proceed with Task 81:

Turn suspicious 13x13 hands into Hero Baseline insight cards by joining hand class, position, stack band, first action, faced action, format, and examples.
