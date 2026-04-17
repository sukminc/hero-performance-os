# TASK

Improve memory ranking and state logic so V2 turns evidence into more believable cumulative Hero memory and better Today prioritization.

# WHAT I CHANGED

- Updated [core/memory/memory_status.py](/Users/chrisyoon/GitHub/hero-performance-os/core/memory/memory_status.py) so:
  - one-off positive evidence no longer promotes straight to `baseline`
  - negative evidence no longer becomes `active` too easily from a single session
  - repeated signals now matter more than isolated confidence spikes
- Updated [core/memory/memory_updater.py](/Users/chrisyoon/GitHub/hero-performance-os/core/memory/memory_updater.py) so:
  - memory summaries include an explicit maturity label
  - memory payload stores `maturity` as structured truth
  - suggested adjustments are only attached once a memory item reaches `active`
- Updated [core/surfaces/today.py](/Users/chrisyoon/GitHub/hero-performance-os/core/surfaces/today.py) so:
  - Today ranking now prefers mature repeated items over emerging ones
  - `watch` items no longer generate direct Today adjustments
  - contamination only flips the current state when it is truly `active`, not merely watch-stage noise
- Expanded [tests/v2_smoke_tests.py](/Users/chrisyoon/GitHub/hero-performance-os/tests/v2_smoke_tests.py) to verify:
  - one-off positive execution memory stays `watch`
  - repeated positive evidence promotes to `baseline`
  - repeated negative evidence promotes to `active`
  - Today surfaces mature active negative memory ahead of lower-maturity positive memory

# ARCHITECTURE IMPACT

This keeps the existing ingest -> evidence -> memory -> Today chain intact while making cumulative memory behave more like real product memory instead of a per-session echo.

- Repetition now matters more in memory state transitions.
- Today is less likely to overreact to emerging one-off observations.
- Memory payload now carries structured maturity truth that downstream surfaces can use.

# DECISIONS MADE

- Positive signals should earn `baseline` through repetition, not one appearance.
- Negative signals should generally earn `active` through repetition unless evidence is unusually strong.
- `watch` is a real staging state, not just a temporary label before everything becomes actionable.
- Today adjustments should come from mature actionable memory, not every new observation.

# RISKS / OPEN QUESTIONS

- Maturity is currently inferred from evidence count only; future work may want recency and session spacing.
- Today still uses fairly simple ranking logic even with the stronger maturity signal.
- Resolved-state behavior remains minimal and will likely need a more explicit operator or verification loop later.

# OUT OF SCOPE

- parser changes
- evidence generation changes
- Review / Brain work
- UI work
- operator correction loop

# TEST / VALIDATION

- Ran `python3 tests/v2_smoke_tests.py`
- Result: `V2 smoke tests passed.`
- Verified one-off positive memory stays `watch`
- Verified repeated positive memory becomes `baseline`
- Verified repeated negative memory becomes `active`
- Verified Today now surfaces mature active adjustments instead of watch-stage noise

# RECOMMENDED NEXT STEP

Move to Today usefulness:

- improve current-state computation
- improve adjustment ranking and language
- make Today feel more like one clear next action surface and less like a thin memory listing
