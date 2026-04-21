# Active Task

## Title

Connect viewer ownership to real auth identity so the public shell enforces player data boundaries.

## Why this is the active task

The public shell cannot be trusted if a logged-in user can still resolve Hero data through a hardcoded viewer scope.
Before broader beta movement, the shell must:

- resolve the current auth identity,
- map that identity to the allowed player scope,
- and hide Today / Review / Brain / dashboard detail when ownership is unresolved.

If this is not built:

- public shell access remains mostly cosmetic
- Hero-vs-operator trust boundaries stay weak
- private beta credibility will still be lower than the backend truth deserves

## Scope

In scope:

- resolve viewer identity from current auth state
- map Hero ownership through explicit env-driven auth identity matching
- make public surfaces use viewer player scope instead of hardcoded Hero player id
- surface blank/safe states when ownership is unresolved
- refresh handoff docs
- write report

Out of scope:

- full multi-player account model
- full Supabase role/claim system
- checkout or entitlement expansion
- non-Hero onboarding beyond safe blank-state handling

## Target outcome

At the end of this task:

- Hero should see Hero data only when the auth identity is mapped to Hero ownership
- unmapped users should not see Hero dashboard / Today / Review / Brain data
- operator/admin should still be able to inspect deeper detail
- another chat should still be able to resume from the canonical handoff docs immediately

## First files to inspect

- `app/dev_server.py`
- `frontend/lib/viewer/`
- `frontend/lib/auth/`
- `frontend/lib/public-surfaces/`
- `frontend/app/app/`
- `frontend/app/operator/`
- `docs/current_state.md`
- `docs/next_up.md`

## Validation target

Minimum:

- viewer scope is not hardcoded to Hero anymore
- unmapped users do not resolve Hero surfaces
- mapped Hero access still works
- handoff is clear

## Completion rule

This task is complete only when:

1. the restored corpus is live in the current repo
2. public surfaces read through resolved viewer ownership instead of a hardcoded Hero id
3. unmapped auth identities get safe blank states rather than Hero data
4. a report is written
5. the canonical handoff path remains accurate
