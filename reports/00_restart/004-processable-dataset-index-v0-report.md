# Task 004 - Processable Dataset Index V0 Report

## TASK

Implement a processable dataset index that turns preserved source files and
hand extraction results into canonical dataset records.

## WHAT I CHANGED

- Added `core/ingest/dataset_index.py`.
- Added `scripts/build_processable_dataset_index.py`.
- Added `tests/dataset_index_tests.py`.
- Added `tasks/00_restart/004-processable-dataset-index-v0.md`.
- Added this report.
- Generated `data/manifests/processable_dataset_index.json`.

## ARCHITECTURE IMPACT

This creates the first bridge from raw intake facts to an organized dataset
layout:

- raw files remain untouched,
- the raw manifest remains the source-file ledger,
- the hand extraction ledger remains the hand occurrence ledger,
- the processable dataset index classifies each asset and assigns a future
  canonical relative path.

This keeps the restart aligned with data processing first. It lets OPB validate
naming and classification before physically reorganizing files.

## DECISIONS MADE

- Canonical paths are proposed under
  `dataset_v0/{player_id}/{yyyy}/{mm}/{dd}/{asset_kind}/{sha12}-{safe_original_name}`.
- The default `player_id` is `hero`.
- GG filename dates such as `GG20260401...` become `2026/04/01`.
- Image-style filename dates such as `2026-04-03...` become `2026/04/03`.
- Files without a clear date go under `unknown/unknown/unknown`.
- Text files with extracted hand blocks become `hand_history_text`.
- Zero-hand text files starting with `Tournament #...` become
  `tournament_summary_text`.
- Zero-hand text files without recognized summary format become
  `text_unclassified`.
- Images remain preserved with OCR pending.

## RISKS / OPEN QUESTIONS

- Canonical paths are not yet materialized on disk.
- Dataset dates currently come from filenames only, not from parsed hand headers.
- Tournament summary parsing is minimal and only reads the first non-empty line.
- Zip archives are indexed as preserved archives; expansion lineage is still
  inferred from current paths rather than a canonical archive-member table.

## OUT OF SCOPE

- No physical reorganization of raw assets.
- No archive expansion changes.
- No image OCR.
- No 13x13 matrix aggregation.
- No EV or actual-result analytics.
- No interpretation layer.

## TEST / VALIDATION

Passed:

- `python3 tests/dataset_index_tests.py`
- `PYTHONPYCACHEPREFIX=/private/tmp/opb_pycache python3 -m py_compile core/ingest/dataset_index.py scripts/build_processable_dataset_index.py tests/dataset_index_tests.py`
- `python3 scripts/build_processable_dataset_index.py --summary`

The generated dataset index should exist at:

- `data/manifests/processable_dataset_index.json`

Current dataset index totals:

- `asset_count`: 933
- `hand_history_text`: 548
- `tournament_summary_text`: 361
- `zip_archive`: 19
- `image_evidence`: 4
- `processed_database`: 1
- `hand_history_occurrence_count`: 25,293
- `known_date_asset_count`: 913
- `unknown_date_asset_count`: 20

## RECOMMENDED NEXT STEP

Implement Matrix Count Seed V0:

- read `hand_history_text` assets from the processable dataset index,
- use unique hand fingerprints from the hand extraction ledger,
- extract Hero hole cards where deterministically available,
- map hands into 13x13 classes,
- count only what can be proven from text,
- leave unknowns blank rather than inventing results.
