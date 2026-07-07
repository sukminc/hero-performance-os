# Task 001 - Data Processing First Contract Report

## TASK

Define OPB's Matrix restart around data processing first: user file dumps become
preserved, deduplicated, cumulative, processable hand-history data before any
interpretation layer kicks in.

## WHAT I CHANGED

- Added `docs/data_processing_contract_v0.md`.
- Added `docs/restart_matrix_data_plan.md`.
- Added `tasks/00_restart/001-data-processing-first-contract.md`.
- Added this report.

## ARCHITECTURE IMPACT

The restart direction is now explicit:

- raw source preservation comes first,
- file and hand dedupe are required,
- `.txt`, `.zip`, and image inputs are accepted at the intake boundary,
- images are preserved as source evidence in V0 rather than forced into OCR,
- Matrix-ready processed data is the first product substrate,
- interpretation layers are deferred.

This supports future analytics by prioritizing dataset quality before coaching
language.

## DECISIONS MADE

- V0 product promise is cumulative data preservation, not advice.
- Raw files should use a user/date/dump-id source path.
- Zip members should be expanded under the same dump id and individually hashed.
- File-level dedupe uses SHA-256 file hash.
- Hand-level dedupe uses normalized source hand id.
- Zero-hand parses must be visible and must not emit fake hands, sessions,
  Matrix rows, or interpretation.
- Cumulative counts are first-value product metrics.

## RISKS / OPEN QUESTIONS

- The existing SQLite and old parser may not match the new naming convention yet.
- Image intake is preservation-only in V0; OCR/result extraction remains later.
- Production storage target is not reselected in this task.
- The current repo still contains old docs/code for richer interpretation, but
  the restart archive marks those as reference rather than active scope.

## OUT OF SCOPE

- No code implementation.
- No schema migration.
- No frontend work.
- No parser rewrite.
- No analytics or coaching interpretation.

## TEST / VALIDATION

Validated by file presence and current preserved data inventory:

- `docs/data_processing_contract_v0.md`
- `docs/restart_matrix_data_plan.md`
- `tasks/00_restart/001-data-processing-first-contract.md`
- `reports/00_restart/001-data-processing-first-contract-report.md`
- `data/hero_v2.sqlite3`
- `data/tmp_uploads_public/`
- `data/raw_intake_legacy/opb-poker-legacy-drop/`

Current restart archive recorded `933` preserved data files under `data/`.

## RECOMMENDED NEXT STEP

Implement the smallest ingestion ledger:

- create or rebuild a raw file manifest from `data/`,
- compute file hashes,
- classify text / zip / image inputs,
- record processing status,
- expose cumulative counters before adding any interpretation.
