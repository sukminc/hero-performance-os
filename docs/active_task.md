# Active Task

## Title

Freeze the public MVP planning layer and rebase the repo around productization-first execution.

## Why this is the active task

Hero has now decided to move from operator-only analysis toward a public MVP path at `www.onepercentbetter.poker`.
The next useful move is to freeze the execution system so future product work can advance phase by phase with minimal input and clean handoff.

- define the public MVP boundary
- define auth/access architecture
- define launch-readiness gates
- define a task system that keeps work sequential, scoped, and handoff-friendly

If this is not locked now:

- frontend work will restart without a stable product boundary
- auth and access choices may leak into canonical poker truth
- later phases will create more conversational overhead instead of less

## Scope

In scope:

- write `public_mvp_plan.md`
- write `auth_and_access_architecture.md`
- write `launch_readiness_checklist.md`
- refresh active task / next-up state for productization execution
- archive the old local `opb-poker` folder and prepare this repo to become the new local `opb-poker`

Out of scope:

- public app implementation itself
- auth provider implementation itself
- billing implementation itself
- public UI polish itself

## Target outcome

At the end of this task:

- the public MVP path should be documented clearly enough to execute with minimal user input
- each phase should be divisible into scoped task packets
- the local repo naming path should be aligned with the future `opb-poker` continuation
- another chat should still be able to resume from the canonical handoff docs immediately

## First files to inspect

- `app/dev_server.py`
- `docs/public_mvp_plan.md`
- `docs/auth_and_access_architecture.md`
- `docs/launch_readiness_checklist.md`
- `docs/current_state.md`
- `docs/next_up.md`

## Validation target

Minimum:

- the productization docs exist and are executable
- the next phases can be progressed sequentially with durable handoff

## Completion rule

This task is complete only when:

1. the productization planning docs exist
2. the next-up queue is aligned
3. a report is written
4. the canonical handoff path remains accurate
