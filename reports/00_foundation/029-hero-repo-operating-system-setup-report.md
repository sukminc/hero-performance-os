# TASK

Set up a durable operating system inside the standalone `hero-performance-os` repo so future sessions can resume work quickly, follow one active task at a time, and continue toward MVP without relying on chat memory.

# WHAT I CHANGED

- Added:
  - `docs/master_plan.md`
  - `docs/active_task.md`
  - `docs/next_up.md`
- Updated:
  - `docs/current_state.md`
  - `docs/runbook.md`
  - `docs/README.md`

The new docs now define:

- the full big-step MVP plan
- the one current active task
- the next task after the active task
- the resume order for future sessions
- the handoff/update rules after meaningful work

# ARCHITECTURE IMPACT

No runtime code changed in this task.
The impact is execution quality and continuity:

- future sessions now have a clear place to start
- the repo carries its own plan
- the repo carries its own active lane
- handoff expectations are explicit

# DECISIONS MADE

- Only one active task should be in progress at a time.
- The current active task is parsing quality improvement.
- The next task after parsing quality is evidence quality improvement.
- The repo should remain understandable without replaying conversation history.

# RISKS / OPEN QUESTIONS

- The docs now define the operating system, but continued discipline is required to keep them current.
- If active work diverges from the current parsing task later, `docs/active_task.md` and `docs/next_up.md` must be updated immediately.

# OUT OF SCOPE

- actual parsing improvements
- actual evidence improvements
- UI changes
- repo split mechanics

# TEST / VALIDATION

- Verified the planning docs were added to the standalone repo
- Verified `docs/README.md` now points at the planning docs

# RECOMMENDED NEXT STEP

Begin the active task defined in `docs/active_task.md`:

- improve real GG parsing quality
- tighten parse quality reporting
- keep smoke coverage green while doing it
