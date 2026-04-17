# Launch Readiness Checklist

## Objective

Provide a simple release gate so public MVP work can move phase by phase without conversational drift.

## Phase 0: Productization Foundation

- [ ] `public_mvp_plan.md` approved
- [ ] `auth_and_access_architecture.md` approved
- [ ] `launch_readiness_checklist.md` approved
- [ ] active task updated
- [ ] next-up queue updated
- [ ] report written

## Phase 1: Auth + App Shell

- [ ] auth provider chosen
- [ ] login works
- [ ] signup works
- [ ] protected routes work
- [ ] operator role gate works
- [ ] account logout/session flow works
- [ ] report written

## Phase 2: Upload Service

- [ ] GG packet upload works
- [ ] duplicate file handling works
- [ ] zero-hand safe failure works
- [ ] processing status is visible
- [ ] upload ownership is stored
- [ ] user can find latest upload result
- [ ] report written

## Phase 3: Public Interpretation Surfaces

- [ ] Today page renders for authenticated user
- [ ] Review page renders for authenticated user
- [ ] Brain page renders for authenticated user
- [ ] public-safe pattern cards render
- [ ] sample/confidence language is visible where needed
- [ ] no operator-only internals leak into public UI
- [ ] report written

## Phase 4: Billing + Entitlement

- [ ] Stripe products/prices exist
- [ ] account can attach to plan state
- [ ] upload limit enforcement works
- [ ] premium gating works
- [ ] account page shows plan correctly
- [ ] downgrade/failure state behaves safely
- [ ] report written

## Phase 5: Launch Operations

- [ ] production env documented
- [ ] logging/monitoring in place
- [ ] upload failure alert path exists
- [ ] admin support path exists
- [ ] rollback path exists
- [ ] private beta checklist complete
- [ ] report written

## Release Gate Rules

### Do not launch if

- uploads can silently fail
- zero-hand parsing emits fake interpretation
- Today / Review / Brain can show another user's data
- operator-only surfaces leak publicly
- public pages imply live assistance or RTA

### Launch is acceptable if

- auth is stable
- upload is stable
- interpretation is believable enough for limited beta
- operator fallback exists
- billing and access state are understandable

## Minimal-Input Delivery Rule

Each phase should be broken into small tasks that can be handed off cleanly.

Each task must include:

- title
- objective
- scope
- out of scope
- validation target
- report destination
- assumptions made

## Handoff Template

Use this exact structure after each meaningful task:

- TASK
- WHAT I CHANGED
- ARCHITECTURE IMPACT
- DECISIONS MADE
- RISKS / OPEN QUESTIONS
- OUT OF SCOPE
- TEST / VALIDATION
- RECOMMENDED NEXT STEP

## Suggested First Public Beta Gate

- [ ] only invited users can access the product
- [ ] operator can inspect and correct bad outputs
- [ ] one broken upload does not block the whole user account
- [ ] cumulative memory persists correctly across uploads
- [ ] the product still feels like a poker adjustment engine, not a generic stat page
