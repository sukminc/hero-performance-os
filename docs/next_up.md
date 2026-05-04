# Next Up

## Immediate next phase

Phase 6: Hero-first private beta hardening through operator-trust loops.

## Current checkpoint

Finish cleanup after the interrupted Claude run, then review the remaining implementation changes as a coherent batch.

## Recommended next implementation packet

### Title

Production architecture decision for external beta.

### Objective

Decide how the frontend should read/write canonical poker truth before any real external beta user is added.

### Why this is next

`STATUS.md` now correctly calls out a deployment blocker: many frontend pages render by spawning `python3` and reading local SQLite. This is acceptable for local Hero/operator work, but not for Vercel/serverless or concurrent external users.

### Scope

- audit current frontend -> Python read paths
- choose one production path:
  - local-only Hero tool for now
  - FastAPI sidecar service
  - move canonical truth reads to Postgres / Node-side queries
- document the decision
- define the first implementation step

### Out of scope

- broad UI polish
- billing checkout
- solver/GTO exactness
- live in-hand advice
- rewriting all surfaces before the architecture decision

### Validation target

- decision is documented in `DECISIONS_LOG.md` and/or `DECISIONS.md`
- next implementation task has a narrow task packet and report destination

### Report destination

- `reports/00_foundation/096-production-architecture-decision-report.md`

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
