# TASK

Improve evidence quality so V2 turns parsed session packets into more believable session interpretation, cumulative memory updates, and Today direction.

# WHAT I CHANGED

- Added [core/evidence/evidence_utils.py](/Users/chrisyoon/GitHub/hero-performance-os/core/evidence/evidence_utils.py) to centralize lightweight evidence helpers for:
  - basic hand outcome interpretation
  - positive execution cue detection
- Tightened [core/evidence/stable_strength_evidence.py](/Users/chrisyoon/GitHub/hero-performance-os/core/evidence/stable_strength_evidence.py):
  - repeated named patterns now require actual repetition instead of a single mention
  - added a stronger positive execution signal for reset / breathing / chip-preservation discipline
  - kept a broader survival-discipline fallback, but with more grounded wording
- Tightened [core/evidence/hand_class_evidence.py](/Users/chrisyoon/GitHub/hero-performance-os/core/evidence/hand_class_evidence.py):
  - generalized beyond a single hardcoded hand class
  - moved to clearer win/loss thresholds before calling out underperformance or stable strength
- Tightened small-sample noise in:
  - [core/evidence/style_drift_evidence.py](/Users/chrisyoon/GitHub/hero-performance-os/core/evidence/style_drift_evidence.py)
  - [core/evidence/field_distortion_evidence.py](/Users/chrisyoon/GitHub/hero-performance-os/core/evidence/field_distortion_evidence.py)
  - [core/evidence/contamination_evidence.py](/Users/chrisyoon/GitHub/hero-performance-os/core/evidence/contamination_evidence.py)
- Expanded [tests/v2_smoke_tests.py](/Users/chrisyoon/GitHub/hero-performance-os/tests/v2_smoke_tests.py) so the small sample fixture now verifies:
  - positive execution discipline evidence is emitted
  - tiny-sample contamination evidence is not emitted
  - tiny-sample field-distortion evidence is not emitted

# ARCHITECTURE IMPACT

This keeps the existing ingest -> evidence -> memory -> surfaces architecture intact while making the evidence layer more conservative and more believable.

- Small samples now produce fewer exaggerated style / field / contamination claims.
- Positive execution memory has a clearer path into the system, which better matches the product rule that strengths are first-class memory.
- Downstream memory and Today layers receive evidence that is less noisy and more operator-trustworthy.

# DECISIONS MADE

- Evidence should be quieter on tiny samples unless a signal is directly visible and meaningful.
- A single named pattern is not enough to claim stable strength by itself.
- Positive execution cues such as reset, breathing, and chip preservation are valid first-class evidence when they recur across a session.
- Field / contamination / drift signals should require more sample support before they influence memory.

# RISKS / OPEN QUESTIONS

- Keyword-based positive execution detection is still a transition heuristic and may need refinement once more real sessions arrive.
- The evidence layer is still session-local; it does not yet compare session behavior against a richer personal baseline.
- More real fixtures are still needed to pressure-test where conservative thresholds should sit.

# OUT OF SCOPE

- memory ranking/state transitions
- Today scoring/ranking logic
- Review / Brain work
- parser rewrites
- UI work

# TEST / VALIDATION

- Ran `python3 tests/v2_smoke_tests.py`
- Result: `V2 smoke tests passed.`
- Verified the sample fixture now yields positive execution evidence without also generating noisy tiny-sample field/contamination claims
- Verified ingest -> evidence -> memory -> Today chain still passes end to end

# RECOMMENDED NEXT STEP

Move to memory ranking and state logic:

- tighten memory promotion rules
- better distinguish watch vs active vs baseline
- improve repeated-vs-one-off weighting so Today ranks the right adjustments first
