# Task 005 - Matrix Count Seed V0 Report

## TASK

Implement the first count-only 13x13 Matrix seed from the restart data ledgers.

## WHAT I CHANGED

- Added `core/ingest/matrix_seed.py`.
- Added `scripts/build_matrix_count_seed.py`.
- Added `tests/matrix_seed_tests.py`.
- Added `tasks/00_restart/005-matrix-count-seed-v0.md`.
- Added this report.
- Generated `data/manifests/matrix_count_seed.json`.

## ARCHITECTURE IMPACT

This adds the first Matrix-ready derived count layer on top of the restart data
pipeline:

- raw source files remain preserved,
- hand blocks remain rebuildable from source file plus line range,
- duplicate hand occurrences do not inflate Matrix counts,
- Hero hole-card extraction is deterministic,
- all 169 13x13 cells are present even when counts are zero.

This remains data processing, not interpretation.

## DECISIONS MADE

- Counting unit is `unique_raw_hand_fingerprint`.
- Source scope is only `hand_history_text` assets from the processable dataset
  index.
- Hero hole cards are extracted only from exact `Dealt to Hero [...]` lines.
- Hand classes use canonical labels:
  - pairs: `AA`, `77`
  - suited non-pairs: `AQs`
  - offsuit non-pairs: `KTo`
- Result extraction is explicitly not part of V0.
- Missing Hero cards are counted and sampled rather than guessed.

## RISKS / OPEN QUESTIONS

- V0 does not distinguish dealt-only from voluntarily played pots.
- V0 does not extract BB result, win/loss, or stack-normalized outcome.
- V0 may miss hands if the Hero line differs from GG's normal
  `Dealt to Hero [...]` text.
- Physical materialization of the canonical dataset still remains future work.

## OUT OF SCOPE

- No EV.
- No actual-result matrix.
- No action taxonomy.
- No played-pot policy.
- No coaching interpretation.
- No frontend surface.

## TEST / VALIDATION

Passed:

- `python3 tests/matrix_seed_tests.py`
- `PYTHONPYCACHEPREFIX=/private/tmp/opb_pycache python3 -m py_compile core/ingest/matrix_seed.py scripts/build_matrix_count_seed.py tests/matrix_seed_tests.py`
- `python3 scripts/build_matrix_count_seed.py --summary`

The generated Matrix seed should exist at:

- `data/manifests/matrix_count_seed.json`

Current Matrix seed totals:

- `source_hand_occurrence_count`: 25,293
- `unique_hand_fingerprint_count`: 9,454
- `duplicate_occurrences_skipped`: 15,839
- `classified_unique_hand_count`: 9,330
- `missing_hero_cards_unique_hand_count`: 124
- `distinct_hand_class_count`: 169
- `matrix_cells`: 169

Sample cell counts:

- `AA`: 61
- `AKs`: 25
- `72o`: 83

## RECOMMENDED NEXT STEP

Implement Matrix Result Seed V0:

- extract deterministic hand result where the GG summary supports it,
- keep result fields blank when unsupported,
- separate dealt counts from played-pot counts,
- avoid leak/strength interpretation until result extraction is reliable.
