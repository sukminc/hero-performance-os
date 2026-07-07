# Task 001 - Data Processing First Contract

## Business Question

Can OPB restart around the simple product loop where users keep dumping GG Poker
files and OPB turns those dumps into a growing, deduplicated, processable hand
history dataset?

## Objective

Define the V0 data-processing contract for text, zip, and image inputs so future
implementation starts from raw preservation, file/hand dedupe, cumulative counts,
and Matrix-ready records rather than interpretation-first product surfaces.

## Scope

- Document supported input kinds: `.txt`, `.zip`, and images.
- Define source preservation metadata.
- Define naming convention for raw and expanded files.
- Define dedupe levels for source files and hands.
- Define minimum processing stages and statuses.
- Define V0 dataset outputs and cumulative product counters.
- Explicitly defer interpretation layers.

## Out Of Scope

- New parser implementation.
- New database migration.
- Frontend changes.
- Today / Review / Brain.
- AOF coaching.
- LLM interpretation.

## Validation Target

- Contract exists at `docs/data_processing_contract_v0.md`.
- Restart plan exists at `docs/restart_matrix_data_plan.md`.
- Report exists at `reports/00_restart/001-data-processing-first-contract-report.md`.
- Current preserved data inventory still exists under `data/`.

## Report Destination

`reports/00_restart/001-data-processing-first-contract-report.md`
