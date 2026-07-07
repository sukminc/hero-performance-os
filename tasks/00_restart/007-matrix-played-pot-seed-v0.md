# Task 007 - Matrix Played-Pot Seed V0

## Business Question

Can OPB separate dealt exposure from Hero's voluntarily played preflop samples in
the Matrix dataset?

## Objective

Add a deterministic played-pot seed that reads the Matrix result seed, rehydrates
raw hand blocks, identifies whether Hero voluntarily entered or escalated the pot
preflop, and aggregates dealt vs played-pot counts by hand class.

## Scope

- Read `data/manifests/matrix_result_seed.json`.
- Rehydrate raw hand blocks from source path and line range.
- Inspect preflop lines from `*** HOLE CARDS ***` until flop/showdown/summary.
- Treat Hero preflop `calls`, `raises`, `bets`, `all-in`, or `all in` as played
  pot evidence.
- Exclude forced antes, blind posts, folds, and checks from played-pot counts.
- Aggregate by hand class:
  - dealt count,
  - played-pot count,
  - folded/unplayed exposure count,
  - played-pot outcome counts,
  - dealt outcome counts.
- Write `data/manifests/matrix_played_pot_seed.json`.

## Out Of Scope

- No leak interpretation.
- No EV or BB result.
- No postflop played-pot classification.
- No sizing taxonomy.
- No frontend work.

## Validation Target

- `python3 tests/matrix_played_pot_seed_tests.py`
- `PYTHONPYCACHEPREFIX=/private/tmp/opb_pycache python3 -m py_compile core/ingest/matrix_played_pot_seed.py scripts/build_matrix_played_pot_seed.py tests/matrix_played_pot_seed_tests.py`
- `python3 scripts/build_matrix_played_pot_seed.py --summary`
- Matrix played-pot seed output exists at `data/manifests/matrix_played_pot_seed.json`.

## Report Destination

`reports/00_restart/007-matrix-played-pot-seed-v0-report.md`
