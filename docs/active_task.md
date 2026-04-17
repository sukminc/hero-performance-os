# Active Task

## Title

Build the Phase 1 public auth provider and app shell foundation.

## Why this is the active task

The public MVP planning layer is now frozen.
The next useful move is to stand up the first real authenticated app shell so later upload and interpretation work has a stable public surface to land on.

- choose the auth provider
- scaffold public and protected routes
- create a role-aware app shell
- keep auth separated from canonical poker truth

If this is not built:

- upload work has nowhere stable to land
- public routing will drift while interpretation work continues
- future handoff will get messy again

## Scope

In scope:

- choose the Phase 1 auth provider
- scaffold the public `frontend/` app shell
- add public routes and protected `/app` routes
- add operator route gating foundation
- add environment/config scaffolding
- validate the scaffold with a production build

Out of scope:

- upload implementation
- Today / Review / Brain public data implementation
- billing implementation
- account-to-player linking

## Target outcome

At the end of this task:

- the public app shell should compile
- public vs protected routes should be stable
- the auth provider should be chosen
- the next task should be able to start upload foundation immediately
- another chat should still be able to resume from the canonical handoff docs immediately

## First files to inspect

- `app/dev_server.py`
- `frontend/package.json`
- `frontend/app/`
- `frontend/proxy.ts`
- `frontend/lib/auth/`
- `docs/current_state.md`
- `docs/next_up.md`

## Validation target

Minimum:

- the frontend auth shell compiles
- protected routing exists
- auth provider choice is explicit

## Completion rule

This task is complete only when:

1. the frontend shell exists
2. the build passes
3. a report is written
4. the canonical handoff path remains accurate
