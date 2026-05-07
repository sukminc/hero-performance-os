# Task 107: Matrix Runout Trend Windows

## TASK

Add Last 7 days / Last 30 days / All history trend windows to the Matrix runout-noise guardrail section.

## WHAT I CHANGED

- Added `runout_noise_trends` to the Matrix payload.
- Each trend window includes:
  - key,
  - label,
  - latest parsed hand anchor,
  - parsed hand count,
  - runout-noise cards,
  - truth policy.
- Added a client-side tab component for `/app/matrix` and `/operator/matrix`.
- The section now defaults to `Last 7 days` so recent painful premium-hand outcomes are not buried under all-history volume.
- Kept `runout_noise_cards` as the all-history compatibility field.
- Added regression coverage that old `KK` pain stays in All history but does not leak into Last 7 when outside the recent window.

## ARCHITECTURE IMPACT

This remains a derived Matrix read model. No canonical hand truth, memory, Today, Brain, or operator overlay state is mutated.

Trend windows are anchored to the latest parsed hand timestamp inside the current Matrix payload rather than wall-clock time. This makes local and uploaded session review stable even when the underlying corpus is older than the current calendar date.

## DECISIONS MADE

- Recent runout pain should have its own view because all-history baselines can emotionally and analytically dilute what Hero just experienced.
- The UI should expose all three windows in one section rather than forcing a full page/filter reload.
- The default tab is `Last 7 days`.

## RISKS / OPEN QUESTIONS

- This is still actual-result proxy interpretation, not all-in adjusted EV.
- If uploaded files have incorrect or missing timestamps, recent-window behavior depends on the parser timestamp quality.
- The next stronger version should add an actual EV/equity calculator for preflop all-ins where showdown cards are available.

## OUT OF SCOPE

- No solver/GTO comparison.
- No persisted trend snapshots.
- No chart visualization yet.
- No operator cooler/misplay tagging workflow.

## TEST / VALIDATION

- `python3 -m py_compile app/api/hand_matrix.py`
- `python3 tests/matrix_position_situation_tests.py`
- `python3 tests/matrix_quiz_tests.py`
- `npm run build` in `frontend`

Local corpus trend check:

- Last 7: 3,118 parsed hands, including `QQ · open_raise`, `AKo · open_raise`, `KK · three_bet`, `KK · open_raise`.
- Last 30: 9,043 parsed hands.
- All history: 27,280 parsed hands.

## RECOMMENDED NEXT STEP

Add a compact trend chart that shows whether a protected hand is a recent pain spike, a long-term neutral pattern, or a repeated all-history problem.
