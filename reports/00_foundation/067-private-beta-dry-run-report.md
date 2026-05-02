# Private Beta Dry Run Report

## TASK

Define and partially execute the private-beta dry run path from application capture through provisioning and owned upload.

## WHAT I CHANGED

- added `docs/private_beta_dry_run.md` with the browser checklist for apply -> approve -> provision -> login -> upload -> Today / Review / Brain
- validated the backend version of the dry run with temporary SQLite
- confirmed the frontend builds with the operator application review/provisioning flow

## ARCHITECTURE IMPACT

- the beta path is now concrete enough to test with real Hero hand-history files
- the system preserves the separation between intake, ownership, upload, and interpretation surfaces
- upload ownership is now part of the dry-run acceptance criteria

## DECISIONS MADE

- treated this task as a dry-run readiness pass rather than pretending a real Hero upload occurred without new files
- made the next task explicitly depend on Hero-provided post-cutoff hand histories

## RISKS / OPEN QUESTIONS

- no new real hand-history batch was provided in this run, so output changes were not measured yet
- browser-level verification still needs to be run once the user is ready to test interactively

## OUT OF SCOPE

- production deployment
- real beta invitation
- checkout
- parser fixes for unknown future files

## TEST / VALIDATION

- backend apply -> approve -> provision -> resolve dry run passed
- frontend typecheck and build passed
- smoke and legacy corpus tests passed

## RECOMMENDED NEXT STEP

Use Hero's new hand-history files to run the real update check and decide the next product direction from observed parser/output behavior.
