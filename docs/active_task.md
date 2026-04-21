# Active Task

## Title

Restore Hero corpus visibility in the public shell and upgrade upload intake for post-cutoff batch dumps.

## Why this is the active task

The public shell cannot be trusted if Hero logs in and sees an empty corpus.
Before any further beta-facing movement, the app must:

- point to the real Hero canonical corpus,
- show the current cutoff date of already-ingested data,
- and accept the next backlog as large multi-file or zip batch uploads.

If this is not built:

- Hero will think the data is gone
- post-cutoff uploads will be tedious and fragile
- private beta credibility will be false because the main user's own corpus is not visible

## Scope

In scope:

- restore current repo canonical SQLite from the archived Hero corpus
- expose corpus coverage and last ingested date in the upload surface
- support multiple `.txt` uploads and `.zip` expansion in the public uploader
- refresh handoff docs
- write report

Out of scope:

- full cloud storage ingestion
- background queueing
- multi-user ownership hardening
- production drag-and-drop polish beyond local MVP usefulness

## Target outcome

At the end of this task:

- Hero's historical corpus should be visible again in the public shell
- the current cutoff date should be explicit before new dumps are uploaded
- new zip dumps should be ingestible in one batch
- another chat should still be able to resume from the canonical handoff docs immediately

## First files to inspect

- `app/dev_server.py`
- `frontend/package.json`
- `frontend/app/app/upload/`
- `frontend/lib/uploads/`
- `core/ingest/`
- `docs/current_state.md`
- `docs/next_up.md`

## Validation target

Minimum:

- Hero corpus is visible again
- upload surface shows cutoff coverage
- zip batch intake works locally
- handoff is clear

## Completion rule

This task is complete only when:

1. the restored corpus is live in the current repo
2. the upload surface exposes current coverage and cutoff date
3. batch zip upload works through the public shell
4. a report is written
5. the canonical handoff path remains accurate
