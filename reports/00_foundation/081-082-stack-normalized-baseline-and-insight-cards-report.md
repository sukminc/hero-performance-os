# Task 81 / 82: Stack-Normalized Baseline + Insight Cards

## TASK

Add stack-normalized result metrics to the existing 13x13 Hero Baseline and surface product insight cards that compare raw BB against stack realization.

## WHAT I CHANGED

- Added `avg_stack_realization_pct` to hand-class scores and matrix cells.
- Added `full_stack_loss_count`, `full_stack_loss_rate`, `double_up_count`, and `double_up_rate`.
- Added stack-band realization summaries for short, mid, and deep stacks.
- Added `stack_realization_leaks` queue.
- Added `raw_vs_stack_mismatches` queue.
- Added `baseline_insight_cards` for selected-hand and normalized leak interpretation.
- Updated the `/operator` Hero Baseline section to show raw BB and stack % together.
- Updated 13x13 cells so the background still reflects raw BB while the bottom bar reflects stack-normalized tone.
- Added `docs/stack_normalized_hero_baseline.md`.

## ARCHITECTURE IMPACT

This extends the existing derived hand matrix without changing canonical storage.

It preserves raw BB result as a first-class metric, but makes it insufficient by itself. Hero Baseline can now compare absolute chip result against starting-stack percentage result before deciding whether a hand class is truly being misplayed.

## DECISIONS MADE

- Stack realization v1 is calculated as `bb_net / effective_stack_bb * 100`.
- Full-stack loss is flagged at `<= -80%` of starting stack.
- Double-up is flagged at `>= +80%` of starting stack.
- Raw BB cell tone remains visible, while stack % tone is shown as a separate bottom indicator.
- Stack normalization is explicitly labeled as better post-hoc result normalization, not solver EV.

## RISKS / OPEN QUESTIONS

- Stack realization can still be distorted by multiway all-ins, bounty incentives, ICM, and runout variance.
- The matrix still needs decision-node decomposition to explain why a hand like `66` is losing.
- The old hand-matrix code still lives under `app/api/hand_matrix.py`; future cleanup should move it into `core/surfaces`.

## OUT OF SCOPE

- No solver chart ingestion.
- No all-in adjusted EV.
- No ICM/PKO EV model.
- No operator approval overlay for Hero Baseline cards yet.

## TEST / VALIDATION

Validation should include:

- Python compile for `app/api/hand_matrix.py`.
- Direct payload read for selected hand `66`.
- Frontend typecheck.
- Frontend production build.

## RECOMMENDED NEXT STEP

Proceed with Task 83:

Decompose `66`, `77`, `88`, `QQ`, and `AQs` into decision-node cards by position, stack band, first preflop action, facing action, and format so the product can explain whether the issue is implementation, variance, or context.
