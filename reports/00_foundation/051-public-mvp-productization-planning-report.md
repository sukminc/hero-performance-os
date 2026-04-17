# 051 Public MVP Productization Planning Report

## TASK

Create the public MVP planning layer and convert the repo execution path into a phase-based, handoff-friendly productization system.

## WHAT I CHANGED

- added `docs/public_mvp_plan.md`
- added `docs/auth_and_access_architecture.md`
- added `docs/launch_readiness_checklist.md`
- updated `docs/active_task.md`
- updated `docs/current_state.md`
- added `docs/next_up.md`

## ARCHITECTURE IMPACT

- freezes the public MVP boundary before frontend/auth work begins
- separates auth/access concerns from canonical poker truth concerns
- creates a durable phase plan that reduces future conversational handoff overhead
- keeps operator-first backend truth while defining a path to public productization

## DECISIONS MADE

- public MVP will expose only a subset of surfaces
- operator shell remains private
- auth/access and billing can use hosted edge systems
- canonical poker interpretation truth must remain separate
- future work should now proceed phase by phase:
  - foundation
  - auth
  - upload
  - public interpretation
  - billing
  - launch ops

## RISKS / OPEN QUESTIONS

- auth provider choice is still open
- the exact public app stack has not yet been locked
- billing strategy and plan shape remain open
- operator/admin may still need a clearer deployment boundary later

## OUT OF SCOPE

- auth implementation
- upload implementation
- public UI implementation
- billing implementation

## TEST / VALIDATION

- docs created
- active-task state refreshed
- next-up packet created

## RECOMMENDED NEXT STEP

Start Phase 1 with a tightly scoped task that chooses the auth provider and scaffolds the public app shell with protected routes.
