# TASK

Build the first V2 Memory Graph read/API packet so cumulative memory can be inspected by status, type, and recent touch order.

# WHAT I CHANGED

- Added:
  - `core/surfaces/memory_graph.py`
  - `app/api/memory_graph.py`

The new Memory Graph packet returns:

- cumulative memory summary counts
- status buckets
- type buckets
- latest touched memory items

# ARCHITECTURE IMPACT

V2 now has the third major Hero-facing read path:

- Today / Command Center for current state
- Session Lab for one-session inspection
- Memory Graph for cumulative memory inspection

This rounds out the first usable backend surface set for `Hero Performance OS`.

# DECISIONS MADE

- Used memory-item snapshots rather than attempting a full historical chart system too early.
- Bucketed by both status and memory type so the payload is useful before any UI-specific formatting exists.
- Kept the payload inspection-oriented rather than presentation-polished.

# RISKS / OPEN QUESTIONS

- This is not yet a true time-series graph payload; it is a cumulative graph/read model foundation.
- Later we may want dedicated memory transition snapshots to show status changes over time.
- Ranking within each bucket currently inherits repository ordering.

# OUT OF SCOPE

- graph UI
- true time-series chart endpoints
- Review / Brain APIs
- operator writeback

# TEST / VALIDATION

- Python syntax validation should be run for the new Memory Graph files.
- No live database read was executed in this task.

# RECOMMENDED NEXT STEP

The next strong move is to choose between:

1. adding simple executable smoke tests for the V2 ingest -> evidence -> memory -> surface chain
2. beginning the first thin UI shell over Command Center, Session Lab, and Memory Graph

If trust is the priority, smoke tests should come first.
