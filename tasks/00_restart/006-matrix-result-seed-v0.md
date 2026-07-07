# Task 006 - Matrix Result Seed V0

## Business Question

Can OPB attach deterministic GG summary outcomes to the 13x13 Matrix seed
without pretending to know EV or net profit?

## Objective

Add a Matrix result seed that reads the count-only Matrix seed, rehydrates each
unique hand block from raw source provenance, extracts Hero's GG summary outcome,
and aggregates outcome counts by hand class.

## Scope

- Read `data/manifests/matrix_count_seed.json`.
- Process only hands already classified in the count seed.
- Rehydrate raw hand blocks from source file path and line range.
- Extract Hero summary line from the `*** SUMMARY ***` section.
- Classify Hero outcome as:
  - `won`
  - `collected`
  - `lost`
  - `folded`
  - `unknown`
- Extract gross collected chips only when Hero's summary line contains a won or
  collected amount.
- Aggregate outcome counts by hand class.
- Write `data/manifests/matrix_result_seed.json`.

## Out Of Scope

- No net chip profit.
- No BB result.
- No EV or all-in adjusted EV.
- No played-pot filtering.
- No action classification.
- No leak/strength interpretation.
- No frontend work.

## Validation Target

- `python3 tests/matrix_result_seed_tests.py`
- `PYTHONPYCACHEPREFIX=/private/tmp/opb_pycache python3 -m py_compile core/ingest/matrix_result_seed.py scripts/build_matrix_result_seed.py tests/matrix_result_seed_tests.py`
- `python3 scripts/build_matrix_result_seed.py --summary`
- Matrix result seed output exists at `data/manifests/matrix_result_seed.json`.

## Report Destination

`reports/00_restart/006-matrix-result-seed-v0-report.md`
