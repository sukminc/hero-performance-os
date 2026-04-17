# TASK

Write the first `13x13` hand-class / result analysis spec and explicitly account for online ante-driven structural negativity.

# WHAT I CHANGED

- Added [docs/thirteen_by_thirteen_analysis_spec_v1.md](/Users/chrisyoon/GitHub/hero-performance-os/docs/thirteen_by_thirteen_analysis_spec_v1.md)
- Defined the first `13x13` surface around:
  - normalized hand-class aggregation
  - position-aware analysis
  - actual `bb` result tracking
  - sample-aware interpretation
  - hand-class product cards
  - study-queue generation
- Explicitly documented that online tournaments use seat-by-seat antes, which means garbage hands such as `72o` may be structurally negative in raw `bb net` without implying strategic misuse.
- Defined the interpretation split between:
  - `structural_negative`
  - `usage concern`
  - `belief concern`

# ARCHITECTURE IMPACT

- No code or schema changes.
- This creates the first stable implementation contract for `13x13` analysis.
- It prevents future implementation from turning the matrix into a naive raw-profit heatmap.

# DECISIONS MADE

- `13x13` analysis is a baseline-building surface, not decorative analytics.
- Raw negative `bb net` is not enough to call a hand class a leak.
- Garbage hands in ante-heavy online structures must be interpreted with structural-cost awareness.
- Position split is mandatory because the same hand class can be acceptable in one seat and suspicious in another.
- The matrix must feed hand-class product cards and a study queue rather than stop at visualization.

# RISKS / OPEN QUESTIONS

- Exact EV support is still out of scope for v1.
- We still need to decide how `actual_bb_net` should account for forced costs in presentation language versus raw aggregation storage.
- Position completeness may remain imperfect in some historical hands.

# OUT OF SCOPE

- No code implementation
- No parser changes
- No storage changes
- No exact EV engine
- No UI implementation

# TEST / VALIDATION

- No tests run because this task only updated documentation and product specs.
- Validation was done by checking the current repo principles and aligning the new spec with the known online-ante constraint.

# RECOMMENDED NEXT STEP

Implement the first derived `13x13` aggregation layer with:

- hand class
- position
- hands played
- actual `bb net`
- average `bb` per hand
- sample band

Then add first-pass flags for:

- `structural_negative_only`
- `overused_and_losing`
- `position_distortion`
- `belief_hand`

# HANDOFF

- `13x13` source of truth now exists in [docs/thirteen_by_thirteen_analysis_spec_v1.md](/Users/chrisyoon/GitHub/hero-performance-os/docs/thirteen_by_thirteen_analysis_spec_v1.md).
- The key constraint is now explicit: garbage-hand negativity under online ante structures is not auto-leak evidence.
- Future implementation should interpret matrix cells, not just color them.
