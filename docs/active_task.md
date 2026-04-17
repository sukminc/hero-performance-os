# Active Task

## Title

Extend the operator shell from conviction review into tournament timing + stack comfort interpretation.

## Why this is the active task

Hero can now inspect `13x13`, HUD trend, field ecology, conviction review, and integrated review cards.
The next useful move is to test whether entry timing, bullet state, and preferred operating depth actually line up with cleaner decision quality.

- detect whether early / mid / late entry shifts performance
- detect whether first bullet and re-entry bullets behave differently
- detect whether `20-25bb` or `25-30bb` really are strong operating zones
- connect stack comfort back to AOF leaks, conviction hands, HUD trend, and field ecology

If this is not built:

- stack comfort remains a feeling instead of an inspectable truth surface
- tournament timing and bullet-state interpretation remain spread across multiple tabs
- Hero cannot clearly test whether the `20bb` neighborhood is actually where decisions stay best

## Scope

In scope:

- implement a read-only timing + stack review API on canonical SQLite
- expose a browser-viewable Tournament Timing + Stack Comfort tab
- add entry-timing proxy, bullet proxy, stack-band comfort cards, and AOF leak queue
- connect the new view to conviction, field, and HUD context

Out of scope:

- official late-registration truth
- exact solver or GTO integration
- final timing/bullet scoring truth
- consumer-facing polish

## Target outcome

At the end of this task:

- Hero should be able to inspect tournament timing, bullet proxy, and stack comfort in the browser
- the operator shell should show whether the `20bb` neighborhood is actually performing well
- the view should connect stack comfort back to AOF, conviction, field, and HUD interpretation
- another chat should still be able to resume from the canonical handoff docs immediately

## First files to inspect

- `app/dev_server.py`
- `app/api/hand_matrix.py`
- `app/api/timing_stack_review.py`
- `app/ui/index.html`
- `app/ui/main.js`
- `docs/current_state.md`

## Validation target

Minimum:

- the local shell exposes a usable Tournament Timing + Stack Comfort tab against canonical SQLite

## Completion rule

This task is complete only when:

1. the timing + stack review route exists
2. the browser shell can render it
3. a report is written
4. the canonical handoff path remains accurate
