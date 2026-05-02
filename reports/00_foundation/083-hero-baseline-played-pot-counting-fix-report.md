# Task 83: Hero Baseline Played-Pot Counting Fix

## TASK

Fix the Hero Baseline hand-matrix counting policy so hand counts and performance metrics represent pots Hero actually played, not every time Hero was dealt the hand.

## WHAT I CHANGED

- Added played-pot filtering to `app/api/hand_matrix.py`.
- Preserved `dealt_count` as exposure context.
- Added `played_count` as the default sample count for performance metrics.
- Updated matrix cells, suspicious queues, stack realization queues, selected-hand summaries, and position breakdowns to use played pots.
- Added `counting_policy` to the payload.
- Updated `/operator` labels so the UI says `played` and also shows dealt count on matrix cells.
- Updated Hero Baseline docs to make the counting policy explicit.

## ARCHITECTURE IMPACT

This corrects the derived Hero Baseline interpretation layer without changing canonical raw hand storage.

The previous matrix could make hands like `72o` appear to have more meaningful performance samples than `AA` because it counted folds/dealt hands. The corrected matrix now treats performance as the result of voluntarily played pots.

## DECISIONS MADE

- `played_count` is now the default count for performance.
- `dealt_count` remains available as context.
- Fold-only observations are excluded from hand-class performance metrics.
- Non-fold Hero actions include `call`, `raise`, `jam`, and `other`.

## RISKS / OPEN QUESTIONS

- Some checked big-blind hands may still need finer classification later.
- The first-action parser is still heuristic and should eventually be normalized in core parsing.
- This does not yet split limp/check/free-play BB spots as a distinct participation category.

## OUT OF SCOPE

- No DB schema change.
- No solver EV.
- No all-in adjusted EV.
- No new review overlay.

## TEST / VALIDATION

Validation should confirm:

- `72o` played count is far lower than dealt count.
- `AA` played count remains close to dealt count.
- `66` metrics still calculate from played pots.
- Frontend typecheck and build pass.

## RECOMMENDED NEXT STEP

Continue with decision-node decomposition for `66`, `77`, `88`, `QQ`, and `AQs`, now using played-pot samples only.
