# Task 102: Matrix Preflop Sizing Summary

## TASK

Define `/operator/matrix` as the preflop baseline surface and make it easier to read as a product page: preflop sizing summary first, full-width 13x13 Matrix second, and only a short correction queue.

## WHAT I CHANGED

- Added `preflop_sizing_summary` to the Matrix payload.
- The summary now exposes:
  - total parsed hand histories,
  - played preflop hands,
  - Hero first-action open average,
  - standard-open count,
  - 2x open discipline rate,
  - non-jam 3bet count,
  - average non-jam 3bet size,
  - average 3bet size versus a single 2x open,
  - average squeeze size versus 2x open plus callers,
  - the same sizing facts by position.
- Reworked `/operator/matrix` hero copy around `Hero Preflop Baseline`.
- Replaced the old overview cards with a preflop sizing summary and by-position sizing table.
- Changed correction candidates to a compact top-five strip.
- Removed hidden-value cards and duplicate selected-hand action breakdown from the primary page flow.
- Made the Matrix shell wider so the 13x13 grid reads closer to fullscreen on desktop.
- Updated Matrix docs and decision log to define the page as the preflop baseline surface.

## ARCHITECTURE IMPACT

This is still deterministic Matrix-derived truth. No new canonical table was added.

The sizing summary uses existing `HandObservation` fields:

- `hero_preflop_size_bb` for first-action open sizing,
- `hero_3bet_size_bb` for non-jam 3bet sizing,
- `open_size_bb` and `prior_call_count` to separate single-open 2x 3bets from squeeze-like 2x-plus-caller spots.

## DECISIONS MADE

- Open-size summary uses non-jam `open_raise` rows.
- Standard open average filters out open sizes above 3.5bb so jam/odd parsed lines do not distort the discipline read.
- 3bet summary excludes jam rows because Hero asked about ordinary sizing such as 6x, 7x, and 8x.
- Correction queue is now top five only on the Matrix page.
- Hidden value remains available in payload but no longer crowds this preflop baseline page.

## RISKS / OPEN QUESTIONS

- 3bet averages show actual Hero behavior and currently run larger than the intended 6x baseline in some positions.
- Open and 3bet sizing are only as good as the current GG parser's preflop amount extraction.
- Position-specific 3bet rows can still mix stack depths and formats; later filters may split this by stack band.

## OUT OF SCOPE

- No solver/GTO sizing comparison.
- No membership/upload gating.
- No consumer-facing page.
- No exact EV or all-in adjusted EV.
- No automatic coaching-memory mutation from sizing deviations.

## TEST / VALIDATION

- `python3 -m py_compile app/api/hand_matrix.py`
- Local payload smoke check:
  - `27280` total hands,
  - `3032` standard opens,
  - `2.13x` average standard open,
  - `82.8%` near-2x open rate,
  - `635` non-jam 3bets,
  - `9.01x` average 3bet,
  - `7.7x` average 3bet versus single 2x open,
  - `8.84x` average squeeze versus 2x plus callers.

## RECOMMENDED NEXT STEP

Add stack-band filters to the sizing summary so Hero can compare the intended 2x / 6x / 7-8x rules at `lt15`, `15to25`, and `gt25` separately.
