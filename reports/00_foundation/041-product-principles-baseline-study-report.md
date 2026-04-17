# TASK

Inject product principles that frame AOF, `13x13`, and EV/result analysis as baseline-building tools for later GTO study.

# WHAT I CHANGED

- Added [docs/product_principles.md](/Users/chrisyoon/GitHub/hero-performance-os/docs/product_principles.md)
- Updated [PROJECT_MASTER_CONTEXT.md](/Users/chrisyoon/GitHub/hero-performance-os/PROJECT_MASTER_CONTEXT.md) to state that the product is not testing GTO memorization and should build Hero's personal baseline first.
- Updated [AGENTS.md](/Users/chrisyoon/GitHub/hero-performance-os/AGENTS.md) so future implementation work treats AOF and `13x13` analysis as first-class MVP baseline-building tools.
- Updated [DECISIONS_LOG.md](/Users/chrisyoon/GitHub/hero-performance-os/DECISIONS_LOG.md) to fix the product decision that repeated pattern plus real result matters more than isolated solver-style hand judgment.
- Updated [WORKFLOW.md](/Users/chrisyoon/GitHub/hero-performance-os/WORKFLOW.md) so the workflow explicitly supports baseline-building before later GTO study.

# ARCHITECTURE IMPACT

- No code or schema changes.
- This clarifies why upcoming strategic surfaces should exist.
- It reduces the risk of building the product as a generic chart grader or solver mirror.

# DECISIONS MADE

- The product is not a GTO memorization test.
- AOF analysis is a baseline-building layer.
- `13x13` hand-class/result analysis is a baseline-building layer.
- EV / actual-result analysis should validate repeated pattern beliefs over time.
- The product should help Hero get more value from later GTO Wizard study rather than trying to replace it.

# RISKS / OPEN QUESTIONS

- These principles still need to be reflected in future active-task priorities and implementation order as work continues.
- Exact EV support is still partial, so some language will still need proxy framing until deeper data layers exist.

# OUT OF SCOPE

- No code implementation
- No parser changes
- No storage changes
- No strategic scoring changes in this task

# TEST / VALIDATION

- No tests run because this task only updated documentation and product principles.
- Validated by reading updated core context docs after patching.

# RECOMMENDED NEXT STEP

Use these product principles to drive the next implementation order:

- AOF baseline analysis
- `13x13` hand-class/result analysis
- then belief/result interpretation layers on top

# HANDOFF

- Product-principle source of truth now exists in [docs/product_principles.md](/Users/chrisyoon/GitHub/hero-performance-os/docs/product_principles.md).
- Core repo context docs now state that AOF and `13x13` analysis are baseline-building tools for later GTO study.
- Future implementation should avoid drifting back into generic solver-style grading.
