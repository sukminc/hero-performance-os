# Demo Lead Provisioning

## Purpose

Define the current handoff from durable demo application capture into canonical ownership provisioning.

Demo applications are not player access.
They are intake records only.

## Current Flow

1. Visitor submits the public demo application form.
2. The app writes a `demo_applications` row with status `new`.
3. Operator reviews the application.
4. Operator may move it to `screening`, `approved`, `rejected`, or `provisioned`.
5. Only after approval should the system create or connect:
   - `user_accounts`
   - `user_player_access`
   - optional `user_global_roles` when the user is an operator/admin

## Status Meaning

- `new`: captured but not reviewed
- `screening`: operator is checking fit and follow-up
- `approved`: user may be provisioned into access
- `rejected`: user should not receive beta access
- `provisioned`: access was explicitly granted

## Safety Rule

Submitting a demo application must never grant player access.

Until provisioning creates an active `user_player_access` row, the authenticated user must remain unscoped and see blank public-shell states.

## First Provisioning Rule

For private beta, one approved application should create at most one active owner access row:

- `access_role = owner`
- `status = active`
- `player_id` is assigned explicitly by the operator

Do not infer `player_id` from email alone.
Do not default applicants to Hero.

## Next Implementation Target

Add an operator-facing application review surface that can:

- list captured applications
- update application status
- show whether a matching `user_account` already exists
- prepare the explicit ownership grant for approved users

