# Demo Application Review And Provisioning Report

## TASK

Add the smallest operator workflow for reviewing durable demo applications and provisioning approved users into explicit player ownership access.

## WHAT I CHANGED

- extended demo application backend support with:
  - `list_demo_applications`
  - `update_demo_application_status`
  - `provision_demo_application_owner`
- added repository methods for fetching one application and updating application status/metadata
- added `frontend/lib/operator/demo-applications.ts` for operator-side application reads
- added `frontend/app/operator/demo-actions.ts` for operator status/provisioning actions
- updated `frontend/app/operator/page.tsx` to show captured applications, status actions, and approved-user provisioning controls

## ARCHITECTURE IMPACT

- demo leads now have an operator-visible review path
- approved users can be connected to canonical owner access without granting access at submission time
- provisioning requires an explicit target `player_id`, preserving the rule that applicants must not default to Hero

## DECISIONS MADE

- kept operator review inside the existing operator page instead of adding a deeper route tree
- allowed simple status transitions first, with audit detail stored in application metadata
- made provisioning email-based for the first private beta bridge, while viewer resolution can still use real Supabase identity when available

## RISKS / OPEN QUESTIONS

- the operator UI is intentionally minimal and not yet a full intake dashboard
- provisioning currently trusts the operator-entered target player id
- status history is lightweight metadata rather than a full event table

## OUT OF SCOPE

- email notifications
- CRM integration
- self-serve account creation
- automatic player creation
- full audit/event log

## TEST / VALIDATION

- direct temporary-SQLite dry run passed:
  - submit application
  - approve application
  - provision owner access
  - resolve viewer access by email to the provisioned player id
- `python3 -m py_compile core/beta/demo_applications.py core/auth/viewer_access.py core/storage/sqlite_repository.py core/storage/postgres_repository.py core/storage/models.py` passed
- `python3 tests/v2_smoke_tests.py` passed
- `python3 tests/legacy_corpus_tests.py` passed
- `cd frontend && npm run typecheck` passed
- `cd frontend && npm run build` passed

## RECOMMENDED NEXT STEP

Run the full Hero login/upload/output update check with real post-cutoff GG hand histories.
