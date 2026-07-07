# Task 003 - Hand Extraction Ledger V0 Report

## TASK

Implement the first hand-level cumulative counting artifact for the Matrix
restart.

## WHAT I CHANGED

- Added `core/ingest/hand_extraction.py`.
- Added `scripts/build_hand_extraction_ledger.py`.
- Added `tests/hand_extraction_tests.py`.
- Added `tasks/00_restart/003-hand-extraction-ledger-v0.md`.
- Added this report.
- Generated `data/manifests/hand_extraction_ledger.json`.

## ARCHITECTURE IMPACT

This adds the next deterministic layer after raw file inventory:

- raw files stay preserved,
- the raw manifest remains the source-file ledger,
- text candidates become hand-block occurrences,
- hand-block identity is based on normalized raw text SHA-256,
- duplicate hand occurrences are visible before any interpretation starts.

This supports the product direction of cumulative numbers first, coaching later.

## DECISIONS MADE

- V0 processes only `text_hand_history_candidate` files from the raw manifest.
- A hand block starts at `Poker Hand #` or `Hand #`.
- The ledger does not grade, classify, or interpret any hand.
- The hand fingerprint is SHA-256 of normalized raw block text.
- GG header metadata is opportunistic: parsed values are stored when the existing
  GG header parser recognizes the header, otherwise the block remains counted
  with `header_parse_status = unparsed`.
- The generated ledger is written under ignored `data/manifests/`.

## RISKS / OPEN QUESTIONS

- Raw block fingerprinting is intentionally conservative; the same GG hand with
  tiny formatting differences may appear as different fingerprints.
- The ledger does not yet choose a canonical occurrence among duplicates.
- Hand-level duplicate groups are exact raw block duplicates, not semantic hand
  duplicates.
- Existing SQLite processed data has not yet been reconciled with this ledger.
- 361 text candidates produced zero hand blocks. Sample paths suggest many are
  tournament summary/result text files rather than hand-history block files.
  They should be classified explicitly in the next intake refinement.

## OUT OF SCOPE

- No 13x13 matrix aggregation.
- No hand result extraction.
- No EV comparison.
- No canonical Postgres/SQLite writes.
- No Today / Review / Brain output.
- No frontend work.

## TEST / VALIDATION

Passed:

- `python3 tests/hand_extraction_tests.py`
- `PYTHONPYCACHEPREFIX=/private/tmp/opb_pycache python3 -m py_compile core/ingest/hand_extraction.py scripts/build_hand_extraction_ledger.py tests/hand_extraction_tests.py`
- `python3 scripts/build_hand_extraction_ledger.py --summary --progress --progress-every 100`

The generated ledger should exist at:

- `data/manifests/hand_extraction_ledger.json`

Current ledger totals:

- `text_file_count`: 909
- `files_with_hands`: 548
- `files_with_zero_hands`: 361
- `hand_occurrence_count`: 25,293
- `unique_hand_fingerprint_count`: 9,454
- `duplicate_hand_group_count`: 4,040
- `duplicate_hand_occurrence_count`: 19,879
- `header_parse_status_counts`: 25,293 parsed

## RECOMMENDED NEXT STEP

Implement Matrix Count Seed V0:

- read unique hand fingerprints from the hand extraction ledger,
- extract Hero hole cards when available,
- map hole cards into 13x13 classes,
- count occurrences, wins/losses/profit where deterministic result extraction is
  available,
- leave unknown result fields blank rather than inventing interpretation.
