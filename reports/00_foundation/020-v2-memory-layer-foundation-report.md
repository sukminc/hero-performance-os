# TASK

Implement the first V2 memory layer so `session_evidence` can become cumulative `memory_items` with initial lifecycle states.

# WHAT I CHANGED

- Added V2 memory modules:
  - `core/memory/memory_models.py`
  - `core/memory/memory_status.py`
  - `core/memory/memory_queries.py`
  - `core/memory/memory_updater.py`
- Added `MemoryItemRecord` to `core/storage/models.py`
- Extended `core/storage/repositories.py` with:
  - `fetch_session_evidence(...)`
  - `get_memory_item(...)`
  - `upsert_memory_item(...)`
- Added a uniqueness constraint for `(player_id, memory_type, memory_key)` in `core/storage/schema.sql`
- Wired memory updates into `core/ingest/file_ingest.py`
- Extended ingest job output with `memory_count`

The V2 path now supports:

`file -> parse -> evidence -> memory_items`

# ARCHITECTURE IMPACT

V2 now has a true cumulative layer.
This means the next surface work can consume `memory_items` instead of rebuilding interpretation from raw hands or one-session evidence every time.

The first lifecycle is intentionally simple:

- `watch`
- `active`
- `baseline`
- `resolved`

# DECISIONS MADE

- Positive evidence can promote directly toward `baseline`.
- Negative or shift evidence starts as `watch` and can escalate to `active`.
- Memory identity is based on `(player_id, memory_type, memory_key)`.
- Suggested adjustments are attached at the memory layer so Today can later compress from memory instead of from evidence.

# RISKS / OPEN QUESTIONS

- The first status logic is intentionally coarse and will likely be refined once multiple sessions are replayed through it.
- There is no operator correction flow attached to memory yet.
- `resolved` is defined in the lifecycle but not yet actively produced by any evidence/update rule.

# OUT OF SCOPE

- Today surface rebuild
- Review / Brain rebuild
- operator review of memory items
- historical snapshotting of memory transitions

# TEST / VALIDATION

- Python syntax validation should be run across the new memory files and updated ingest/storage files.
- No live Postgres migration or end-to-end ingest execution was run in this task.

# RECOMMENDED NEXT STEP

Implement the first V2 Today surface packet:

1. read `memory_items`
2. prioritize `active` and `baseline` items
3. generate `current state`
4. output 1-3 next adjustments with confidence-aware language
