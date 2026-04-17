# TASK

Document the large-step path from the current V2 state to MVP, define the independent-repo cutover path, and leave re-entry docs so future sessions can quickly understand the system.

# WHAT I CHANGED

- Updated `docs/v2/README.md` to include the new high-priority docs
- Added:
  - `docs/v2/reentry_start_here.md`
  - `docs/v2/mvp_big_steps.md`
  - `docs/v2/independent_repo_cutover.md`

These docs now define:

- what V2 is
- what V1 is
- what V2 already has
- how to resume work quickly later
- the big-step path to MVP
- the cutover path to a standalone V2 repo

# ARCHITECTURE IMPACT

This change does not alter runtime code, but it materially improves continuity and execution quality.
V2 is now documented as:

- an independent logical product
- a staged MVP build
- a future standalone repo

This lowers restart friction and reduces dependence on chat memory.

# DECISIONS MADE

- V2 should be treated as logically independent now, even before the physical repo split.
- The MVP path should be described in large product steps, not only implementation micro-phases.
- Re-entry documentation should explicitly tell a future reader what to read first and what is already built.
- Independent repo cutover should move only active V2 assets first, not the whole historical tree.

# RISKS / OPEN QUESTIONS

- The physical repo split has not happened yet.
- The final standalone V2 repo will still need its own root README/AGENTS/current-state set.
- The thin UI shell decision remains the next major product/build branch point.

# OUT OF SCOPE

- actual repo split
- branch/repo creation
- moving files into a new git repository
- UI implementation

# TEST / VALIDATION

- Verified the new docs exist under `docs/v2/`
- Verified `docs/v2/README.md` now points at the new re-entry, MVP, and cutover docs

# RECOMMENDED NEXT STEP

Choose one of these two paths explicitly:

1. continue in this repo long enough to add the first thin UI shell, then cut V2 into its own repo
2. cut V2 into its own repo immediately and continue all future work there

Given the current state, the strongest path is usually:

- one more pass in this repo to add the thin UI shell
- then standalone V2 repo cutover
