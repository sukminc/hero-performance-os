# Next Up

## Immediate next phase

Phase 2: Upload Service Foundation

## Recommended first task packet

### Title

Build the first user-owned GG packet upload path for the public MVP shell.

### Objective

Enable authenticated users to upload GG session packets, see processing state, and safely reach the canonical ingest path.

### Scope

- upload UI on `/app/upload`
- upload endpoint or server action
- upload storage target choice
- duplicate guard integration
- processing job state
- latest upload status block

### Out of scope

- public Today / Review / Brain rendering
- billing

### Validation target

- authenticated user can submit a GG packet
- duplicate packets fail safely
- processing state is visible
- upload ownership is preserved

### Report destination

- `reports/00_foundation/053-upload-service-foundation-report.md`

## After that

1. public Today / Review / Brain surfaces
2. billing + entitlement
3. launch operations
