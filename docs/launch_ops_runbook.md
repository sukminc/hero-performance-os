# Launch Ops Runbook

## Objective

Provide the minimum operating discipline needed to run a limited public beta of One Percent Better Poker without relying on chat memory.

## Production Environment Checklist

### App shell

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY`
- `STRIPE_SECRET_KEY`
- `STRIPE_PRO_MONTHLY_PRICE_ID`
- `STRIPE_WEBHOOK_SECRET`

### Backend/runtime

- `SQLITE_DB_PATH` or canonical production database target
- `V2_STORAGE_BACKEND`
- upload temp/storage path
- production domain config

## Launch Day Checks

### Before opening access

- auth login works
- protected routes work
- upload works
- duplicate skip works
- Today / Review / Brain render
- pricing/account render
- one full end-to-end packet ingest succeeds

### Do not open beta if

- uploads can silently fail
- duplicate guard is broken
- another user's data can be seen
- public pages expose operator internals
- billing state is misleading

## Upload Failure Handling

### Symptom

User uploads a GG packet and does not see a successful result.

### Immediate checks

1. inspect upload temp/storage path
2. inspect latest `ingest_files` rows
3. confirm duplicate skip vs true failure
4. confirm parse status
5. confirm zero-hand failure is surfaced honestly

### Operator response

- if duplicate: tell user the packet was already processed
- if zero-hand: tell user the file parsed no usable hands
- if ingest crash: mark as operator follow-up required and do not fabricate output

## Support/Admin Workflow

### Minimum support tools required

- latest upload inspection
- latest ingest status inspection
- latest session id lookup
- latest Today / Review / Brain read
- operator-only route access

### Support response categories

- auth issue
- upload issue
- duplicate issue
- interpretation quality issue
- billing issue

## Limited Beta Protocol

### Recommended shape

- invite-only
- low user count
- operator review fallback available
- direct support channel available

### Beta gate

- one working happy path from signup to upload to Today
- one verified duplicate-file path
- one verified failed-zero-hand path
- one verified billing-plan display path

## Rollback Rule

Rollback or pause beta access if:

- uploads stop processing
- auth breaks for multiple users
- billing state becomes misleading
- public data isolation is in doubt

## Daily Operating Routine

1. check newest uploads
2. check newest failures
3. check latest Today / Review / Brain outputs
4. check support queue
5. confirm no broken billing/account state

## Handoff Rule

At end of each beta-related task, update:

- `docs/current_state.md`
- `docs/active_task.md`
- `docs/next_up.md`
- relevant report file
