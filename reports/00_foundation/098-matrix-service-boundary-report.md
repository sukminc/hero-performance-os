# Task 098: Matrix Service Boundary Slice

## TASK

Move the operator Matrix read path onto the new backend service boundary as the second production-read slice.

## WHAT I CHANGED

- Added an optional `observations` injection point to `get_hand_matrix_payload` so service tests can exercise Matrix assembly without SQLite.
- Added `build_matrix_service_payload` to `app/service/routes.py`.
- Added a stdlib HTTP route for `GET /v1/players/{player_id}/matrix`.
- Updated `getHeroBaselineMatrix` in `frontend/lib/public-surfaces/read.ts` to call `OPB_BACKEND_BASE_URL` first and fall back to the existing local subprocess path unless `OPB_REQUIRE_BACKEND_SERVICE=1`.
- Extended `tests/service_boundary_tests.py` to cover the Matrix service wrapper and payload shape.

## ARCHITECTURE IMPACT

Matrix now follows the same service-first boundary pattern as Today. This does not remove all Matrix storage debt yet, because the default Matrix builder still fetches observations from SQLite when no observations are injected. It does, however, establish the endpoint shape and frontend switching point needed for the production backend migration.

The `observations` injection point makes the next Postgres-safe refactor cleaner: observation collection can move behind a repository-backed adapter without rewriting Matrix scoring and surface assembly.

## DECISIONS MADE

- Preserve the existing Matrix payload shape so operator UI does not need a redesign.
- Use `window=all` and `selected_hand` query params in the service route to match the current operator page behavior.
- Keep local subprocess fallback for Hero-local development.

## RISKS / OPEN QUESTIONS

- Default Matrix observation fetching still uses direct SQLite through `get_sqlite_connection`.
- Backend service auth/player access is still not first-class at the service boundary.
- Other operator surfaces and mutations still need migration.

## OUT OF SCOPE

- No Postgres observation adapter in this task.
- No Matrix approve/reject overlays.
- No UI redesign.
- No all-surface migration.

## TEST / VALIDATION

- `python3 tests/service_boundary_tests.py`
- `python3 tests/v2_smoke_tests.py`
- `npm run build`

## RECOMMENDED NEXT STEP

Replace Matrix's default observation fetcher with a repository-compatible adapter so the service route can run against managed Postgres without direct SQLite queries.
