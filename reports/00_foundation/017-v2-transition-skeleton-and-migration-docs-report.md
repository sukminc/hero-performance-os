# TASK

Define the current repo as V1, create the V2 active skeleton, and document the migration path so future implementation work lands in the new architecture instead of expanding legacy folders.

# WHAT I CHANGED

- Created the V2 active skeleton folders:
  - `core/`
  - `operator_app/`
  - `app/`
  - `docs/v2/`
  - `archive_v1/`
  - `qa/gates/`
- Added V2 documentation:
  - `docs/v2/README.md`
  - `docs/v2/product_principles.md`
  - `docs/v2/architecture.md`
  - `docs/v2/module_map.md`
  - `docs/v2/migration_plan.md`
- Added folder-level README markers for the new active structure.
- Updated `README.md` to mark:
  - V1 as the existing reference implementation
  - V2 as the active rebuild path
  - the rule that new active work should target V2 folders
- Updated `docs/current_state/current_state.md` to reflect the transition and point to the V2 docs.

# ARCHITECTURE IMPACT

The repo now has an explicit boundary between:

- V1 reference/history
- V2 active implementation

This reduces future architecture drift by making it clear where new work belongs.
It also sets up the next implementation packet to focus on `core/storage` and `core/ingest` rather than growing legacy surfaces.

# DECISIONS MADE

- V1 is preserved, not discarded.
- V2 is the active build path for `Hero Performance OS`.
- New active code should move into `core/`, `operator_app/`, `app/`, and `docs/v2/`.
- Legacy folders remain available as migration/reference sources until their V2 equivalents exist.

# RISKS / OPEN QUESTIONS

- The exact V2 schema is still to be defined.
- Some V1 modules may end up partially salvaged instead of fully rewritten.
- The exact point when each V1 folder should physically move into `archive_v1/` remains implementation-dependent.

# OUT OF SCOPE

- No logic migration yet
- No schema rewrite yet
- No API implementation yet
- No UI implementation yet
- No physical archival move of V1 folders yet

# TEST / VALIDATION

- Verified the new folders were created successfully.
- Verified the new V2 docs and updated root/current-state docs were written.
- No runtime tests were needed because this task only establishes structure and documentation.

# RECOMMENDED NEXT STEP

Execute the first V2 implementation packet:

1. define the V2 storage/schema boundary
2. rebuild ingest/parsing in `core/`
3. wire the first V2 persistence path before any new surface work
