# TASK

Add a first V2 Today read/API packet so the cumulative Today surface can be fetched from snapshots or rebuilt on demand.

# WHAT I CHANGED

- Extended `core/storage/repositories.py` with:
  - `fetch_latest_surface_snapshot(...)`
  - `fetch_latest_session_id(...)`
- Added:
  - `app/api/__init__.py`
  - `app/api/today.py`

The new Today API path supports:

- reading the latest `today` snapshot for a player
- forcing a fresh Today rebuild from current cumulative memory
- rebuilding automatically when no snapshot exists yet

# ARCHITECTURE IMPACT

V2 now has its first callable read path.
This means the architecture no longer stops at background data generation; it now supports:

`memory -> Today surface -> latest snapshot fetch or on-demand rebuild`

This is the first step toward a real Command Center surface and app transport.

# DECISIONS MADE

- Kept the API packet simple and local-first.
- Used snapshot-first semantics:
  - read latest snapshot when available
  - rebuild when requested or when no snapshot exists
- Reused the latest player session id as the default session anchor when rebuilding Today.

# RISKS / OPEN QUESTIONS

- There is still no HTTP server or web route wrapper; this is currently a Python app-layer entrypoint.
- Snapshot freshness policy is still basic. Later we may want explicit stale/rebuild rules.
- If no sessions exist yet, the Today rebuild path will still produce a sparse result based on empty memory.

# OUT OF SCOPE

- web UI transport
- Review / Brain read APIs
- Command Center API aggregation
- auth/access control

# TEST / VALIDATION

- Python syntax validation should be run for the new app API file and updated repository file.
- No live database request was executed in this task.

# RECOMMENDED NEXT STEP

Build the first Command Center aggregation packet next:

1. Today payload
2. top memory items
3. current state summary
4. confidence block

That would create the first real Hero-facing V2 read model.
