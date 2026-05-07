# Task 108: Matrix Render QA And Sizing Table Fix

## TASK

Fix the broken Matrix sizing summary rendering and add a repeatable build-plus-screenshot QA process for Matrix frontend work.

## WHAT I CHANGED

- Replaced the fragile `div` grid sizing summary with a native table component:
  - `frontend/app/operator/matrix/preflop-sizing-table.tsx`
- Reused that component from:
  - `/operator/matrix`
  - `/app/matrix`
- Updated sizing table CSS so the desktop view renders stable rows and the mobile view preserves table structure.
- Added `npm run qa:matrix:render` in `frontend/package.json`.
- Added `frontend/scripts/qa-matrix-render.mjs` to capture:
  - desktop screenshot,
  - mobile full-page screenshot.
- Added a Frontend Render QA Rule to `WORKFLOW.md`.
- Fixed a React list-key warning in `MatrixPinBoard`.

## ARCHITECTURE IMPACT

No backend truth changes. This is frontend render stability plus workflow hardening.

The sizing table now uses native table semantics, which is more resilient for a first-value user-facing page.

## DECISIONS MADE

- Matrix frontend changes must not be accepted on build success alone.
- Browser screenshot QA is now required for meaningful Matrix UI changes.
- The default render QA target is `/operator/matrix` through the dev-login route because it exercises the full operator-depth Matrix payload.

## RISKS / OPEN QUESTIONS

- `npm run qa:matrix:render` requires a running local dev server at `localhost:3000`.
- In this sandbox, Chromium screenshot execution required elevated browser permissions. In a normal local shell it should run directly.
- The screenshot script uses an existing cached Playwright CLI when no local project Playwright dependency exists.

## OUT OF SCOPE

- No full visual regression diffing.
- No CI integration.
- No pixel-based pass/fail threshold yet.

## TEST / VALIDATION

- `python3 tests/matrix_position_situation_tests.py`
- `python3 tests/matrix_quiz_tests.py`
- `npm run build` in `frontend`
- `npm run qa:matrix:render` in `frontend`
- In-app browser reload showed zero console errors.

Screenshots:

- Desktop: `tmp/qa/matrix-render-desktop.png`
- Mobile full-page: `tmp/qa/matrix-render-mobile-full.png`

Visual finding:

- The sizing summary now renders as separated rows and columns instead of collapsed inline text.
- The mobile full-page screenshot preserves the table structure and does not merge the sizing labels/numbers into one line.

## RECOMMENDED NEXT STEP

Add a lightweight visual assertion script that checks for expected Matrix section text and table row count after screenshots are captured.
