# Task 005 - Matrix Count Seed V0

## Business Question

Can OPB create the first 13x13-ready count dataset from processed hand-history
text without interpretation?

## Objective

Add a deterministic matrix count seed that reads the hand extraction ledger and
processable dataset index, extracts Hero hole cards from unique raw hand blocks,
maps them into 13x13 hand classes, and writes count-only matrix data.

## Scope

- Read `data/manifests/hand_extraction_ledger.json`.
- Read `data/manifests/processable_dataset_index.json`.
- Process only `hand_history_text` assets.
- Count each unique raw hand fingerprint once.
- Extract Hero hole cards from `Dealt to Hero [...]`.
- Map hole cards into canonical hand classes such as `AA`, `AQs`, `KTo`.
- Build all 169 matrix cells, including zero-count cells.
- Write `data/manifests/matrix_count_seed.json`.

## Out Of Scope

- No actual-result extraction.
- No EV or all-in adjusted EV.
- No played-pot filtering.
- No decision/action classification.
- No interpretation, coaching, leak detection, or Today / Review / Brain output.
- No frontend work.

## Validation Target

- `python3 tests/matrix_seed_tests.py`
- `PYTHONPYCACHEPREFIX=/private/tmp/opb_pycache python3 -m py_compile core/ingest/matrix_seed.py scripts/build_matrix_count_seed.py tests/matrix_seed_tests.py`
- `python3 scripts/build_matrix_count_seed.py --summary`
- Matrix seed output exists at `data/manifests/matrix_count_seed.json`.

## Report Destination

`reports/00_restart/005-matrix-count-seed-v0-report.md`
