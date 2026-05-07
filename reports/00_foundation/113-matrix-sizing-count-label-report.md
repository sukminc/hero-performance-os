# Matrix Sizing Count Label Report

## TASK
Make the preflop sizing table less confusing by separating size multipliers from observation counts.

## WHAT I CHANGED
- Changed sizing-table counts from `754x`, `24x`, and `8x` style labels to semantic count labels:
  - `754 opens`
  - `24 3bets`
  - `20 spots`
  - `8 squeezes`
- Kept sizing values as `x`, because `2.1x`, `6.36x`, and `7.17x` are size multipliers.
- Extended Matrix render QA so sizing count labels fail if they regress back to count-as-`x` labels like `754x`.

## ARCHITECTURE IMPACT
- No backend or Matrix payload changes.
- Presentation-only product-language cleanup.
- Keeps the same data while making the table easier to interpret.

## DECISIONS MADE
- Use `x` only for bet-size multipliers.
- Use nouns for counts because they explain what was counted.
- Use `spots` for context-specific rows such as `Vs single 2x`.

## RISKS / OPEN QUESTIONS
- `spots` is intentionally general. Later, this can become more specific if the row taxonomy becomes more consumer-facing.

## OUT OF SCOPE
- No calculation changes.
- No table layout redesign.
- No mobile pinned-detail cleanup.

## TEST / VALIDATION
- `npm run build` in `frontend` passed.
- `python3 tests/matrix_position_situation_tests.py` passed.
- `python3 tests/matrix_quiz_tests.py` passed.
- `npm run qa:matrix:render` passed.
- QA screenshots:
  - `/Users/chrisyoon/GitHub/opb-poker/tmp/qa/matrix-render-desktop.png`
  - `/Users/chrisyoon/GitHub/opb-poker/tmp/qa/matrix-render-desktop-full.png`
  - `/Users/chrisyoon/GitHub/opb-poker/tmp/qa/matrix-render-mobile-full.png`

## RECOMMENDED NEXT STEP
Apply the same language rule elsewhere: `x` means sizing multiplier, count labels use human nouns like `hands`, `opens`, `spots`, or `jams`.
