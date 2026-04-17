# TASK

Prototype an integrated review operator surface that combines repeated spots, HUD trend, and field ecology into one review workflow.

# WHAT I CHANGED

- added a new read-only API at `app/api/review_operator.py`
- added a new `Review Operator` tab to the local operator shell
- combined:
  - hand-matrix study families
  - HUD trend context
  - field ecology context
  into unified review cards
- each review card now tries to answer:
  - what happened
  - what the environment looked like
  - what current style trend says
  - what should be fixed next

# ARCHITECTURE IMPACT

- this is an orchestration read layer on top of existing operator APIs
- it does not create new canonical storage
- it establishes the product direction for integrated post-hoc review without requiring new ingestion architecture first

# DECISIONS MADE

- kept the first version orchestration-only instead of building a new deep canonical aggregation layer
- prioritized readability and felt meaning over completeness
- used existing study, HUD, and ecology surfaces as inputs rather than duplicating extraction logic in the UI

# RISKS / OPEN QUESTIONS

- current integrated cards still use heuristic cross-surface synthesis
- future versions should attach exact evidence counts and stronger tournament linking
- some cards still describe family-level context rather than exact one-spot causality

# OUT OF SCOPE

- final coaching copy
- exact solver-grounded adjustment text
- persistent intervention tracking loop for each card

# TEST / VALIDATION

- integrated route added to local server
- payload shape built from existing operator APIs
- UI tab added for browser-based inspection

# RECOMMENDED NEXT STEP

Make the integrated review cards sortable by priority and add direct jump links into AOF, 13x13, HUD Trend, and Field Ecology slices for the same family.
