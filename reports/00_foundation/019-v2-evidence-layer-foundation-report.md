# TASK

Implement the first V2 evidence layer so parsed sessions can emit structured `session_evidence` instead of stopping at stored hands.

# WHAT I CHANGED

- Added V2 evidence modules:
  - `core/evidence/evidence_models.py`
  - `core/evidence/hand_class_evidence.py`
  - `core/evidence/style_drift_evidence.py`
  - `core/evidence/stable_strength_evidence.py`
  - `core/evidence/field_distortion_evidence.py`
  - `core/evidence/contamination_evidence.py`
  - `core/evidence/session_evidence_pipeline.py`
- Added `SessionEvidenceRecord` to `core/storage/models.py`
- Added `create_session_evidence(...)` to `core/storage/repositories.py`
- Wired evidence generation + persistence into `core/ingest/file_ingest.py`
- Extended ingest result output to report `evidence_count`

The V2 path now supports:

`file -> parse -> hands -> evidence candidates -> session_evidence rows`

# ARCHITECTURE IMPACT

V2 now has the first true middle layer between parsing and cumulative memory.
This is important because future memory and surface logic can now operate on:

- structured evidence
- explicit evidence type
- entity scope
- confidence
- source hand references

instead of trying to interpret raw hands directly each time.

# DECISIONS MADE

- Started with five evidence families only:
  - hand class underperformance
  - style drift
  - stable strength
  - field distortion
  - contamination risk
- Kept the heuristics conservative and inspectable rather than pretending to be solver-exact.
- Wired evidence generation into the ingest path now so every successful V2 ingest can leave inspectable middle-layer artifacts.

# RISKS / OPEN QUESTIONS

- The first heuristics are intentionally rough and should be treated as candidate-generation logic.
- `99` underperformance is included as a direct first-pass example, but broader hand-class expectation logic still needs a better baseline layer.
- Contamination and field-distortion logic currently relies on limited parsing features and will improve as parsing gets richer.

# OUT OF SCOPE

- cumulative memory updates
- Today / Review / Brain generation
- operator review of evidence
- baseline-window comparison against historical snapshots

# TEST / VALIDATION

- Python syntax validation should be run across the new evidence and updated ingest/storage files.
- No database runtime test was executed in this task.

# RECOMMENDED NEXT STEP

Implement the V2 memory layer next:

1. read `session_evidence`
2. upsert `memory_items`
3. define `watch / active / baseline / resolved` behavior
4. prepare the first Today surface to consume memory instead of raw evidence
