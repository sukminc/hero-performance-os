# Task 006 - Matrix Result Seed V0 Report

## TASK

Implement deterministic GG summary outcome extraction on top of the Matrix count
seed.

## WHAT I CHANGED

- Added `core/ingest/matrix_result_seed.py`.
- Added `scripts/build_matrix_result_seed.py`.
- Added `tests/matrix_result_seed_tests.py`.
- Added `tasks/00_restart/006-matrix-result-seed-v0.md`.
- Added this report.
- Generated `data/manifests/matrix_result_seed.json`.

## ARCHITECTURE IMPACT

This adds a result-observation layer without changing raw truth:

- source files remain preserved,
- Matrix count seed remains count-only,
- result seed rehydrates raw blocks from provenance,
- outcome counts are rebuildable,
- gross collected chips are kept separate from net result.

This moves the dataset closer to future actual-result Matrix analytics while
staying inside deterministic data processing.

## DECISIONS MADE

- Outcome source is the Hero `Seat ... Hero ...` line inside `*** SUMMARY ***`.
- Supported V0 outcome buckets are `won`, `collected`, `lost`, `folded`, and
  `unknown`.
- Amounts are stored only as `gross_collected_chips` when Hero won or collected.
- `gross_collected_chips` is not net profit, not BB result, not EV, and not
  all-in adjusted EV.
- Unsupported summary shapes become `unknown` rather than guessed.

## RISKS / OPEN QUESTIONS

- Net chip result still requires deterministic contribution accounting or stack
  delta extraction.
- Folded hands do not yet include loss amount.
- Split pots and side pots are only represented through Hero's summary outcome
  and gross collected amount, not full pot accounting.
- Played-pot filtering remains future work.

## OUT OF SCOPE

- No net chip or BB result.
- No EV.
- No all-in adjusted EV.
- No played-pot filter.
- No interpretation.
- No frontend surface.

## TEST / VALIDATION

Passed:

- `python3 tests/matrix_result_seed_tests.py`
- `PYTHONPYCACHEPREFIX=/private/tmp/opb_pycache python3 -m py_compile core/ingest/matrix_result_seed.py scripts/build_matrix_result_seed.py tests/matrix_result_seed_tests.py`
- `python3 scripts/build_matrix_result_seed.py --summary`

The generated Matrix result seed should exist at:

- `data/manifests/matrix_result_seed.json`

Current Matrix result seed totals:

- `result_hand_count`: 9,330
- `distinct_hand_class_count`: 169
- `outcome_counts`: 595 collected, 7,102 folded, 558 lost, 1,075 won
- `unknown_result_count`: 0
- `gross_collected_chips_sum`: 103,893,317
- `total_pot_chips_sum`: 435,456,352

Sample hand-class result observations:

- `AA`: 61 observed, 38 won, 14 collected, 8 lost, 1 folded
- `AKs`: 25 observed, 13 won, 5 collected, 6 lost, 1 folded
- `72o`: 83 observed, 82 folded, 1 lost

## RECOMMENDED NEXT STEP

Implement Matrix Played-Pot Seed V0:

- detect whether Hero voluntarily entered or escalated preflop,
- separate dealt exposure from played-pot samples,
- keep result observations factual,
- avoid leak interpretation until played-pot classification is validated.
