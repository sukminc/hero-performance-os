# TASK

Tighten Today usefulness so V2 turns stronger memory into clearer, more believable pre-session action guidance.

# WHAT I CHANGED

- Updated [core/surfaces/today.py](/Users/chrisyoon/GitHub/hero-performance-os/core/surfaces/today.py) to:
  - produce more situation-aware headlines instead of generic state text
  - translate memory items into clearer action labels such as `Re-anchor blind discipline`
  - generate more specific reasons tied to maturity and evidence count
  - keep Today narrow by capping surfaced adjustments at two
  - avoid turning baseline negative items or watch-stage noise into direct action bullets
  - add `primary_focus` to the confidence summary so the top pre-session emphasis is explicit
- Expanded [tests/v2_smoke_tests.py](/Users/chrisyoon/GitHub/hero-performance-os/tests/v2_smoke_tests.py) to verify:
  - early thin-memory Today defaults to a simple focus
  - repeated active drift is translated into a clearer action label
  - Today state and headline reflect the mixed baseline-plus-one-risk scenario more credibly
  - Today remains focused instead of surfacing too many actions

# ARCHITECTURE IMPACT

This keeps the existing surface architecture intact while making Today behave more like a pre-session action surface and less like a thin memory listing.

- Memory remains the canonical driver.
- Today now compresses memory into fewer, clearer operator-facing actions.
- Snapshot confidence summaries carry a directly usable `primary_focus` field.

# DECISIONS MADE

- Today should surface fewer actions, not more.
- Headlines should identify the main issue or baseline explicitly when evidence supports it.
- Action labels should be translated into pre-session language rather than raw memory type names.
- Watch-stage memory should inform context, but not dominate the action surface.

# RISKS / OPEN QUESTIONS

- Today wording is still rule-based and may need a more nuanced phrasing layer later.
- Ranking remains mostly memory-driven; future work may want stronger weighting for recency or intervention history.
- The current output is better compressed, but still depends on the quality of upstream memory phrasing.

# OUT OF SCOPE

- parser changes
- evidence changes
- memory-state rewrites
- Session Lab / Memory Graph refinement
- Review / Brain work
- UI redesign

# TEST / VALIDATION

- Ran `python3 tests/v2_smoke_tests.py`
- Result: `V2 smoke tests passed.`
- Verified early thin-memory Today stays simple
- Verified repeated active drift turns into a specific top action
- Verified Today remains limited to a small number of adjustments

# RECOMMENDED NEXT STEP

Move to Session Lab and Memory Graph usefulness:

- make evidence and memory deltas easier to inspect
- improve grouping and trend readability
- reduce raw operator noise without hiding backend truth
