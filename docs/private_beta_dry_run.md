# Private Beta Dry Run

## Purpose

Use this checklist to prove the private-beta path before inviting real users.

## Current Dry Run Coverage

Verified in code:

- demo application can be submitted durably
- operator can move an application to `approved`
- operator can provision approved email into owner access
- viewer resolution maps that email to the provisioned `player_id`
- upload ingest now receives the logged-in viewer `playerId`
- unmapped users still do not receive player data

## Manual Browser Dry Run

1. Start the frontend app.
2. Open `/signup`.
3. Submit a demo application.
4. Open `/auth/dev-login?role=operator&next=/operator`.
5. Confirm the application appears in the operator view.
6. Mark it `approved`.
7. Provision it with an explicit target player id.
8. Log in as the provisioned user or resolve that user through canonical auth.
9. Open `/app/upload`.
10. Upload a GG `.txt` or `.zip` hand-history batch.
11. Confirm recent upload rows and corpus counts update.
12. Open `/app/today`, `/app/review`, and `/app/brain`.
13. Capture what changed and whether it feels believable.

## Safety Checks

- Demo application submission must not grant player access.
- Provisioning must require an explicit player id.
- Upload must not default to Hero when the login is unmapped.
- Zero-hand parses must still fail or skip honestly.

