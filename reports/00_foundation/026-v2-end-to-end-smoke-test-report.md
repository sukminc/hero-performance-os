# TASK

Add a V2 smoke test that exercises the full chain from ingest through evidence, memory, and read surfaces.

# WHAT I CHANGED

- Added `tests/v2_smoke_tests.py`
- Extended `core/parsing/gg_parser.py` with a lightweight fallback parser for the existing simplified GG session fixture format
- Extended `core/evidence/stable_strength_evidence.py` so simple-format fixtures can still produce inspectable positive execution evidence

The smoke test now covers:

1. ingesting a non-empty fixture
2. generating evidence
3. generating cumulative memory
4. generating Today
5. reading Command Center
6. reading Session Lab
7. reading Memory Graph
8. duplicate-safe ingest behavior
9. zero-hand safe failure behavior

# ARCHITECTURE IMPACT

V2 now has its first executable trust loop.
This is important because the rebuild is no longer validated only by structure and syntax; it now has a fixture-driven end-to-end smoke path.

# DECISIONS MADE

- Used an in-memory repository double instead of requiring live Postgres for the first smoke test.
- Kept the smoke test focused on chain integrity rather than exact scoring semantics.
- Supported both raw-style and simplified session fixture formats at the parser level so the existing fixture corpus remains useful during transition.

# RISKS / OPEN QUESTIONS

- This is a smoke test, not a full truth regression suite.
- The fallback parser exists to keep transition momentum, but later we may want to split simplified fixture parsing from real GG parsing more explicitly.
- Real Postgres-backed integration tests are still needed once the V2 schema stabilizes further.

# OUT OF SCOPE

- live Postgres integration test
- HTTP/web transport testing
- exact semantic validation of every evidence heuristic

# TEST / VALIDATION

Executed:

```bash
python3 -m py_compile core/evidence/stable_strength_evidence.py core/parsing/gg_parser.py tests/v2_smoke_tests.py
python3 tests/v2_smoke_tests.py
```

Result:

- `V2 smoke tests passed.`

# RECOMMENDED NEXT STEP

The next strong move is to start a thin UI shell over the already-built V2 read models:

1. Command Center
2. Session Lab
3. Memory Graph

That would turn the current backend surface set into the first usable operator-facing V2 experience.
