# Task 100: Matrix Position Situation Detail

## TASK

Simplify Hero Baseline Matrix pinned detail so Hero can see which position/situation combinations drive a hand's result before reading low-level action labels.

## WHAT I CHANGED

- Added `prior_call_count` and `facing_state` to Matrix hand observations.
- Added `hero_preflop_size_bb` so Matrix detail can show Hero's average preflop open / call / 3bet / jam sizing.
- Added deterministic preflop facing-state extraction:
  - `unopened`,
  - `vs_limp`,
  - `vs_multi_limp`,
  - `vs_open`,
  - `vs_3bet_plus`,
  - `vs_all_in`.
- Added `position_situation_breakdown` to Matrix cells and selected-hand detail.
- Reworked `/operator/matrix` pinned detail to lead with a position-first "Where hand wins / loses" table.
- Added an `Avg size` column so hands like `QJs` can be read as position + preflop decision + average size + actual result.
- Replaced raw internal action labels in the primary detail view with readable situation labels such as:
  - `Unopened open`,
  - `Call vs open`,
  - `Iso vs limper(s)`,
  - `3bet / re-raise`,
  - `Jam / all-in`,
  - `Fold exposure`.
- Kept existing `hover_action_breakdown` for backward compatibility and retained compact 3bet facts as secondary context.
- Updated Matrix docs and decisions to preserve the position/situation-first product rule.

## ARCHITECTURE IMPACT

This keeps Matrix as deterministic derived truth while making the primary operator view match the product question: "with this hand, from which position and situation am I actually winning or losing?"

No new canonical table or consumer-facing route was added. The change extends the existing Matrix payload and preserves old action breakdown fields for compatibility.

## DECISIONS MADE

- Position/situation is now the primary hand-detail lens.
- Action taxonomy remains available, but no longer leads the pinned detail.
- Prior caller count is exposed as limper context for iso spots and caller context for call-vs-open spots.
- Call-vs-open rows show the faced open size as the primary size because it better answers what Hero responded to.
- Fold exposure remains not performance-scored.
- Tiny samples remain visible with a `small sample` badge rather than being hidden or overinterpreted.

## RISKS / OPEN QUESTIONS

- `prior_call_count` means limpers before Hero in unopened/limped pots, but callers before Hero in raised pots; the UI labels this based on situation.
- Open-size extraction is still heuristic and inherited from the current Matrix parser.
- The table currently shows top 8 position/situation rows; later versions may add expand/collapse for full detail.

## OUT OF SCOPE

- No solver/GTO comparison.
- No new membership or upload gating.
- No consumer-facing page.
- No postflop node breakdown.
- No exact ICM/PKO truth.

## TEST / VALIDATION

- `python3 -m py_compile app/api/hand_matrix.py`
- `python3 tests/matrix_position_situation_tests.py`
- `python3 tests/service_boundary_tests.py`
- `python3 tests/matrix_quiz_tests.py`
- `python3 tests/v2_smoke_tests.py`
- `npm run build`
- Local QJs payload smoke check shows position/situation rows such as `BB · Call vs open`, `UTG · Open`, and `UTG+1 · Open`, with average action/open sizes.

## RECOMMENDED NEXT STEP

Use the simplified pinned detail to review QJs first, then add a lightweight operator note/status overlay for each position/situation row once the labels feel right.
