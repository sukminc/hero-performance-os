# TASK

Implement the first V2 Today surface so cumulative memory can produce a current-state read and 1-3 next-session adjustments.

# WHAT I CHANGED

- Added `fetch_memory_items(...)` and `create_surface_snapshot(...)` to `core/storage/repositories.py`
- Added:
  - `core/surfaces/__init__.py`
  - `core/surfaces/surface_models.py`
  - `core/surfaces/today.py`

The new Today surface:

- reads `memory_items`
- prioritizes `active`, then `baseline`, then `watch`
- computes a first-pass `current_state`
- builds up to three adjustments from cumulative memory
- writes a `core.surface_snapshots` row for the generated Today payload

# ARCHITECTURE IMPACT

V2 now has its first memory-driven surface.
This is the first real point where the new architecture behaves like a performance system rather than a parsing pipeline:

`memory_items -> current_state + adjustments -> Today snapshot`

This creates a usable foundation for the eventual Command Center screen.

# DECISIONS MADE

- Today reads memory, not raw evidence.
- State vocabulary is intentionally small for the first pass:
  - `stable`
  - `drifting`
  - `contaminated`
  - `volatile_but_acceptable`
  - `unclear`
- Adjustments are capped at 3.
- Today snapshots are persisted immediately so historical state remains inspectable.

# RISKS / OPEN QUESTIONS

- Current-state logic is intentionally simple and will need refinement against real multi-session data.
- The surface currently relies on memory-level suggested adjustments, which are still heuristic.
- No API/UI transport has been added yet, so the Today surface is currently callable only as a core layer function.

# OUT OF SCOPE

- Review surface
- Brain surface
- operator review of Today emphasis
- Command Center UI
- end-to-end runtime execution against live Postgres

# TEST / VALIDATION

- Python syntax validation should be run for the new surface files and updated repository file.
- No runtime DB test was executed in this task.

# RECOMMENDED NEXT STEP

Build the first Command Center or API transport packet next:

1. expose Today through a simple application entrypoint
2. add a read path for the latest Today snapshot
3. begin wiring Session Lab and Memory Graph around the same cumulative V2 core
