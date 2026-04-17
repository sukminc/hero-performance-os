# TASK

Build the first V2 Command Center aggregation packet so Hero-facing state, Today, and top cumulative memory can be fetched as one read model.

# WHAT I CHANGED

- Added:
  - `core/surfaces/command_center.py`
  - `app/api/command_center.py`

The new Command Center packet:

- reuses the Today surface
- reads top memory items
- assembles a confidence block
- returns freshness/source metadata for Today

# ARCHITECTURE IMPACT

V2 now has its first aggregated Hero-facing read model.
Instead of fetching Today and memory separately, the Command Center packet returns:

- current state
- headline
- Today payload
- top memory
- confidence block
- source/freshness metadata

This is the first clean contract for the future Command Center screen.

# DECISIONS MADE

- Kept Command Center aggregation read-only.
- Reused Today snapshot-first behavior instead of duplicating surface rules.
- Limited top memory to a compact set suitable for operator-facing overview.

# RISKS / OPEN QUESTIONS

- The current Command Center is still a Python app-layer API, not an HTTP/web route.
- Memory ranking is currently inherited from repository ordering plus truncation.
- We may later want a dedicated Command Center ranking model separate from Today ranking.

# OUT OF SCOPE

- web UI implementation
- Session Lab API
- Memory Graph API
- auth/access control

# TEST / VALIDATION

- Python syntax validation should be run for the new Command Center files.
- No live database read was executed in this task.

# RECOMMENDED NEXT STEP

Choose the next Hero-facing slice:

1. Session Lab read/API packet
2. Memory Graph read/API packet

If the goal is inspection first, Session Lab is the better next move.
