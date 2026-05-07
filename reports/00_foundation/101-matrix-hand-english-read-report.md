# Task 101: Matrix Hand English Read

## TASK

Make the Matrix pinned detail easier to understand by attaching a short deterministic English interpretation to every hand class.

## WHAT I CHANGED

- Added `english_read` to each `matrix_cells[hand_class]`.
- Added `english_read` to selected-hand Matrix `detail`.
- Added deterministic hand-read logic that identifies:
  - the main working spot,
  - the main losing spot,
  - whether the hand should be kept as baseline, reviewed by subset, protected as value, watched, or treated as insufficient sample.
- Added a baseline guardrail for core playable hands such as pairs, suited broadways, strong Ax, and nearby broadways.
- Updated `/operator/matrix` pinned detail so the English read appears above the position/situation table.
- Reduced the primary position/situation table from 8 rows to 5 rows to make the screen easier to scan.
- Removed the compact 3bet summary block from the primary pinned-card flow; sizing remains visible inside the position/situation table.
- Added tests that ensure a QJs-style BB call loss becomes a review action, not an automatic range-cut instruction.
- Updated Matrix docs and decision log with the actual-result vs solver-EV framing.

## ARCHITECTURE IMPACT

The Matrix remains deterministic derived truth. No LLM output becomes canonical scoring or state.

The new `english_read` is a derived explanation layer over existing Matrix facts. It does not mutate hands, sessions, Today, Brain, or memory.

## DECISIONS MADE

- The primary product question is now: "What should I review next for this hand?"
- The UI should lead with interpretation before showing the diagnostic table.
- Actual-result underperformance should be separated from solver/range conclusions.
- For hands like `QJs`, BB call losses should say to review the BB defend subset, especially larger opens or multi-caller pots, before changing the preflop baseline.
- Tiny jam/all-in rows are visible but explicitly excluded from baseline decisions until repeated.

## RISKS / OPEN QUESTIONS

- The core-baseline hand list is deterministic and conservative, but still a v1 heuristic.
- The read does not yet inspect postflop line quality, so it can identify where to review but not why the hand lost postflop.
- "3x+ open" detection depends on current open-size extraction quality.
- Later product versions may want an operator-approved override for hand-read language.

## OUT OF SCOPE

- No solver/GTO comparison.
- No exact EV or all-in adjusted EV.
- No membership/upload gating.
- No quiz changes in this slice.
- No automatic Today, Brain, or memory promotion from Matrix reads.

## TEST / VALIDATION

- `python3 -m py_compile app/api/hand_matrix.py`
- `python3 tests/matrix_position_situation_tests.py`
- `python3 tests/service_boundary_tests.py`
- `python3 tests/matrix_quiz_tests.py`
- `python3 tests/v2_smoke_tests.py`
- `npm run build`
- Local QJs payload smoke check returns:
  - headline: `QJs: keep the baseline, review BB defend results`
  - next action: `Keep normal single-raised-pot BB defend baseline; review the losing BB call examples first.`
  - next action: `Filter BB calls facing 3x+ opens and multi-caller pots before changing the range.`

## RECOMMENDED NEXT STEP

Review the QJs examples listed under `BB · Call vs open`, then decide whether the next Matrix slice should add one-click example drill-down for those rows.
