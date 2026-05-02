# Task 86: Hero Baseline Hover Popover Readability

## TASK

Improve 13x13 matrix hover breakdown readability so action-depth data appears as a structured popover instead of a dense text blob.

## WHAT I CHANGED

- Added structured `hover_action_breakdown` rows to matrix cells.
- Updated `/operator` matrix hover UI to render a popover table with:
  - Action
  - Count
  - BB
  - Stack %
- Enlarged hover popover styling so it behaves like a separate inspection card.

## ARCHITECTURE IMPACT

No canonical truth changes. This improves the operator product surface for existing deterministic Hero Baseline metrics.

## DECISIONS MADE

- Keep compact values in the cell.
- Move action-depth detail into a hover inspection card.
- Keep the top five action entries per hand in hover to avoid overload.

## RISKS / OPEN QUESTIONS

- Hover is desktop-first. Mobile/touch needs click-to-open later.
- Very edge-positioned cells may still need viewport-aware placement later.

## OUT OF SCOPE

- No click-to-select behavior.
- No new metrics.
- No database changes.

## TEST / VALIDATION

Run Python compile, frontend typecheck, and build.

## RECOMMENDED NEXT STEP

Add click-to-select matrix cells so hover is quick inspection and click opens persistent detail for that hand.
