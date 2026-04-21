# Next Up

## Immediate next phase

Phase 6: Hero-first private beta hardening

## Recommended first task packet

### Title

Move operator authorization off display cookies and define the smallest canonical user-to-player ownership record.

### Objective

Replace the remaining cosmetic operator gate with verified auth-derived authorization, then define the minimal durable ownership truth needed for post-Hero beta users.

### Scope

- derive operator authorization from verified auth identity rather than the `opb_role` display cookie alone
- define the smallest canonical user-to-player ownership record for future beta users
- preserve the new safe blank-state behavior for unmapped authenticated users
- document the env-vs-canonical ownership transition path

### Out of scope

- full multi-tenant production auth stack
- checkout
- broad non-Hero onboarding implementation

### Validation target

- operator route access no longer depends on a display-only cookie
- Hero ownership mapping remains intact
- the next step toward non-Hero beta users is explicit in repo truth

### Report destination

- `reports/00_foundation/060-operator-auth-and-ownership-truth-report.md`

## After that

1. use beta findings to decide whether checkout is ready
