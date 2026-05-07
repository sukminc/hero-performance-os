# Task 110: Matrix Sizing Table Stability Fix

## TASK

Fix the recurring Matrix sizing table breakage where the table appeared as unstyled inline text in the browser.

## WHAT I CHANGED

- Reworked `PreflopSizingTable` so the critical column layout is carried by React inline grid styles.
- Kept CSS classes for visual polish, but no longer rely on class-only CSS for the row/column structure.
- Restarted the stale Next dev server on port `3000`.
- Re-ran build and screenshot QA.

## ARCHITECTURE IMPACT

No backend truth changes. This is a frontend rendering hardening pass for the first-value Matrix page.

The key product-surface change is that sizing rows should preserve their column layout even if CSS hot reload/cache behavior is briefly inconsistent.

## DECISIONS MADE

- Native table markup was still too vulnerable to class CSS not applying in the user's live browser state.
- For the Matrix sizing summary, critical layout should be inline-stabilized because this is a first-screen trust surface.
- Stale dev server/HMR state should be treated as part of local frontend QA, not dismissed as user-side weirdness.

## RISKS / OPEN QUESTIONS

- This is more explicit styling inside the component than ideal, but it is appropriate for a critical metric table that keeps losing its layout during local iteration.
- A later design-system pass can extract these inline layout constants into a stable shared component style pattern.

## OUT OF SCOPE

- No broader redesign of Matrix layout.
- No automated visual diffing.
- No parser or metric changes.

## TEST / VALIDATION

- `python3 tests/matrix_position_situation_tests.py`
- `python3 tests/matrix_quiz_tests.py`
- `npm run build` in `frontend`
- Restarted `npm run dev` on port `3000`
- `npm run qa:matrix:render` in `frontend`
- In-app browser reload showed zero console errors.

Screenshots:

- Desktop: `tmp/qa/matrix-render-desktop.png`
- Mobile full-page: `tmp/qa/matrix-render-mobile-full.png`

Visual finding:

- The sizing rows now render as stable horizontal rows with separated columns on desktop.
- The mobile full-page screenshot keeps the sizing rows grouped and readable instead of collapsing into inline text.

## RECOMMENDED NEXT STEP

Add a QA assertion that fails if the sizing section width collapses below the expected row width or if the `Position` header shares one unstyled text line with all metric labels.
