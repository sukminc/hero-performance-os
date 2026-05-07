# Task 106: Matrix Runout Noise Guardrail

## TASK

Add a Matrix dashboard section that protects Hero from over-correcting standard premium/baseline hands after painful actual-result losses.

## WHAT I CHANGED

- Added `runout_noise_cards` to the Matrix payload.
- Detects protected premium pressure hands such as `AA`, `KK`, `QQ`, `AKs`, and `AKo` when they show repeated painful losses or negative actual results.
- Detects standard BB defend guardrails for core defend families such as `QJs`, `KQs`, `KQo`, and related suited broadways when BB call-vs-open results are negative enough to review but not enough to auto-cut.
- Added a `/app/matrix` and `/operator/matrix` section titled `Do not over-correct / Correct hand, painful runout`.
- Updated Matrix docs and decision log.
- Added regression coverage proving repeated `KK` premium losses are protected as runout-noise guardrails while loose `A9o` pressure is not.

## ARCHITECTURE IMPACT

This is a derived Matrix interpretation layer only. It does not mutate hand history truth, player memory, Today, Brain, or operator review overlays.

The card is intentionally framed as actual-result proxy interpretation, not solver EV or all-in adjusted EV.

## DECISIONS MADE

- Premium/standard baseline spots can appear in a guardrail section even when they have repeated full-stack losses, because the product must help Hero avoid fear-based range shrinkage.
- Loose non-premium pressure hands are not protected by this guardrail and remain eligible for correction review.
- The section appears before correction candidates so confidence protection is visible before leak review.

## RISKS / OPEN QUESTIONS

- True EV-based cooler detection still requires either all-in adjusted EV from source data or an equity calculator for all-in showdowns.
- Some `open_raise` rows include later all-in outcomes, so the current card is best read as "painful result in this preflop entry family" rather than exact action-street EV.
- Recency-weighted cooler cards are not implemented yet, so "last week KK got crushed five times" only appears if those hands are uploaded and present in the current corpus.

## OUT OF SCOPE

- No solver lookup.
- No all-in equity calculator.
- No automatic memory promotion.
- No operator tagging workflow for `cooler`, `standard`, or `misplayed` yet.

## TEST / VALIDATION

- `python3 -m py_compile app/api/hand_matrix.py`
- `python3 tests/matrix_position_situation_tests.py`
- `python3 tests/matrix_quiz_tests.py`
- `npm run build` in `frontend`

## RECOMMENDED NEXT STEP

Add recency windows to the guardrail section so a user can see "last 7 days / last 30 days" painful premium-hand runouts separately from the all-history baseline.
