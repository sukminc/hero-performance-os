# Task 004 - Processable Dataset Index V0

## Business Question

Can OPB turn preserved raw assets plus extracted hand blocks into a processable
dataset index with stable naming conventions before moving or interpreting data?

## Objective

Add a dataset index builder that combines the raw file manifest and hand
extraction ledger, classifies source assets into processable dataset kinds, and
assigns canonical relative paths for later organized storage.

## Scope

- Read `data/manifests/raw_file_manifest.json`.
- Read `data/manifests/hand_extraction_ledger.json`.
- Classify assets as:
  - `hand_history_text`
  - `tournament_summary_text`
  - `text_unclassified`
  - `zip_archive`
  - `image_evidence`
  - `processed_database`
  - `unsupported_source`
- Generate canonical relative paths under:
  - `dataset_v0/{player_id}/{yyyy}/{mm}/{dd}/{asset_kind}/{sha12}-{safe_original_name}`
- Extract dataset dates from GG filenames or image-style date filenames.
- Preserve source provenance and processing state.
- Write `data/manifests/processable_dataset_index.json`.

## Out Of Scope

- No physical file moves.
- No database writes.
- No image OCR.
- No zip re-expansion.
- No 13x13 matrix aggregation.
- No interpretation or coaching.

## Validation Target

- `python3 tests/dataset_index_tests.py`
- `PYTHONPYCACHEPREFIX=/private/tmp/opb_pycache python3 -m py_compile core/ingest/dataset_index.py scripts/build_processable_dataset_index.py tests/dataset_index_tests.py`
- `python3 scripts/build_processable_dataset_index.py --summary`
- Dataset index output exists at `data/manifests/processable_dataset_index.json`.

## Report Destination

`reports/00_restart/004-processable-dataset-index-v0-report.md`
