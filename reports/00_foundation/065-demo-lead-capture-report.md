# Demo Lead Capture Report

## TASK

Replace the temporary demo apply UI behavior with durable lead capture and preserve a clear handoff into canonical ownership provisioning.

## WHAT I CHANGED

- added `DemoApplicationRecord` to storage models
- added `demo_applications` storage support to both SQLite and Postgres repositories
- updated the canonical ownership SQL draft to include demo applications
- added `core/beta/demo_applications.py` for validated demo application submission
- added `frontend/app/demo-apply/actions.ts` so the public demo form submits through a server action
- updated `frontend/app/demo-apply-form.tsx` so form submissions persist into storage and show server-confirmed success/failure
- added a small `.form-error` style for failed submissions
- added `docs/demo_lead_provisioning.md` to define the intake -> approval -> ownership handoff
- updated handoff docs so the next active task is operator review/provisioning for captured applications

## ARCHITECTURE IMPACT

- demo intake is now durable backend data instead of local-only UI state
- lead capture remains separate from poker truth and from user-player ownership until the operator explicitly provisions access
- captured applications can now become the input to a future operator approval/provisioning loop

## DECISIONS MADE

- used the existing Next server action -> Python backend pattern already used by upload/surface flows
- kept the first lead model small: name, email, games, help goal, status, source, metadata
- preserved the current GG Ontario recruiting boundary in application metadata
- did not auto-create user ownership from a demo application submission

## RISKS / OPEN QUESTIONS

- there is not yet an operator UI for reviewing captured applications
- there is not yet an action that turns an approved application into `user_accounts` / `user_player_access`
- duplicate applications are allowed for now; operator review should decide whether to merge or ignore repeats

## OUT OF SCOPE

- CRM integration
- email notifications
- self-serve signup
- automatic user-player provisioning
- checkout changes

## TEST / VALIDATION

- `python3 -m py_compile core/beta/demo_applications.py core/storage/sqlite_repository.py core/storage/postgres_repository.py core/storage/models.py` passed
- direct temporary-SQLite demo submission persisted and was read back as `new`
- `python3 tests/v2_smoke_tests.py` passed
- `python3 tests/legacy_corpus_tests.py` passed
- `cd frontend && npm run typecheck` passed
- `cd frontend && npm run build` passed

## RECOMMENDED NEXT STEP

Add the operator review/provisioning loop for demo applications, then run an internal private-beta dry run from application through upload and Today / Review / Brain output.
