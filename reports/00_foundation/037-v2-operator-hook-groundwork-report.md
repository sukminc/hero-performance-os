# TASK

Prepare operator correction and truth-shaping hooks on top of the fully replayed canonical SQLite corpus.

# WHAT I CHANGED

- Added [core/surfaces/review_hooks.py](/Users/chrisyoon/GitHub/hero-performance-os/core/surfaces/review_hooks.py) to define explicit review-hook packets that separate canonical truth from future reviewed overlays.
- Updated [core/surfaces/command_center.py](/Users/chrisyoon/GitHub/hero-performance-os/core/surfaces/command_center.py) to expose player-level review hooks for:
  - Today emphasis
  - Command Center interpretation emphasis
- Updated [core/surfaces/session_lab.py](/Users/chrisyoon/GitHub/hero-performance-os/core/surfaces/session_lab.py) to expose session-level review hooks for:
  - session evidence assessment
  - memory update assessment
  - session surface emphasis
- Updated [core/surfaces/memory_graph.py](/Users/chrisyoon/GitHub/hero-performance-os/core/surfaces/memory_graph.py) to expose review hooks for:
  - cumulative memory assessment
  - interpretation emphasis assessment
- Added `OperatorReviewRecord` to [core/storage/models.py](/Users/chrisyoon/GitHub/hero-performance-os/core/storage/models.py).
- Added `operator_reviews` storage support to:
  - [core/storage/schema.sql](/Users/chrisyoon/GitHub/hero-performance-os/core/storage/schema.sql)
  - [core/storage/sqlite_repository.py](/Users/chrisyoon/GitHub/hero-performance-os/core/storage/sqlite_repository.py)
  - [core/storage/postgres_repository.py](/Users/chrisyoon/GitHub/hero-performance-os/core/storage/postgres_repository.py)
- Hardened SQLite schema initialization so canonical read-only corpus files can still be read safely without failing in `ensure_schema()`.
- Expanded [tests/v2_smoke_tests.py](/Users/chrisyoon/GitHub/hero-performance-os/tests/v2_smoke_tests.py) so review hooks and canonical-truth separation are now part of regression coverage.

# ARCHITECTURE IMPACT

This does not implement reviewed overlays yet. It defines where they will attach.

- Canonical evidence, memory, and surfaces remain immutable source truth.
- Future operator-reviewed overlays now have explicit attachment points instead of vague later-stage hook ideas.
- Canonical SQLite read paths remain usable even when the DB file is read-only.

# DECISIONS MADE

- Review hooks should exist at both session scope and player/cumulative scope.
- Reviewed overlays must be stored separately from canonical truth.
- Hook packets should make the separation explicit through `canonical_truth_policy`.
- Read-only canonical SQLite files are valid truth sources and should not fail just because schema writes are unavailable.

# RISKS / OPEN QUESTIONS

- Review hooks are explicit now, but no reviewed overlay write/read path is implemented yet.
- The first actual reviewed overlay design still needs to choose whether to start at evidence, memory, or interpretation-emphasis level.
- Existing canonical SQLite files will only receive the new `operator_reviews` table when writable; read-only use is safe, but overlay persistence will require a writable canonical or sidecar DB strategy.

# OUT OF SCOPE

- full operator correction implementation
- UI for review actions
- migration/replay redesign
- evidence or memory algorithm rewrites

# TEST / VALIDATION

- Ran `python3 tests/v2_smoke_tests.py`
- Result: `V2 smoke tests passed.`
- Ran Command Center against canonical SQLite:
  - `env PYTHONPATH=. SQLITE_DB_PATH=/Users/chrisyoon/GitHub/opb-poker/data/hero-v2/hero_v2.sqlite3 V2_STORAGE_BACKEND=sqlite python3 app/api/command_center.py`
- Ran Session Lab against canonical SQLite:
  - `env PYTHONPATH=. SQLITE_DB_PATH=/Users/chrisyoon/GitHub/opb-poker/data/hero-v2/hero_v2.sqlite3 V2_STORAGE_BACKEND=sqlite python3 app/api/session_lab.py`
- Verified:
  - review hooks now surface in Command Center, Session Lab, and Memory Graph
  - canonical truth separation is explicit in hook payloads
  - read-only canonical SQLite no longer crashes surface reads during schema initialization

# RECOMMENDED NEXT STEP

Build the first operator-reviewed overlays on top of canonical truth:

- choose the first reviewable layer
- likely start with interpretation emphasis or session evidence
- keep overlay storage separate from canonical truth and preserve replay assumptions
