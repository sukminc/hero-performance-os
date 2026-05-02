# Viewer Owned Upload Report

## TASK

Ensure GG hand-history uploads use the logged-in viewer's resolved player ownership instead of defaulting silently to Hero.

## WHAT I CHANGED

- updated upload server action to resolve `getViewerContext()` before ingest
- changed `ingestUploadedFiles` to require a `playerId`
- passed `--player-id` into the Python ingest job for each uploaded packet
- scoped upload status and coverage summaries by viewer `playerId`
- updated upload page copy to explain that upload writes to the player model resolved from login

## ARCHITECTURE IMPACT

- uploads now respect canonical ownership boundaries
- unmapped users cannot upload into Hero by accident
- this makes the upcoming Hero real hand-history update check meaningful because the upload path is tied to viewer ownership

## DECISIONS MADE

- kept the existing Python ingest job and passed the resolved `playerId` explicitly
- returned a clear upload error when a login has no player ownership mapping
- scoped upload history reads by player instead of showing global ingest rows

## RISKS / OPEN QUESTIONS

- operator users still resolve to Hero in the current Hero-first bridge; broader multi-player operator selection remains future work
- upload coverage SQL is still direct SQLite query code in the frontend helper and should eventually move behind a backend API/repository read

## OUT OF SCOPE

- multi-player upload picker
- production API route refactor
- parser/evidence changes

## TEST / VALIDATION

- `cd frontend && npm run typecheck` passed
- `cd frontend && npm run build` passed
- backend smoke tests passed

## RECOMMENDED NEXT STEP

Run the real Hero hand-history upload and compare Today / Review / Brain before and after ingestion.
