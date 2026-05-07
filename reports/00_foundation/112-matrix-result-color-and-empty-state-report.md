# Matrix Result Color And Empty State Report

## TASK
Clean up `/operator/matrix` visual language so missing sizing data is blank instead of noisy, and positive/negative result values are readable and color-consistent.

## WHAT I CHANGED
- Removed visual `n/a 0x` noise from the preflop sizing table.
- Left missing sizing spots blank while preserving the table columns.
- Added shared positive / negative / neutral metric color classes:
  - positive result: teal,
  - negative result: orange-red,
  - neutral result: pale slate.
- Applied result coloring to:
  - AOF summary result values,
  - AOF By Action rows,
  - AOF By Position rows,
  - repeated big minus clusters,
  - runout-noise guardrail cards,
  - correction candidate cards,
  - pinned detail Raw BB / Stack cards,
  - pinned detail position/result rows.
- Split dense `3x · -16.37bb · -99.07% stack` strings into separated metric chips.
- Extended Matrix render QA so it fails when:
  - `n/a 0x` appears,
  - positive/negative metric classes are missing,
  - AOF big-loss metrics are not split into readable chips.

## ARCHITECTURE IMPACT
- No poker parsing, scoring, AOF calculation, or Matrix payload contract changed.
- This is presentation-layer cleanup only.
- The product surface now has a more consistent visual language for actual-result evidence.

## DECISIONS MADE
- Missing sizing observations should be blank, not `n/a 0x`, because they do not carry useful decision information.
- Actual-result metrics should use color consistently across the page, not only in one section.
- Dense metric strings should be split into chips when they mix count, BB result, and stack realization.

## RISKS / OPEN QUESTIONS
- The 13x13 cells still rely mainly on background tone and border tone rather than signed font colors. This keeps the matrix from becoming too visually noisy, but it can be revisited.
- Mobile pinned detail remains dense, though it no longer overflows the page boundary.

## OUT OF SCOPE
- No backend recalculation.
- No redesign of card hierarchy.
- No change to correction candidate selection.
- No consumer membership or upload-limit work.

## TEST / VALIDATION
- `npm run build` in `frontend` passed.
- `python3 tests/matrix_position_situation_tests.py` passed.
- `python3 tests/matrix_quiz_tests.py` passed.
- `npm run qa:matrix:render` passed with structural and visual-language assertions.
- QA screenshots:
  - `/Users/chrisyoon/GitHub/opb-poker/tmp/qa/matrix-render-desktop.png`
  - `/Users/chrisyoon/GitHub/opb-poker/tmp/qa/matrix-render-desktop-full.png`
  - `/Users/chrisyoon/GitHub/opb-poker/tmp/qa/matrix-render-mobile-full.png`

## RECOMMENDED NEXT STEP
Keep this color system as the Matrix visual grammar and next simplify the mobile pinned-detail rows so they scan less like a compressed audit table.
