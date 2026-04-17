# V2 Re-entry Start Here

## What this is

`Hero Performance OS V2` is the active rebuild path for the personal poker performance system.

It is designed to make Hero stronger as:

- a semipro poker player,
- a data engineer,
- and an AI product engineer.

This is not a mass-market poker app effort.
This is a personal high-signal performance system first.

## What V1 is

V1 is the preserved reference implementation and historical learning base.

Use V1 for:

- proven ideas,
- operator workflow lessons,
- QA discipline,
- and selective migration.

Do not keep growing V1 as the active architecture.

## What V2 already has

V2 currently has working foundations for:

- storage/schema
- ingest/parsing
- evidence generation
- cumulative memory updates
- Today surface generation
- Today read/API packet
- Command Center aggregation packet
- Session Lab read/API packet
- Memory Graph read/API packet
- end-to-end smoke testing across the chain

## What the product is trying to answer

Every new feature should help answer one or more of these questions:

1. Which hand classes are underperforming relative to Hero baseline?
2. Where is Hero drifting?
3. Which stable strengths are regressing or holding?
4. What field distortions characterize the current pool?
5. Where is adaptation becoming contamination?
6. What should Hero carry into the next session?

## If you are coming back later

Read in this order:

1. [product_principles.md](/Users/chrisyoon/GitHub/opb-poker/docs/v2/product_principles.md)
2. [architecture.md](/Users/chrisyoon/GitHub/opb-poker/docs/v2/architecture.md)
3. [mvp_big_steps.md](/Users/chrisyoon/GitHub/opb-poker/docs/v2/mvp_big_steps.md)
4. [independent_repo_cutover.md](/Users/chrisyoon/GitHub/opb-poker/docs/v2/independent_repo_cutover.md)
5. [migration_plan.md](/Users/chrisyoon/GitHub/opb-poker/docs/v2/migration_plan.md)

Then inspect the current active implementation folders:

- `core/`
- `app/api/`
- `core/surfaces/`
- `tests/v2_smoke_tests.py`

## Current active build rule

When adding new work:

- prefer large, clean product steps over scattered micro-features
- document each meaningful step in `reports/00_foundation/` or the relevant report group
- keep V2 understandable without replaying the whole chat history

## Current recommendation

Treat V2 as if it is already its own product codebase logically, even before it is physically split into an independent repo.
