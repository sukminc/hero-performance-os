# Public MVP Plan

## Objective

Turn the current operator-grade poker performance engine into a limited public MVP that serious players can log into, upload GG session packets to, and receive believable Today / Review / Brain outputs from.

The public MVP must preserve the current backend truth model instead of replacing it with a frontend-first toy.

## Product Boundary

The first public MVP is:

- authenticated
- upload-driven
- post-hoc only
- memory-backed
- paid-product compatible
- operator-supervised

The first public MVP is not:

- a real-time poker tool
- a generic hand-history browser
- a solver product
- a public-facing version of the full operator shell

## Public MVP Promise

For a logged-in player, the MVP should let them:

1. create an account,
2. upload one or more GG `.txt` session packets,
3. see whether processing succeeded,
4. receive current Today / Review / Brain outputs,
5. inspect a small number of believable pattern cards,
6. and return later without losing cumulative interpretation.

## MVP Surface Freeze

### Public surfaces in scope

- marketing landing page
- login / signup
- authenticated app shell
- upload page
- upload history / processing status
- Today page
- Review page
- Brain page
- lightweight pattern watch cards
- account / plan status

### Operator-only surfaces kept private

- full raw operator shell
- Golden Rule authoring
- operator review overlays
- parse failure deep inspection
- full hand-matrix operator internals
- full conviction and timing-stack internals
- QA / regression tooling

## Phase Plan

### Phase 0: Productization Foundation

#### Goal

Freeze the public MVP scope, boundaries, and execution system before writing public-facing product code.

#### Deliverables

- `docs/public_mvp_plan.md`
- `docs/auth_and_access_architecture.md`
- `docs/launch_readiness_checklist.md`
- refreshed `docs/active_task.md`
- refreshed `docs/next_up.md`

#### Acceptance

- public vs operator boundaries are explicit
- auth/access/billing vs canonical truth boundary is explicit
- phase execution order is explicit

#### Handoff packet

- one brief summary of what Phase 1 will implement next
- one report path
- one list of blockers that require user input

### Phase 1: Auth + App Shell

#### Goal

Create the first authenticated shell at `www.onepercentbetter.poker` that can distinguish public visitors, signed-in users, and operator/admin roles.

#### Scope

- login
- signup
- session management
- route protection
- role-aware layout
- placeholder app navigation

#### Out of scope

- upload processing
- billing enforcement
- final public dashboard language

#### Minimum task slices

1. auth provider choice and wiring
2. public/app layout split
3. protected routes
4. basic user profile bootstrap
5. operator/admin role gating

#### Handoff expectation

- exact env vars needed
- exact routes added
- exact auth assumptions made

### Phase 2: Upload Service

#### Goal

Make upload the first real user action.

#### Scope

- upload UI
- packet ingest endpoint
- duplicate guard
- processing states
- upload ownership
- user-visible error states

#### Minimum task slices

1. upload form and storage target
2. upload job creation
3. duplicate detection
4. processing timeline state
5. latest-result linking

#### Handoff expectation

- what succeeds
- what fails safely
- what still requires operator fallback

### Phase 3: Public Interpretation Surfaces

#### Goal

Expose Today / Review / Brain in a public-safe form.

#### Scope

- latest Today
- latest Review
- latest Brain
- selected Pattern Watch cards
- upload-history-to-output connection

#### Minimum task slices

1. dashboard shell
2. Today read surface
3. Review read surface
4. Brain read surface
5. public-safe pattern cards

#### Handoff expectation

- what is public-safe
- what still remains operator-only
- what needs further trust labeling

### Phase 4: Entitlement + Billing

#### Goal

Turn the MVP into a controlled service rather than a free infinite tool.

#### Scope

- subscription plans
- entitlement checks
- usage caps
- account plan view
- gated features

#### Minimum task slices

1. Stripe product/price setup
2. plan table + entitlement model
3. upload caps
4. premium surface gating
5. billing status UI

#### Handoff expectation

- what is free
- what is paid
- what can break account access

### Phase 5: Launch Operations

#### Goal

Make launch survivable.

#### Scope

- logs
- alerts
- backup expectations
- support/admin access
- launch runbook
- beta rollout sequence

#### Minimum task slices

1. production env checklist
2. upload failure monitoring
3. admin support paths
4. limited beta launch protocol
5. rollback / incident notes

#### Handoff expectation

- what to watch daily
- what to do when parsing fails
- what to do when a user reports wrong interpretation

## Minimal-Input Execution Rule

The repo should now optimize for minimal user input and maximum forward motion.

That means each phase should be broken into tasks that:

- have one business question
- can be completed end-to-end in one pass where possible
- include their own validation target
- include one report path
- include one explicit list of assumptions

If a task needs more than one meaningful decision from the user, it is too large and should be split.

## Recommended Immediate Sequence

1. freeze Phase 0 docs
2. choose auth provider
3. implement Phase 1 auth shell
4. wire upload flow
5. expose public Today / Review / Brain
6. only then gate with billing

## First Public Beta Shape

The safest first public beta is:

- private invite only
- limited uploads
- no raw operator shell
- operator review fallback allowed
- explicit post-hoc-only language

That beta should be used to verify:

- upload reliability
- interpretation credibility
- whether users understand Today / Review / Brain
- whether pattern cards feel actionable rather than generic
