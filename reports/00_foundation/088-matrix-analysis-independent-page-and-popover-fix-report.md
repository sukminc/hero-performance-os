# 088 Matrix Analysis Independent Page And Popover Fix Report

## TASK

Make Hero Baseline Matrix Analysis easier to read as a product surface and fix matrix hover popovers being clipped.

## WHAT I CHANGED

- Added a dedicated operator page at `/operator/matrix`.
- Added a dashboard link from the existing Hero Baseline section to the dedicated Matrix Analysis page.
- Updated matrix card CSS so hover popovers can escape the parent card instead of being clipped.
- Added keyboard focus support for matrix cells on the dedicated page.
- Added `hidden_value_cards` to the hand matrix payload so the page can show positive execution / keep-study candidates next to mandatory correction candidates.
- Updated `docs/hero_baseline_13x13_matrix.md`.
- Updated `DECISIONS_LOG.md`.

## ARCHITECTURE IMPACT

- Keeps the same deterministic hand matrix payload as the source of truth.
- Does not introduce LLM interpretation as truth.
- Promotes Matrix Analysis from a buried operator section into an explicit operator-facing product surface.
- Adds positive execution surfacing without changing raw / normalized / derived truth boundaries.

## DECISIONS MADE

- `/operator/matrix` is the focused Matrix Analysis page for MVP/operator mode.
- The operator dashboard keeps a compact Matrix section but links to the dedicated reading surface.
- Hover popovers remain lightweight quick peeks; deeper interpretation belongs in cards and selected-hand breakdown sections.
- Hidden value candidates exclude obvious premium hands so the surface highlights less obvious working patterns.

## RISKS / OPEN QUESTIONS

- `hidden_value_cards` are result-based positive execution candidates, not solver-approved lines.
- The page still reads from the legacy `app/api/hand_matrix.py` bridge; a later cleanup should move the surface builder into `core/surfaces`.
- Popovers are improved by overflow/z-index changes, but very small screens may still prefer click-to-open panels later.

## OUT OF SCOPE

- No GTO chart integration.
- No all-in adjusted EV / ICM / PKO EV.
- No consumer-facing polish pass beyond making the operator surface readable.
- No persistence change or schema migration.

## TEST / VALIDATION

- Passed `python3 -m py_compile app/api/hand_matrix.py`.
- Passed payload smoke check for `hidden_value_cards`; payload returned 8 hidden value candidates and the selected `66` action breakdown.
- Passed `npm run build` in `frontend`; Next generated `/operator/matrix` as a dynamic route.

## RECOMMENDED NEXT STEP

1. Build a dedicated `/operator/aof` page using the same product pattern.
2. Add click-to-pin matrix cell detail so Hero can compare two hand classes without fighting hover behavior.
