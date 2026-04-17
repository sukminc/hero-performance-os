# Active Task

## Title

Build the Phase 2 upload service foundation for the public MVP shell.

## Why this is the active task

The public auth shell now exists and compiles.
The next useful move is to make upload the first real user action, because the public product cannot be meaningful until a signed-in user can hand the system a GG session packet and see processing state.

- wire `/app/upload`
- invoke the canonical ingest path
- fail duplicates safely
- surface upload status back to the user

If this is not built:

- the public app remains decorative
- Today / Review / Brain cannot be attached to user-owned uploads
- productization momentum stalls after the auth shell

## Scope

In scope:

- build the upload UI on `/app/upload`
- add upload action/runtime scaffolding
- invoke canonical Python ingest
- show latest upload statuses
- keep duplicate handling safe
- validate with a production build

Out of scope:

- Today / Review / Brain public data implementation
- billing implementation
- account-to-player linking
- cloud storage

## Target outcome

At the end of this task:

- authenticated users should have a real upload path
- upload status should be visible
- duplicate-safe ingest should be connected
- the next task should be able to start public Today / Review / Brain rendering immediately
- another chat should still be able to resume from the canonical handoff docs immediately

## First files to inspect

- `app/dev_server.py`
- `frontend/package.json`
- `frontend/app/app/upload/`
- `frontend/lib/uploads/`
- `core/ingest/ingest_jobs.py`
- `docs/current_state.md`
- `docs/next_up.md`

## Validation target

Minimum:

- upload action exists
- latest upload status is visible
- the build passes

## Completion rule

This task is complete only when:

1. the upload foundation exists
2. the build passes
3. a report is written
4. the canonical handoff path remains accurate
