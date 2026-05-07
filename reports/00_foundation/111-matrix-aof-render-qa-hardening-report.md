# Matrix AOF Render QA Hardening Report

## TASK
Fix `/operator/matrix` sections that collapsed from card/table layouts into inline text, especially the AOF Baseline detail rows, and harden Matrix render QA so these failures are caught before operator review.

## WHAT I CHANGED
- Replaced duplicated AOF rendering on `/operator/matrix` and `/app/matrix` with a shared `AofBaselineSection`.
- Replaced CSS-hover-only AOF detail cards with `AofDetailDisclosure`, a deterministic closed-by-default details control.
- Added explicit closed/open CSS rules so AOF detail panels cannot render inline before interaction.
- Kept AOF rows table-like with inline grid styles for action and position rows.
- Added a desktop full-page screenshot to `npm run qa:matrix:render`.
- Hardened `npm run qa:matrix:render` with Chromium layout assertions for:
  - sizing table rows,
  - AOF grid and AOF rows,
  - hidden AOF detail panels,
  - correction candidate grid,
  - runout trend tabs,
  - 13x13 matrix grid,
  - pinned detail grid,
  - mobile card overflow.
- Updated `WORKFLOW.md` so Matrix frontend QA requires structural layout assertions, not only screenshots.

## ARCHITECTURE IMPACT
- No canonical poker truth changed.
- No matrix parsing, grading, AOF calculation, or backend payload contract changed.
- AOF display is now a shared frontend component across operator and authenticated Matrix surfaces, reducing drift between the two first-value pages.
- Matrix QA now has a deterministic browser assertion layer for the product surface.

## DECISIONS MADE
- Detail information should not depend on hover-only hidden content because CSS failures can expose all detail text as body text.
- AOF detail should start collapsed and only reveal on explicit user interaction.
- QA must fail when section structure collapses, even if TypeScript and build pass.
- Desktop QA needs a full-page screenshot because this page's failures often happen below the first viewport.

## RISKS / OPEN QUESTIONS
- The mobile pinned-detail result-driver table is still dense. It no longer overflows the page boundary, but future polish should make it more readable on narrow screens.
- The QA script asserts the current operator Matrix structure. If class names change intentionally, the QA script should be updated in the same diff.

## OUT OF SCOPE
- No backend AOF metric recalculation.
- No new data model.
- No consumer signup or membership work.
- No redesign of the 13x13 matrix cells or pinned detail content hierarchy beyond preserving layout.

## TEST / VALIDATION
- `npm run build` in `frontend` passed.
- `python3 tests/matrix_position_situation_tests.py` passed.
- `python3 tests/matrix_quiz_tests.py` passed.
- `npm run qa:matrix:render` passed with structural layout assertions.
- QA screenshots:
  - `/Users/chrisyoon/GitHub/opb-poker/tmp/qa/matrix-render-desktop.png`
  - `/Users/chrisyoon/GitHub/opb-poker/tmp/qa/matrix-render-desktop-full.png`
  - `/Users/chrisyoon/GitHub/opb-poker/tmp/qa/matrix-render-mobile-full.png`

## RECOMMENDED NEXT STEP
Use the hardened Matrix render QA as the required acceptance gate for every `/operator/matrix` and `/app/matrix` frontend slice, then make the mobile pinned-detail table easier to scan.
