# Active Task

## Title

Build the Phase 3 public interpretation surfaces for the public MVP shell.

## Why this is the active task

The public app can now authenticate and upload.
The next useful move is to expose believable Today / Review / Brain reads, because that is the first moment the MVP starts behaving like a real product instead of a shell.

- connect `/app/today`
- connect `/app/review`
- connect `/app/brain`
- keep the rendering public-safe and confidence-aware

If this is not built:

- uploads terminate into a dead end
- users cannot feel the value of cumulative interpretation
- the public MVP still does not answer the real product question

## Scope

In scope:

- connect the public Today page
- connect the public Review page
- connect the public Brain page
- reuse canonical backend outputs
- keep operator-only internals out of public UI
- validate with a production build

Out of scope:

- billing implementation
- account-to-player linking
- final public polish
- billing

## Target outcome

At the end of this task:

- public Today / Review / Brain should render
- the pages should feel product-like without leaking operator internals
- the next task should be able to start billing/entitlement or deeper public UX cleanup
- another chat should still be able to resume from the canonical handoff docs immediately

## First files to inspect

- `app/dev_server.py`
- `frontend/package.json`
- `frontend/app/app/upload/`
- `frontend/app/app/today/page.tsx`
- `frontend/app/app/review/page.tsx`
- `frontend/app/app/brain/page.tsx`
- `frontend/lib/public-surfaces/`
- `docs/current_state.md`
- `docs/next_up.md`

## Validation target

Minimum:

- Today / Review / Brain render
- build passes
- the build passes

## Completion rule

This task is complete only when:

1. the public interpretation surfaces exist
2. the build passes
3. a report is written
4. the canonical handoff path remains accurate
