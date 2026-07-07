# Task 002 - Raw File Manifest V0 Report

## TASK

Implement the first data-processing artifact for the Matrix restart: a raw file
manifest that inventories preserved text, zip, image, SQLite, and unsupported
files under `data/`.

## WHAT I CHANGED

- Added `core/ingest/raw_manifest.py`.
- Added `scripts/build_raw_file_manifest.py`.
- Added `tests/raw_manifest_tests.py`.
- Added `tasks/00_restart/002-raw-file-manifest-v0.md`.
- Added this report.
- Generated `data/manifests/raw_file_manifest.json`.

## ARCHITECTURE IMPACT

This is the first implementation step toward OPB as a cumulative data-processing
system.

The manifest does not parse or interpret poker decisions. It establishes the
source-file ledger needed before deeper analytics:

- immutable file identity through SHA-256,
- input kind classification,
- source bucket classification,
- duplicate file groups,
- text hand block counts,
- zip member inspection,
- image preservation status,
- processed database preservation status.

## DECISIONS MADE

- `.txt` files are `text_hand_history_candidate`.
- `.zip` files are `zip_archive`.
- `.png`, `.jpg`, `.jpeg`, and `.webp` files are `image_evidence`.
- `.sqlite`, `.sqlite3`, and `.db` files are `processed_sqlite`.
- Duplicate groups are based on exact SHA-256 equality.
- Text hand block count is optional and skipped by default because the current
  restart priority is fast file inventory plus duplicate detection.
- The manifest is written under ignored `data/manifests/` because it is a
  generated processed-data artifact.
- Progress output is throttled with `--progress-every` so large local inventories
  do not flood the terminal.

## RISKS / OPEN QUESTIONS

- The manifest records current paths but does not yet move files into the new
  canonical naming convention.
- Zip member files are inspected but not re-expanded in this task.
- Hand-level dedupe is still future work.
- Image OCR remains future work.

## OUT OF SCOPE

- No normalized hand table.
- No session table rebuild.
- No Matrix aggregate rebuild.
- No frontend surface.
- No coaching interpretation.

## TEST / VALIDATION

Passed:

- `python3 tests/raw_manifest_tests.py`
- `PYTHONPYCACHEPREFIX=/private/tmp/opb_pycache python3 -m py_compile core/ingest/raw_manifest.py scripts/build_raw_file_manifest.py tests/raw_manifest_tests.py`
- `python3 scripts/build_raw_file_manifest.py --summary --progress --progress-every 100`

Generated manifest:

- `data/manifests/raw_file_manifest.json`

Current manifest totals:

- `file_count`: 933
- `total_size_bytes`: 165,367,198
- `input_kind_counts`: 909 text candidates, 19 zip archives, 4 images, 1 SQLite
- `source_bucket_counts`: 901 expanded upload members, 19 legacy raw intake
  files, 12 uploaded source archives, 1 processed database
- `duplicate_group_count`: 153
- `duplicate_file_count`: 760
- `text_hand_block_count_mode`: skipped

## RECOMMENDED NEXT STEP

Implement Hand Extraction Ledger V0:

- read text candidates from the manifest,
- split hand blocks,
- assign stable normalized hand ids,
- detect duplicate hands,
- write append-only hand extraction counters.
