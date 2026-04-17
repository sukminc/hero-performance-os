# TASK

Refocus interpretation around repeated pattern tracking and correction progress.

# WHAT I CHANGED

- Added [core/surfaces/pattern_progress.py](/Users/chrisyoon/GitHub/hero-performance-os/core/surfaces/pattern_progress.py) to turn cumulative memory into operator-readable pattern cards.
- Wired `pattern_progress` into [core/surfaces/command_center.py](/Users/chrisyoon/GitHub/hero-performance-os/core/surfaces/command_center.py) and [core/surfaces/memory_graph.py](/Users/chrisyoon/GitHub/hero-performance-os/core/surfaces/memory_graph.py).
- Each pattern card now exposes:
  - pattern label
  - pattern family (`strength`, `leak_or_risk`, `field_or_context`)
  - whether it appeared in the latest session
  - a progress verdict such as `holding`, `still_repeating`, `improving_window`, `watching`, or `context_live`
  - a short reason explaining that verdict
- Updated [tests/v2_smoke_tests.py](/Users/chrisyoon/GitHub/hero-performance-os/tests/v2_smoke_tests.py) so the smoke path asserts that repeated pattern progress is surfaced once memory matures.
- Rewrote [docs/active_task.md](/Users/chrisyoon/GitHub/hero-performance-os/docs/active_task.md), [docs/current_state.md](/Users/chrisyoon/GitHub/hero-performance-os/docs/current_state.md), and [docs/next_up.md](/Users/chrisyoon/GitHub/hero-performance-os/docs/next_up.md) to match the clarified product direction.
- Corrected the stale canonical corpus session count in `docs/current_state.md` from `268` to `368`.

# ARCHITECTURE IMPACT

- This does not change canonical truth or storage schema.
- It adds a deterministic read-model layer on top of existing cumulative memory.
- The product emphasis shifts from “review overlays first” to “pattern loop first” without deleting reviewed overlay support.
- The new surface is compatible with the intended loop:
  - recommendation
  - application
  - verification
  - model update

# DECISIONS MADE

- Repeated pattern visibility is now the primary product need, not overlay mechanics.
- Progress verdicts are inferred deterministically from:
  - memory direction
  - memory status
  - maturity
  - evidence count
  - whether the pattern reappeared in the latest session
- Positive patterns and negative patterns are treated differently:
  - positive patterns can read as `holding`
  - negative patterns can read as `still_repeating` or `improving_window`
- Field/context patterns remain visible but are not framed as direct correction progress.

# RISKS / OPEN QUESTIONS

- The current evidence taxonomy is still coarse. It can say things like `blind-structure absorption` or `multiway pressure`, but it does not yet map enough poker-specific corrections such as:
  - avoiding overbet hesitation
  - BB defend under-frequency
  - missed large c-bet opportunities
- Because of that, the new progress layer is structurally correct but not yet semantically rich enough for all of Hero's real questions.
- Latest-session progress currently depends on existing session-linked memory updates. If we want stronger “fixed vs not fixed” judgment, we will likely need more explicit intervention tags or recommendation-family mapping.

# OUT OF SCOPE

- No migration or replay architecture changes
- No schema change
- No new operator write path
- No UI redesign
- No broad reviewed-overlay expansion

# TEST / VALIDATION

- Ran `python3 tests/v2_smoke_tests.py`
  - result: passed
- Ran live canonical reads against `/Users/chrisyoon/GitHub/opb-poker/data/hero-v2/hero_v2.sqlite3`
  - `app/api/command_center.py`
  - `app/api/memory_graph.py`
- Confirmed live payloads now expose `pattern_progress`
- Confirmed canonical SQLite counts:
  - sessions: `368`
  - hands: `18442`
  - session_evidence: `1039`
  - memory_items: `34`

# RECOMMENDED NEXT STEP

Map more concrete poker corrections into deterministic pattern families so Hero can track questions in the form he actually cares about, for example:

- overbet reluctance
- BB defend discipline
- large c-bet opportunity usage
- pressure follow-through

That is the step that will turn the current pattern-progress shell into a real poker correction tracker.

# HANDOFF

- Canonical SQLite remains `/Users/chrisyoon/GitHub/opb-poker/data/hero-v2/hero_v2.sqlite3`
- New read-model entry point is `pattern_progress` inside:
  - `command_center`
  - `memory_graph`
- Current live read on canonical corpus still says the top repeated leak/risk is `blind-structure absorption`, which may still be too abstract for Hero's needs.
- The next useful implementation is not more overlay infrastructure. It is deeper poker-specific pattern extraction so corrections like “I am still under-defending BB” can be tracked directly.
