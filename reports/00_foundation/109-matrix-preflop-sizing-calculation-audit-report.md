# Task 109: Matrix Preflop Sizing Calculation Audit

## TASK

Audit the Matrix preflop open and 3bet sizing calculations because the displayed values did not match Hero's felt baseline of mostly 2x opens and 6bb 3bets versus 2x opens.

## WHAT I CHANGED

- Audited backend sizing rows directly from parsed `HandObservation` objects.
- Confirmed open average `2.13x` is mathematically correct, but incomplete as a product read without mode/median.
- Added open size mode and median to the sizing summary.
- Found that raw 3bet average `9.01x` was misleading because it included near-all-in / 20bb+ pressure raises.
- Added near-all-in / 20bb+ 3bet exclusion for sizing-discipline metrics.
- Updated the top Matrix card to show clean `3bet vs 2x` instead of raw all-context 3bet average.
- Added backend regression coverage so near-all-in 3bets do not pollute clean 3bet sizing.
- Updated docs and decisions.

## ARCHITECTURE IMPACT

No raw hand truth changed. This changes the derived Matrix read model so sizing discipline is separated from all-in pressure outcomes.

The backend now preserves:

- raw 3bet count,
- raw average 3bet size,
- near-all-in excluded count,
- clean 3bet average,
- clean single-2x-open 3bet average and mode.

## DECISIONS MADE

- Open sizing should show average plus mode/median. Average alone can hide Hero's actual 2x habit.
- 3bet sizing discipline should exclude:
  - `hero_3bet_size_bb >= 20`, or
  - `hero_3bet_size_bb >= 80%` of starting stack.
- The first-value UI should emphasize `3bet vs 2x` because that matches Hero's actual tactical question.

## RISKS / OPEN QUESTIONS

- Some GG lines that are effectively all-in may still be represented as `raise` rather than `jam` in raw text. The new exclusion handles this for sizing, but the parser taxonomy should later classify these as all-in-like actions more explicitly.
- There may be edge cases where a legitimate deep-stack large 3bet is above 20bb, but for the sizing-discipline dashboard it is better excluded than mixed into the standard 6bb/7bb question.

## OUT OF SCOPE

- No full preflop parser taxonomy rewrite.
- No per-hand raw action viewer.
- No solver sizing comparison.

## TEST / VALIDATION

- `python3 -m py_compile app/api/hand_matrix.py`
- `python3 tests/matrix_position_situation_tests.py`
- `python3 tests/matrix_quiz_tests.py`
- `npm run build` in `frontend`
- `npm run qa:matrix:render` in `frontend`
- In-app browser reload showed zero console errors.

Backend audit results:

- Standard open count: `3032`
- Open average: `2.13x`
- Open mode: `2.0x`
- Open median: `2.0x`
- 2x open rate: `82.8%`
- Raw 3bet count: `635`
- Raw 3bet average: `9.01x`
- Near-all-in / 20bb+ 3bets excluded from sizing discipline: `90`
- Clean 3bet count: `545`
- Clean all-context 3bet average: `7.37x`
- Clean 3bet versus single 2x open count: `307`
- Clean 3bet versus single 2x open average: `6.35x`
- Clean 3bet versus single 2x open mode: `6.0x`
- Clean squeeze versus 2x callers average: `7.53x`

Screenshots:

- Desktop: `tmp/qa/matrix-render-desktop.png`
- Mobile full-page: `tmp/qa/matrix-render-mobile-full.png`

## RECOMMENDED NEXT STEP

Add a small "calculation detail" popover beside the sizing cards so Hero can see mode, median, raw average, excluded all-in-like rows, and clean sample count without guessing whether the backend is lying.
