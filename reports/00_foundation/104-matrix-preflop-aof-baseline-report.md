# Task 104: Matrix Preflop AOF Baseline

## TASK

Show Hero's preflop AOF stack-depth baseline on `/operator/matrix`, with the numeric summary and interpretation separated into clear sections.

## WHAT I CHANGED

- Added `preflop_aof_summary` to the Matrix payload.
- Defined AOF for this surface as: Hero's first preflop action is jam/all-in.
- Added overall AOF count, average stack BB, median stack BB, min, and max.
- Added a separate `<=25bb` AOF baseline.
- Added AOF breakdown by preflop jam action type:
  - `open_raise_jam`,
  - `three_bet_jam`,
  - `iso_raise_jam`,
  - `four_bet_jam`.
- Added AOF breakdown by position.
- Added deterministic interpretation copy and takeaways.
- Added a dedicated `/operator/matrix` AOF Baseline section below the sizing summary.
- Updated docs and regression tests.

## ARCHITECTURE IMPACT

This remains deterministic Matrix-derived truth. No solver chart, live advice, or canonical memory mutation was added.

The AOF summary reports Hero's actual historical preflop all-in stack depth and is explicitly post-hoc baseline evidence.

## DECISIONS MADE

- AOF is counted only when Hero's first preflop action is `jam`.
- The section shows both average and median because average is pulled upward by deeper rejam spots.
- The `<=25bb` subset is shown separately because that is closer to the practical short-stack AOF baseline.
- Interpretation is part of the payload so the UI can display consistent product language.

## RISKS / OPEN QUESTIONS

- Some deeper jams may be standard reshove spots rather than true short-stack AOF behavior.
- Future work should split the summary by stack band, format, and position pressure.
- This does not compare to solver shove charts.

## OUT OF SCOPE

- No GTO/AOF chart comparison.
- No hand-by-hand jam correctness scoring.
- No Today/Brain/memory mutation.
- No upload/membership gating.

## TEST / VALIDATION

- Regression test added for AOF average/median and `<=25bb` summary.
- Local Hero Matrix payload measured:
  - `720` total preflop jams,
  - `14.95bb` average,
  - `12.21bb` median,
  - `652` jams at `<=25bb`,
  - `11.59bb` `<=25bb` average,
  - `11.58bb` `<=25bb` median.

## RECOMMENDED NEXT STEP

Add an AOF stack-band drilldown so Hero can compare open jam, iso jam, 3bet jam, and 4bet jam behavior separately at `lt15`, `15to25`, and `gt25`.

## UI REVISION

After adding the Matrix sections, pinned detail summary cards overflowed when the viewport was narrowed. I updated the pinned summary grid to use responsive `auto-fit` columns, removed negative letter spacing from result metrics, enabled wrapping inside metric cards, and gave pinned cards container sizing so the metric font scales down with the card width.

## AOF RESULT REVISION

The AOF section now includes actual result metrics:

- `avg_bb_per_jam`,
- `avg_stack_realization_pct`,
- `full_stack_loss_count`,
- repeated big-minus clusters grouped by `hand_class + position + entry_type`.

The page shows result values in the AOF rows and exposes repeated big-minus details on hover, including the clustered hand/action/position and one recent example.
