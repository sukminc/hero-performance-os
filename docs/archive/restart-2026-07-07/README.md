# OPB Restart Archive - 2026-07-07

## Purpose

This archive freezes the current OPB working state before a Matrix-first restart.

The next phase should treat the current repo as research reference, not as the
active product shape.

## Product Reset

The clean product direction is:

> GG Poker hand history dump -> deduplicated personal database -> growing 13x13
> actual-result Matrix -> hand-class drilldown -> simple review candidates.

The product should first preserve user data and show factual hand-class outcomes.
Deep analytics can come later after the hand-history corpus keeps growing.

## Preserve

Keep these as first-class assets:

- `data/hero_v2.sqlite3`
  - processed local SQLite database
  - contains parsed hands, sessions, ingest files, reviews, and matrix source data
- `data/tmp_uploads_public/`
  - uploaded GG Poker zip/txt packets and expanded packet files
- `data/raw_intake_legacy/opb-poker-legacy-drop/`
  - former untracked `opb-poker/` raw intake candidate folder
  - contains additional zip/txt/png assets preserved as data, not active code

These are the current durable data assets. Do not delete them during cleanup.

## Archived Here

- `tracked-changes.patch`
  - binary-safe patch of tracked source changes at restart time
- `git-status-short.txt`
  - git working tree state at restart time
- `untracked-files.txt`
  - all untracked files at restart time
- `untracked-nondata-files.txt`
  - untracked files excluding raw/processed data folders and this archive
- `untracked-nondata-files.tgz`
  - tar archive of untracked non-data research/code/report files
- `raw-and-processed-data-files.txt`
  - pre-clean inventory of preserved data files under `data/` and `opb-poker/`
- `post-clean-data-files.txt`
  - post-clean inventory of preserved files under `data/`
- `post-clean-git-status-short.txt`
  - git working tree state after cleanup
- `post-clean-disk-usage.txt`
  - disk usage after cleanup

## Restart Rules

- Do not carry old complexity forward by default.
- Do not rebuild Today / Review / Brain first.
- Do not optimize public landing pages before the Matrix data loop is reliable.
- Do not treat solver/GTO judgment as the first product promise.
- Do not discard raw GG Poker files or processed Matrix source data.

## New MVP Scope

Start from the smallest believable loop:

1. User uploads GG Poker hand-history zip/txt files.
2. System fingerprints files and hands.
3. Duplicate files/hands are skipped.
4. New hands are appended to the user's durable corpus.
5. System rebuilds a 13x13 actual-result Matrix.
6. User can click a hand class and see factual result drivers.

The first commercial promise should be data preservation plus personal baseline
visibility, not AI coaching.

## Reference, Not Active Truth

Existing reports, docs, frontend pages, AOF work, Brain/Today/Review logic, and
operator tooling may be referenced later, but they should not define the new
active product architecture unless intentionally reintroduced.
