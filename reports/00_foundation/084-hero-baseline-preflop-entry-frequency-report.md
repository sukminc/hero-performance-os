# Task 84: Hero Baseline Preflop Entry Frequency

## TASK

Add preflop entry frequency decomposition to Hero Baseline so a hand like `66` can be inspected by open/limp, call-vs-open, 3bet, 4bet+, and related entry types.

## WHAT I CHANGED

- Extended hand observations with `preflop_entry_type` and `prior_raise_count`.
- Added entry-type classification for:
  - `open_limp_or_complete`
  - `limp_behind`
  - `call_vs_open`
  - `call_vs_3bet`
  - `call_vs_4bet_plus`
  - `open_raise`
  - `open_raise_jam`
  - `iso_raise`
  - `three_bet`
  - `three_bet_jam`
  - `four_bet`
  - `four_bet_jam`
  - `five_bet_plus`
- Added action-depth summary counts to matrix cells and selected-hand summary.
- Added selected-hand `action_depth_breakdown` with count, raw BB, stack realization, position mix, format mix, and examples.
- Updated `/operator` Hero Baseline to show `66 Preflop Entry Frequency` and `66 Action Counts`.

## ARCHITECTURE IMPACT

This stays in the derived Hero Baseline layer and does not change canonical storage.

It makes hand-class interpretation more product-useful by separating “Hero played this hand” from “Hero opened, limped, called an open, 3bet, or 4bet+ with this hand.”

## DECISIONS MADE

- The first Hero preflop action is the v1 anchor for entry classification.
- Prior non-Hero raise count determines whether Hero's raise is open, iso, 3bet, 4bet, or 5bet+.
- Prior non-Hero raise count also determines whether Hero's call is call-vs-open, call-vs-3bet, or call-vs-4bet+.
- Limp/complete without prior raise is counted separately because Hero explicitly wants opened/limp frequency visible.

## RISKS / OPEN QUESTIONS

- Blind complete/check/free-play cases still need finer classification later.
- GG text action parsing remains heuristic and should eventually move from the legacy hand-matrix API into normalized core parsing.
- This does not yet judge whether a 3bet/4bet is strategically wrong; it only counts and summarizes outcomes.

## OUT OF SCOPE

- No solver comparison.
- No EV model.
- No operator approval overlay.
- No database schema change.

## TEST / VALIDATION

Validation should confirm:

- `66` exposes action-depth counts.
- Matrix still compiles and builds.
- Frontend still renders typecheck/build.

## RECOMMENDED NEXT STEP

Use the new action-depth breakdown to build a `66 Overplay Review Card` that flags whether the actual damage comes from opens, calls versus action, 3bets, or 4bet+ spots.
