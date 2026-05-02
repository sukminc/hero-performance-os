# Tournament Result Truth

## Purpose

GG Poker hand-history packets and GG Poker tournament summary exports answer different business questions.

- Hand-history packets answer: what decisions and patterns appeared in the session?
- Tournament summaries answer: what was the official tournament outcome?

Both are useful, but they must not be collapsed into the same truth layer.

## Canonical Rule

Official GG tournament summary exports are persisted as `tournament_results`.

They are linked to hand-history sessions by:

- `player_id`
- `site`
- `tournament_id`

This lets the product detect high-weight outcomes such as final tables, big cashes, and satellite seat wins without pretending those results prove every decision was good.

## Interpretation Rule

A big cash is review context, not automatic strategic credit.

For example, a top-three bounty tournament cash should tell OPB:

- this session deserves high review priority,
- positive execution candidates should be inspected carefully,
- obvious run-good should be labeled separately,
- and only repeatable evidence should become durable Hero memory.

## Current MVP Behavior

Summary-only exports still do not create fake sessions or fake hands.

Instead, they:

- keep the ingest status as `skipped_summary_only`,
- persist official result context when `tournament_id` is available,
- allow duplicate summary uploads to repair missing result rows,
- and expose linked result context in Review / Brain surfaces.

## Out Of Scope

This does not yet calculate EV, bounty EV, ICM, or exact luck.

The current layer only preserves official result truth and deterministic high-weight result signals so operator review can separate run-good from repeatable execution.
