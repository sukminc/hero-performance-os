# Phase 1 Auth Foundation

## Chosen provider

Phase 1 chooses `Supabase Auth`.

## Why

- fastest path to email/password and magic-link style auth
- good fit for early protected-route MVP work
- can handle account/session concerns without becoming canonical poker truth
- consistent with the product rule that auth is an edge service, not core poker truth

## Phase 1 deliverables

- public routes
- login/signup shell
- protected `/app` shell
- operator route gate
- environment scaffold

## Not yet implemented

- live sign-in actions
- account bootstrap persistence
- upload ownership linkage
- billing entitlement
