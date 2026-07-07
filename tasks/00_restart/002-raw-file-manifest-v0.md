# Task 002 - Raw File Manifest V0

## Business Question

Can OPB inventory the current raw and processed data assets into a deterministic
manifest so the restart can focus on cumulative data processing before
interpretation?

## Objective

Add a small manifest builder that scans `data/`, classifies `.txt`, `.zip`,
image, SQLite, and unsupported files, computes SHA-256 hashes, identifies
duplicate file groups, and writes cumulative counts suitable for the first
data-processing product numbers.

## Scope

- Add a deterministic raw file manifest module.
- Add a CLI script to build `data/manifests/raw_file_manifest.json`.
- Add test coverage for file kind classification, duplicate groups, text hand
  block counts, zip member inspection, and source bucket assignment.
- Generate the manifest against the current preserved `data/` folder.

## Out Of Scope

- Parsing hands into normalized records.
- Reorganizing raw files on disk.
- OCR for image files.
- Frontend display.
- Coaching or interpretation.

## Validation Target

- `python3 tests/raw_manifest_tests.py`
- `python3 scripts/build_raw_file_manifest.py --summary --progress --progress-every 100`
- Manifest output exists at `data/manifests/raw_file_manifest.json`.
- Manifest totals match the current preserved data inventory.

## Report Destination

`reports/00_restart/002-raw-file-manifest-v0-report.md`
