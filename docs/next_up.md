# Next Up

## Immediate next phase

Phase 6: Hero-first private beta hardening through operator-trust loops.

## Current checkpoint

Cleanup after the interrupted Claude run is complete enough to proceed. The production architecture decision is now made: external beta requires managed Postgres plus a Python backend service boundary; local SQLite plus direct Python subprocess remains dev/Hero-local only.

## Recommended next implementation packet

### Title

Backend service boundary skeleton for external beta.

### Objective

Create the first narrow backend service/API boundary that lets Next.js stop spawning Python directly for one vertical slice.

### Why this is next

The production architecture decision has been made, but the app still renders by spawning `python3` and reading local SQLite. The next step is to prove the new boundary with one high-value read path before migrating every surface.

### Scope

- add a small Python HTTP service entrypoint for one surface family, preferably Today or operator Matrix
- read through `V2Repository` with `V2_STORAGE_BACKEND=postgres` support preserved
- add a Next.js client/server helper that can call the service when configured and fall back to local subprocess only in dev
- keep auth/player access checks explicit at the boundary
- document how to run the service locally

### Out of scope

- broad UI polish
- billing checkout
- solver/GTO exactness
- live in-hand advice
- migrating every surface in one pass
- rewriting derived poker interpretation logic in Node

### Validation target

- existing backend smoke tests still pass
- the selected frontend surface still renders locally
- service endpoint returns the same payload shape as the existing Python function for the selected slice

### Report destination

- `reports/00_foundation/097-backend-service-boundary-skeleton-report.md`

## Other candidate next tasks

1. Matrix operator approve/reject overlays for correction and hidden-value candidates.
2. AOF position inference and operator-approved baseline tables.
3. Remove any remaining raw JSON dumps from operator surfaces.
4. First real Supabase project E2E test: signup -> demo apply -> operator approve -> provision -> upload -> Today renders.

## Do not do next

- Do not start broad consumer-facing polish before production truth architecture is decided.
- Do not promote unreviewed Matrix or AOF candidates into durable memory.
- Do not collapse GG session uploads into stateless hand review.
- Do not treat `run_good`, `cooler`, or `unclear` Big Win tags as promotable memory.
