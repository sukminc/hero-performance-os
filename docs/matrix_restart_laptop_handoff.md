# Matrix Restart Laptop Handoff

## Purpose

Use this when continuing the OPB Matrix restart on another laptop.

The restart is data-processing-first:

```text
raw files -> raw manifest -> hand extraction ledger -> processable dataset index
-> matrix count seed -> matrix result seed -> matrix played-pot seed
```

Interpretation, coaching, EV, and frontend polish are intentionally deferred.

## Branch

Use:

```bash
git fetch origin
git checkout matrix-restart
git pull origin matrix-restart
```

## Local Data Rule

The `data/` directory is ignored and is not pushed to GitHub.

To reproduce the current local pipeline on another laptop, that laptop needs the
raw OPB data folder restored locally, including files equivalent to:

```text
data/hero_v2.sqlite3
data/raw_intake_legacy/
data/tmp_uploads_public/
```

Generated manifests are also ignored. Rebuild them locally.

## Rebuild Commands

Run from the repo root:

```bash
python3 scripts/build_raw_file_manifest.py --summary --progress --progress-every 100
python3 scripts/build_hand_extraction_ledger.py --summary --progress --progress-every 100
python3 scripts/build_processable_dataset_index.py --summary
python3 scripts/build_matrix_count_seed.py --summary
python3 scripts/build_matrix_result_seed.py --summary
python3 scripts/build_matrix_played_pot_seed.py --summary
```

Expected generated files:

```text
data/manifests/raw_file_manifest.json
data/manifests/hand_extraction_ledger.json
data/manifests/processable_dataset_index.json
data/manifests/matrix_count_seed.json
data/manifests/matrix_result_seed.json
data/manifests/matrix_played_pot_seed.json
```

## Current Reference Counts

On the original restart machine, the latest generated counts were:

- source assets: 933
- text hand-history files: 548
- tournament summary text files: 361
- zip archives: 19
- images: 4
- unique hand fingerprints: 9,454
- classified unique hands: 9,330
- Matrix hand classes present: 169 / 169
- Matrix result hands: 9,330
- Matrix played pots: 2,888
- folded/unplayed exposure: 6,442

Different counts on another laptop usually mean the local `data/` folder is not
the same corpus yet.

## Validation

Run:

```bash
python3 tests/raw_manifest_tests.py
python3 tests/hand_extraction_tests.py
python3 tests/dataset_index_tests.py
python3 tests/matrix_seed_tests.py
python3 tests/matrix_result_seed_tests.py
python3 tests/matrix_played_pot_seed_tests.py
PYTHONPYCACHEPREFIX=/private/tmp/opb_pycache python3 -m py_compile \
  core/ingest/raw_manifest.py \
  core/ingest/hand_extraction.py \
  core/ingest/dataset_index.py \
  core/ingest/matrix_seed.py \
  core/ingest/matrix_result_seed.py \
  core/ingest/matrix_played_pot_seed.py \
  scripts/build_raw_file_manifest.py \
  scripts/build_hand_extraction_ledger.py \
  scripts/build_processable_dataset_index.py \
  scripts/build_matrix_count_seed.py \
  scripts/build_matrix_result_seed.py \
  scripts/build_matrix_played_pot_seed.py \
  tests/raw_manifest_tests.py \
  tests/hand_extraction_tests.py \
  tests/dataset_index_tests.py \
  tests/matrix_seed_tests.py \
  tests/matrix_result_seed_tests.py \
  tests/matrix_played_pot_seed_tests.py
```

## Next Slice

The next clean backend slice is:

```text
Matrix Preflop Action Seed V0
```

Goal:

- split played pots into factual first-action buckets,
- preserve source examples,
- avoid strategic interpretation until taxonomy is validated.
