# V2 Architecture

## Rebuild intent

V2 keeps the strongest V1 ideas while narrowing the active implementation center.

The V2 core loop is:

`upload -> parse -> evidence -> memory update -> surfaces -> operator correction -> QA`

## Active folders

- `core/`
  Canonical product logic. No UI assumptions.
- `operator_app/`
  Hero-facing operator workbench surfaces.
- `app/`
  Web/API shell for the active V2 product.
- `qa/`
  Deterministic fixtures, truth assets, and gates.
- `data/`
  Working artifacts across raw, normalized, derived, runtime, and session layers.
- `docs/v2/`
  Active V2 product and architecture docs.

## Core domain split

### `core/ingest`
- file intake
- duplicate detection
- ingest orchestration

### `core/parsing`
- GG session parsing
- session building
- hand normalization
- parse quality evaluation

### `core/evidence`
- hand-class evidence
- style drift evidence
- stable strength evidence
- field distortion evidence
- contamination evidence

### `core/memory`
- cumulative memory updates
- memory status transitions
- Hero baseline maintenance

### `core/metrics`
- baseline windows
- hand-class metrics
- style snapshots

### `core/field`
- pool texture
- field snapshots
- chaos/softness metrics

### `core/interventions`
- recommendation generation
- verification/update loop

### `core/surfaces`
- Today
- Review
- Brain

### `core/storage`
- schema
- repositories
- database integration

## Operator-facing screens

V2 aims to center on three core screens:

1. Command Center
2. Session Lab
3. Memory Graph

Review and rules remain active support surfaces around those three.

## V1 boundary

V1 remains the reference base for:

- ingestion safeguards
- QA discipline
- operator review patterns
- existing truth and memory experiments

New active implementation should not expand legacy V1 folders unless the work is a V1-specific bug fix.
