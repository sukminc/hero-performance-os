# V2 Migration Plan

## Rule

Use V1 as a reference implementation.
Do not grow V1 as the active architecture.

## Migration phases

### Phase 0. Freeze V1
- mark V1/V2 transition in root docs
- stop adding new feature work to legacy V1 folders

### Phase 1. Create V2 skeleton
- create `core/`, `operator_app/`, `app/`, and `docs/v2/`
- document responsibilities before moving logic

### Phase 2. Rebuild storage boundary
- define V2 schema
- define repositories and DB contract

### Phase 3. Rebuild ingest/parsing
- migrate duplicate-safe ingestion
- migrate parse quality
- migrate session/hand normalization

### Phase 4. Rebuild evidence layer
- hand class underperformance
- style drift
- stable strength
- field distortion
- contamination risk

### Phase 5. Rebuild cumulative memory
- evidence -> memory update
- active/watch/baseline/resolved lifecycle

### Phase 6. Rebuild metrics and field snapshots
- style snapshots
- field snapshots
- baseline windows

### Phase 7. Rebuild Today
- current state
- top adjustments
- evidence-aware support

### Phase 8. Rebuild Session Lab
- upload
- parse quality
- evidence inspection
- memory preview

### Phase 9. Rebuild Command Center and Memory Graph
- current state
- trend tracking
- field/contamination view

### Phase 10. Rebuild Review / Brain / operator correction
- review queue
- rule authoring
- correction overlays

### Phase 11. Reconnect QA
- fixtures
- approved truth
- regression gates

### Phase 12. Archive V1 history cleanly
- mark or move legacy folders once V2 equivalents are live

## First implementation packet

The first active build packet should cover:

1. V2 skeleton
2. storage/schema boundary
3. ingest/parsing rebuild

Nothing else should expand until that packet lands cleanly.
