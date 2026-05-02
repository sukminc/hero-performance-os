# Active Task

## Title

Run a real Hero hand-history update check through login, upload, and changed Today / Review / Brain outputs.

## Why this is the active task

Viewer ownership hardening, durable demo capture, and operator provisioning now exist.
Upload now resolves through the logged-in viewer player id.
The next blocker is proving the complete Hero workflow with real post-cutoff hand histories.
Before broader private beta movement, Hero needs to verify:

- login works
- upload writes to the correct player model
- new hand histories update the canonical corpus
- Today / Review / Brain change in a believable way

If this is not built:

- private beta confidence remains theoretical
- upload/result feedback cannot be trusted end-to-end
- Hero cannot decide the next product direction from real post-cutoff data

## Scope

In scope:

- run the app locally
- login as Hero/operator dev user where appropriate
- upload a real GG hand-history batch provided by Hero
- compare pre/post corpus and surface outputs
- report whether Today / Review / Brain changed and whether the change is believable
- refresh handoff docs
- write report

Out of scope:

- broad frontend polish
- checkout or entitlement expansion
- solver/GTO exactness claims
- live in-hand advice

## Target outcome

At the end of this task:

- Hero should know whether the login -> upload -> changed output loop works on real new hand histories
- the pre/post surface change should be captured in a report
- any parsing/output credibility gaps should become the next task queue
- another chat should still be able to resume from the canonical handoff docs immediately

## First files to inspect

- `frontend/app/app/upload/`
- `frontend/lib/uploads/`
- `frontend/lib/public-surfaces/`
- `core/ingest/`
- `core/parsing/`
- `docs/current_state.md`
- `docs/next_up.md`

## Validation target

Minimum:

- upload uses the logged-in viewer player id
- new hand histories ingest or fail honestly
- Today / Review / Brain can be compared before and after upload
- handoff is clear

## Completion rule

This task is complete only when:

1. a real upload run is performed or blocked on missing files explicitly
2. pre/post corpus state is captured
3. pre/post Today / Review / Brain changes are captured
4. parsing/output credibility gaps are documented
5. a report is written
