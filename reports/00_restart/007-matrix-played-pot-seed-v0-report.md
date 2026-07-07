# Task 007 - Matrix Played-Pot Seed V0 Report

## TASK

Implement dealt-vs-played-pot separation for the restart Matrix dataset.

## WHAT I CHANGED

- Added `core/ingest/matrix_played_pot_seed.py`.
- Added `scripts/build_matrix_played_pot_seed.py`.
- Added `tests/matrix_played_pot_seed_tests.py`.
- Added `tasks/00_restart/007-matrix-played-pot-seed-v0.md`.
- Added this report.
- Generated `data/manifests/matrix_played_pot_seed.json`.

## ARCHITECTURE IMPACT

This adds a new derived data-processing layer after Matrix result seed:

- dealt exposure remains visible,
- played-pot samples are counted separately,
- forced posts and BB checks no longer look like performance samples,
- future 13x13 analysis can use played-pot count by default while still showing
  dealt count as context.

This is still factual dataset shaping, not interpretation.

## DECISIONS MADE

- Played-pot evidence is Hero voluntarily calling, raising, betting, or going
  all-in preflop.
- Forced antes, blind posts, folds, and checks are excluded from played-pot
  counts.
- The seed stores reason counts so operator review can inspect what was excluded.
- Outcome counts are carried from Matrix result seed but no new result meaning is
  inferred.

## RISKS / OPEN QUESTIONS

- V0 only classifies preflop voluntary entry/escalation.
- Some unusual GG action text may be classified as unclassified/unplayed until
  explicitly supported.
- Limp/call/raise sizing taxonomy remains future work.
- Net chip/BB result remains future work.

## OUT OF SCOPE

- No EV.
- No BB result.
- No action sizing taxonomy.
- No leak/strength interpretation.
- No frontend surface.

## TEST / VALIDATION

Passed:

- `python3 tests/matrix_played_pot_seed_tests.py`
- `PYTHONPYCACHEPREFIX=/private/tmp/opb_pycache python3 -m py_compile core/ingest/matrix_played_pot_seed.py scripts/build_matrix_played_pot_seed.py tests/matrix_played_pot_seed_tests.py`
- `python3 scripts/build_matrix_played_pot_seed.py --summary`

The generated Matrix played-pot seed should exist at:

- `data/manifests/matrix_played_pot_seed.json`

Current Matrix played-pot seed totals:

- `dealt_hand_count`: 9,330
- `played_pot_count`: 2,888
- `folded_or_unplayed_exposure_count`: 6,442
- `played_pot_rate`: 0.3095
- `distinct_hand_class_count`: 169
- `played_pot_reason_counts`:
  - `hero_voluntary_preflop_action`: 2,888
  - `no_hero_voluntary_preflop_action`: 6,339
  - `no_hero_preflop_action`: 103

Sample hand-class separation:

- `AA`: 61 dealt, 58 played pots
- `AKs`: 25 dealt, 25 played pots
- `JTo`: 105 dealt, 57 played pots
- `72o`: 83 dealt, 0 played pots

## RECOMMENDED NEXT STEP

Implement Matrix Preflop Action Seed V0:

- split played pots into first Hero action buckets,
- preserve examples for operator inspection,
- keep action taxonomy factual before adding any strategic interpretation.
