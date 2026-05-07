# Task 097: Backend Service Boundary Skeleton

## TASK

Create the first narrow backend service/API boundary so Next.js can stop spawning Python directly for one vertical slice.

## WHAT I CHANGED

- Added `app/service/routes.py` with service-layer health and Today payload builders.
- Added `app/service/server.py`, a stdlib HTTP JSON entrypoint for `/health` and `/v1/players/{player_id}/today`.
- Updated `app/api/today.py` so `get_today_payload` can accept an injected repository for service tests and future service composition.
- Updated `frontend/lib/public-surfaces/read.ts` so `getPublicTodaySurface` calls `OPB_BACKEND_BASE_URL` first when configured, then falls back to the existing local Python subprocess path unless `OPB_REQUIRE_BACKEND_SERVICE=1`.
- Added `tests/service_boundary_tests.py`.

## ARCHITECTURE IMPACT

This establishes the first production-facing boundary without rewriting the Python interpretation engine. Today can now be read through a backend service shape while local Hero development keeps the current SQLite/subprocess fallback.

The implementation is intentionally dependency-light because the repo currently has no Python dependency manifest and no FastAPI/uvicorn dependency. The boundary can later move to FastAPI without changing the selected API shape.

## DECISIONS MADE

- Start with Today as the first vertical slice because it is the smallest core MVP surface and already has a compact API payload.
- Keep the service payload wrapped with `ok`, `surface`, `player_id`, and `data` so provenance is explicit.
- Require bearer auth only when `OPB_BACKEND_API_TOKEN` is configured.
- Add `OPB_REQUIRE_BACKEND_SERVICE=1` as a production guardrail to prevent silent fallback to local subprocess when the service is expected.

## RISKS / OPEN QUESTIONS

- This is a skeleton, not a full production deployment.
- The service does not yet enforce viewer/player access. Next.js still resolves viewer access before requesting Today, but the backend boundary needs first-class auth before external beta.
- Only Today has been migrated. Review, Brain, Matrix, AOF, Big Win, upload, demo applications, and operator mutations still use direct subprocess paths.
- The service currently uses Python stdlib HTTP primitives. A later FastAPI migration may be worthwhile once dependencies are formalized.

## OUT OF SCOPE

- No managed Postgres provisioning.
- No all-surface migration.
- No auth token issuance flow.
- No upload/mutation endpoint migration.
- No frontend redesign.

## TEST / VALIDATION

- `python3 tests/service_boundary_tests.py`
- `python3 tests/v2_smoke_tests.py`
- `npm run build`

## RECOMMENDED NEXT STEP

Migrate one operator read surface, preferably Matrix, through the same backend boundary and replace its direct SQLite wrapper with a `V2Repository`-compatible path before moving write actions.
