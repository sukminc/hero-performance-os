# Task 79: AOF Product Insight Cards

## TASK

Convert the AOF v2 leak candidate surface from raw developer-style dumps into readable product insight cards that tell Hero what matters, why it matters, what to change, and what not to over-correct.

## WHAT I CHANGED

- Added product summary generation to `core/surfaces/aof_decision_system.py`.
- Added priority scoring for AOF leak families so repeated high-severity spots are surfaced first.
- Added per-card product reads with title, severity, evidence line, why-it-matters, next adjustment, and over-correction guardrails.
- Updated `/operator` AOF Decision System v2 to lead with Lead Read, Next Adjustment, Cooler Guard, and Priority Leak Cards.
- Moved the full mistake-card JSON into expandable operator evidence.
- Added visual CSS for insight cards, leak cards, evidence chips, and operator details.
- Added `docs/aof_product_insight_cards.md`.

## ARCHITECTURE IMPACT

This preserves the existing deterministic AOF classifier and adds a product interpretation layer on top of it. It does not promote UI copy to canonical truth and does not replace the raw evidence layer.

The product surface now better matches the MVP rule that AOF analysis should help Hero build a personal short-stack baseline before later GTO study.

## DECISIONS MADE

- `Leak candidates` remains a summary metric, but the product should lead with priority cards.
- Priority is based on deterministic family severity multiplied by repeat count.
- Cooler protection is displayed as a first-class product guardrail so lost standard all-ins do not become fake leaks.
- Operator-defer remains visible because AOF quality still depends on position, opener, multiway geometry, bounty economics, and tournament format.

## RISKS / OPEN QUESTIONS

- The current priority score is intentionally simple and deterministic; it is not solver EV.
- Position/opener/stack-geometry context is still incomplete, so some cards must remain operator-review-needed.
- Copy is useful enough for operator mode but may need tighter consumer-facing language later.

## OUT OF SCOPE

- No new database schema.
- No solver chart ingestion.
- No live in-hand advice.
- No consumer-facing app redesign beyond the operator AOF surface.

## TEST / VALIDATION

Validation commands should confirm:

- Python syntax for the AOF surface.
- Frontend type/build integrity.

## RECOMMENDED NEXT STEP

Proceed with Task 80 / 81:

- Task 80: enrich AOF spots with position/opener/action-chain features.
- Task 81: add operator review controls to approve/reject specific AOF priority cards and preserve reviewed truth as overlays.
