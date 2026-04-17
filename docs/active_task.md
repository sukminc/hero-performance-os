# Active Task

## Title

Build the Phase 5 launch operations foundation for the public MVP shell.

## Why this is the active task

The public MVP shell can now authenticate, upload, render interpretation, and show billing boundaries.
The next useful move is to create the operating discipline for a limited beta, because without launch ops the product remains technically assembled but operationally fragile.

- document production env needs
- define support/admin workflow
- define upload failure handling
- define rollback and beta gate rules

If this is not built:

- launch decisions will rely on memory instead of repo truth
- support response will be inconsistent
- beta risk will stay implicit rather than managed

## Scope

In scope:

- write launch ops runbook
- write private beta checklist
- update launch readiness checklist
- update runbook references
- refresh current/active/next-up state
- write report

Out of scope:

- full observability tooling
- automated incident response
- real support inbox integration
- actual beta launch execution

## Target outcome

At the end of this task:

- beta launch rules should be explicit
- support/admin handling should be documented
- failure/rollback behavior should be explicit
- the next task should be able to move into live checkout wiring or a real private beta
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
- `docs/launch_ops_runbook.md`
- `docs/private_beta_checklist.md`
- `docs/current_state.md`
- `docs/next_up.md`

## Validation target

Minimum:

- launch docs exist
- beta gate is explicit
- handoff is clear

## Completion rule

This task is complete only when:

1. the launch ops docs exist
2. the next-up queue is aligned
3. a report is written
4. the canonical handoff path remains accurate
