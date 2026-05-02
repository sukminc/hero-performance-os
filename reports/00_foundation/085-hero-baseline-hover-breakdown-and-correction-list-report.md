# Task 85: Hero Baseline Hover Breakdown + Correction List

## TASK

Make every 13x13 matrix cell reveal action-depth breakdown on hover and add a mandatory correction list based on hand/action patterns.

## WHAT I CHANGED

- Added per-cell `hover_action_lines` to the hand matrix payload.
- Added `mandatory_correction_cards` across all hand/action combinations.
- Ranked correction cards by stack-normalized severity and repeat count.
- Added hover popovers to 13x13 cells in `/operator`.
- Added a Mandatory Corrections section below the matrix.
- Added CSS for matrix hover popovers.

## ARCHITECTURE IMPACT

This keeps the matrix as a derived inspection surface and adds product interpretation over deterministic hand/action aggregates.

The product can now show both high-level hand-class performance and the actual action route that produced the result.

## DECISIONS MADE

- Hover panels show the top action-depth lines for each hand.
- Correction candidates require repeat count >= 2 and meaningful negative raw or stack-normalized performance.
- Correction cards do not become approved truth; they are review candidates.

## RISKS / OPEN QUESTIONS

- Hover is useful on desktop but needs a tap/click alternative for mobile later.
- The correction threshold is v1 heuristic and should be operator-tuned.
- Some entry categories still need refinement for blind completes and free checks.

## OUT OF SCOPE

- No DB schema change.
- No solver comparison.
- No all-in adjusted EV.
- No approved truth overlay yet.

## TEST / VALIDATION

Validation should confirm:

- Python compile succeeds.
- Payload includes hover lines and correction cards.
- Frontend typecheck/build pass.

## RECOMMENDED NEXT STEP

Add click-to-select matrix cells so selecting `66`, `77`, or any hand reloads the spotlight/action-depth cards for that hand instead of hardcoding `66`.
