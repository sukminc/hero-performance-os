# Active Task

## Title

Build the Phase 4 billing and entitlement foundation for the public MVP shell.

## Why this is the active task

The public MVP shell can now authenticate, upload, and render compact interpretation surfaces.
The next useful move is to define the commercial boundary, because without plan state and entitlement the product is still an open demo instead of a controllable service.

- choose billing provider
- define plans
- define entitlement gates
- surface account plan state

If this is not built:

- there is no product boundary between free and paid value
- account surfaces remain incomplete
- launch readiness stays theoretical

## Scope

In scope:

- choose the billing provider
- define the first plan model
- scaffold Stripe environment/config
- add account entitlement rendering
- add pricing foundation
- reflect free vs paid gates in public interpretation surfaces
- validate with a production build

Out of scope:

- live checkout flow
- webhook processing
- account-to-player linking
- final launch operations

## Target outcome

At the end of this task:

- pricing/account foundation should exist
- plan state and entitlement model should be visible
- public surfaces should acknowledge free vs paid boundaries
- the next task should be able to start launch operations or live checkout wiring
- another chat should still be able to resume from the canonical handoff docs immediately

## First files to inspect

- `app/dev_server.py`
- `frontend/package.json`
- `frontend/app/app/upload/`
- `frontend/app/app/today/page.tsx`
- `frontend/app/app/review/page.tsx`
- `frontend/app/app/brain/page.tsx`
- `frontend/app/pricing/page.tsx`
- `frontend/app/app/account/page.tsx`
- `frontend/lib/billing/`
- `docs/current_state.md`
- `docs/next_up.md`

## Validation target

Minimum:

- pricing/account surfaces render
- entitlements are explicit
- build passes

## Completion rule

This task is complete only when:

1. the billing foundation exists
2. the build passes
3. a report is written
4. the canonical handoff path remains accurate
