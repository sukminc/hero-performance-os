# Task 003 - Hand Extraction Ledger V0

## Business Question

Can OPB turn preserved text hand-history candidates into cumulative hand-block
counts before interpretation?

## Objective

Add a deterministic hand extraction ledger that reads the raw file manifest,
splits text candidates into hand blocks, assigns raw block fingerprints, detects
hand-level duplicates, and writes cumulative counts.

## Scope

- Read `data/manifests/raw_file_manifest.json`.
- Process only `text_hand_history_candidate` records.
- Split blocks beginning with `Poker Hand #` or `Hand #`.
- Store source file provenance, source sequence, line range, header, hand ref,
  optional tournament id, optional played-at timestamp, and header parse status.
- Assign hand identity by SHA-256 of normalized raw hand block text.
- Generate duplicate hand group counts.
- Write `data/manifests/hand_extraction_ledger.json`.

## Out Of Scope

- No 13x13 classification.
- No EV or result interpretation.
- No normalized canonical hand table.
- No database writes.
- No coaching surface.
- No image OCR.

## Validation Target

- `python3 tests/hand_extraction_tests.py`
- `PYTHONPYCACHEPREFIX=/private/tmp/opb_pycache python3 -m py_compile core/ingest/hand_extraction.py scripts/build_hand_extraction_ledger.py tests/hand_extraction_tests.py`
- `python3 scripts/build_hand_extraction_ledger.py --summary --progress --progress-every 100`
- Ledger output exists at `data/manifests/hand_extraction_ledger.json`.

## Report Destination

`reports/00_restart/003-hand-extraction-ledger-v0-report.md`
