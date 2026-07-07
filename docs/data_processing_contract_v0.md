# OPB Data Processing Contract V0

## Product Job

OPB's restart product job is data accumulation.

The first user experience is:

1. user dumps GG Poker files,
2. OPB preserves the source files,
3. OPB detects duplicates,
4. OPB extracts processable hand records,
5. OPB appends only new records,
6. OPB updates cumulative counts and the 13x13 Matrix dataset.

Interpretation can kick in later. The first proof is that the user's poker data
corpus keeps growing cleanly.

## First Product Promise

GG Poker hand histories are time-limited. OPB should help the user preserve a
growing personal hand-history database before the source export window expires.

The product should lead with cumulative numbers:

- source files preserved,
- files processed,
- duplicate files skipped,
- sessions discovered,
- hands extracted,
- duplicate hands skipped,
- new hands added,
- hand classes seen,
- last successful dump,
- recent 7-day and 30-day ingestion volume.

## Supported Input Kinds

The ingestion boundary must accept:

- `.txt`
  - GG Poker hand-history text exports.
- `.zip`
  - archives containing one or more `.txt` hand-history files and possibly
    screenshots or other support files.
- image files such as `.png`, `.jpg`, `.jpeg`, `.webp`
  - preserved as raw source evidence.
  - not required to produce hand records in V0.

Unsupported files should be preserved with status `unsupported`, not silently
discarded.

## Source Preservation Rule

Every user dump must be stored as immutable raw source.

Raw source storage should preserve:

- original filename,
- original extension,
- byte size,
- SHA-256 file hash,
- upload/dump timestamp,
- source channel,
- player/user id,
- normalized storage path,
- processing status,
- parser version.

Raw files must not be overwritten by normalized files.

## Naming Convention

Raw source files should be organized by user and dump event:

```text
data/raw/{player_id}/{yyyy}/{mm}/{dd}/{dump_id}/source/{ordinal}-{sha256_12}-{safe_original_name}
```

Expanded archive members should be organized under the same dump:

```text
data/raw/{player_id}/{yyyy}/{mm}/{dd}/{dump_id}/expanded/{ordinal}-{sha256_12}-{safe_member_name}
```

Normalized records should use stable ids derived from source truth:

```text
file_id = sha256(file bytes)
member_file_id = sha256(member file bytes)
hand_id = source_site + ":" + external_hand_id
session_id = player_id + ":" + source_site + ":" + tournament_id + ":" + source_file_date_or_dump_id
```

Different files must not collapse into the same file record.
Duplicate files must not be processed twice.
Duplicate hands must not be appended twice.

## Minimum Processing Stages

### 1. Raw Intake

Accept a dump and write source metadata before parsing.

Required statuses:

- `received`
- `duplicate_file`
- `expanded`
- `unsupported`
- `parse_failed`
- `processed`

### 2. File Expansion

For `.zip` inputs:

- compute hash for the zip,
- preserve the zip,
- extract members into the dump's expanded area,
- compute hash for every member,
- classify each member by extension and content sniffing.

### 3. Text Hand Extraction

For GG `.txt` inputs:

- split into individual hand blocks,
- extract external hand id,
- extract tournament id where available,
- extract started-at timestamp where available,
- extract Hero hole cards where available,
- normalize hand class into 13x13 labels,
- store parse confidence and parser version.

Zero-hand parse results must remain visible as parse failures or unsupported
inputs. They must not generate fake sessions, fake hands, fake Matrix rows, or
fake interpretation.

### 4. Image Preservation

For image inputs:

- preserve file and metadata,
- optionally attach to a dump or future review context,
- do not require OCR in V0,
- do not block text hand processing.

### 5. Deduplication

Dedupe must happen at two levels:

- file-level dedupe by SHA-256 file hash,
- hand-level dedupe by normalized `hand_id`.

If the same zip is uploaded twice, skip it.
If a different zip contains already-seen hand-history text files, skip duplicate
member files and duplicate hands while still recording the dump attempt.

## V0 Dataset Outputs

The first processed dataset should support:

- source file manifest,
- dump manifest,
- extracted hand table,
- session summary table,
- 13x13 hand-class aggregate table or rebuildable view,
- ingestion counters.

The V0 product surface should be able to say:

```text
You have preserved 933 source files.
OPB has extracted 27,280 processable hands.
169 / 169 starting-hand classes have appeared.
This dump added 312 new hands and skipped 4 duplicate files.
```

## Interpretation Boundary

V0 should not lead with coaching interpretation.

Allowed:

- factual counts,
- actual hand-class outcomes,
- coverage / sample size,
- duplicate and parse status,
- simple Matrix cells.

Deferred:

- leak diagnosis,
- Today / Review / Brain,
- AOF judgment,
- GTO comparison,
- emotional or strategic interpretation,
- LLM coaching language.

## Current Preserved Data

As of the restart archive:

- processed SQLite database: `data/hero_v2.sqlite3`
- preserved data files: `933`
- legacy raw intake folder: `data/raw_intake_legacy/opb-poker-legacy-drop/`
- restart archive: `docs/archive/restart-2026-07-07/`

This existing data should be treated as research/reference input for the new
data-processing-first implementation.
