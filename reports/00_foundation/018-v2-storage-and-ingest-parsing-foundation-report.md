# TASK

Create the first executable V2 implementation packet by adding the initial storage/schema boundary and the first ingest/parsing path under `core/`.

# WHAT I CHANGED

- Added V2 storage files:
  - `core/storage/schema.sql`
  - `core/storage/models.py`
  - `core/storage/postgres.py`
  - `core/storage/repositories.py`
- Added V2 parsing files:
  - `core/parsing/gg_parser.py`
  - `core/parsing/parse_quality.py`
  - `core/parsing/hand_normalizer.py`
  - `core/parsing/session_builder.py`
- Added V2 ingest files:
  - `core/ingest/duplicate_guard.py`
  - `core/ingest/file_ingest.py`
  - `core/ingest/ingest_jobs.py`

The new V2 path now supports:

- file hashing and duplicate detection
- zero-hand safe failure
- GG text parsing into a structured session packet
- session and hand normalization
- Postgres persistence into the new V2 schema

# ARCHITECTURE IMPACT

The repo now has the first real executable V2 path:

`file -> duplicate guard -> parse -> parse quality -> session record -> hand records -> Postgres`

This is intentionally smaller than the V1 operator/truth path.
It creates a clean canonical center for the next layers:

- evidence
- memory
- surfaces

# DECISIONS MADE

- Reused V1 concepts, but reimplemented them by V2 responsibility instead of copying V1 folder structure.
- Chose Postgres as the first V2 canonical persistence target.
- Kept the parser intentionally minimal and inspectable for the first packet.
- Preserved duplicate-safe and zero-hand-safe behavior as non-negotiable V2 rules.

# RISKS / OPEN QUESTIONS

- The current parser is intentionally conservative and does not yet capture all V1-enriched interpretation detail.
- The schema is the first V2 cut and will likely evolve once evidence and memory layers land.
- Repository schema loading currently assumes commands are run from the repo root.

# OUT OF SCOPE

- evidence extraction
- cumulative memory updates
- Today / Review / Brain assembly
- operator review flows
- UI/API transport

# TEST / VALIDATION

- No runtime DB test executed in this task.
- Structural validation completed by creating the V2 modules and verifying they align with the planned migration responsibilities.
- The ingest path includes explicit duplicate and zero-hand handling logic.

# RECOMMENDED NEXT STEP

Implement the V2 evidence layer next:

1. `core/evidence/*`
2. write `session_evidence` rows from parsed hands
3. define the first five evidence types:
   - hand class underperformance
   - style drift
   - stable strength
   - field distortion
   - contamination risk
