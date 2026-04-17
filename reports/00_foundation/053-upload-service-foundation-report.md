# 053 Upload Service Foundation Report

## TASK

Build the first user-owned GG packet upload path inside the public MVP shell.

## WHAT I CHANGED

- updated `core/ingest/ingest_jobs.py` to emit JSON output for shell-friendly consumption
- added frontend upload runtime helpers in:
  - `frontend/lib/uploads/runtime.ts`
  - `frontend/lib/uploads/ingest.ts`
  - `frontend/lib/uploads/status.ts`
- added upload server action in `frontend/app/app/upload/actions.ts`
- added upload form client component in `frontend/app/app/upload/upload-form.tsx`
- turned `/app/upload` into a real upload foundation route with:
  - GG `.txt` file input
  - canonical ingest invocation
  - duplicate-safe result handling
  - latest upload status list
- updated active/current/next-up docs for Phase 3 readiness

## ARCHITECTURE IMPACT

- connects the public app shell to the canonical Python ingest path without moving poker truth into the frontend
- keeps the upload layer thin and server-side
- proves that public productization can reuse existing backend truth instead of rebuilding logic in JS

## DECISIONS MADE

- upload foundation uses local server action + Python ingest invocation
- upload temp files go to repo-local temp upload storage by default
- latest upload status is read from canonical SQLite
- duplicate handling remains owned by existing backend duplicate guard logic

## RISKS / OPEN QUESTIONS

- upload ownership is not yet user-scoped in storage reads
- local filesystem upload temp path is good for foundation but not the final cloud path
- upload action currently assumes same-machine backend access
- public auth identity is still not linked to player ownership yet

## OUT OF SCOPE

- cloud object storage
- async queue/job worker
- public Today / Review / Brain rendering
- billing

## TEST / VALIDATION

- `npm run build` passed in `frontend/`
- upload route compiles
- latest upload status read path compiles

## RECOMMENDED NEXT STEP

Connect `/app/today`, `/app/review`, and `/app/brain` to the latest user-owned upload outputs with public-safe confidence labeling.
