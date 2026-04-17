# Auth And Access Architecture

## Objective

Define how public app authentication, account access, billing, and operator roles can exist without corrupting canonical poker truth.

## Core Rule

Authentication and access control may be managed by a hosted edge system.
Canonical poker truth must remain separate.

Auth answers:

- who is the user?
- are they signed in?
- what can they access?
- what plan are they on?

Canonical poker truth answers:

- what player memory exists?
- what uploads belong to which player identity?
- what Today / Review / Brain outputs are true?
- what cumulative interpretation exists?

## Entity Model

### User

Represents the authenticated human account.

Examples:

- email
- auth provider id
- status
- plan
- created at

### Player

Represents a poker identity / performance model.

Examples:

- hero player id
- screen-name aliases
- site/source metadata
- primary interpretation profile

### User Player Access

Represents which authenticated users may access which player models.

Examples:

- owner
- coach
- operator/admin reviewer

### Upload

Represents one uploaded GG session packet owned by a user and linked to a player.

### Processing Job

Represents the backend ingestion / parse / derive workflow for an upload.

## Access Layers

### Public

- landing
- pricing
- login
- signup

### Authenticated user

- upload
- dashboard
- Today
- Review
- Brain
- upload history
- account

### Operator/Admin

- everything user can see
- operator shell
- QA tools
- parse inspection
- correction overlays
- Golden Rule tools

## Recommended First Implementation

### Auth provider

Choose one:

- Supabase Auth
- Clerk

Selection criteria:

- fast setup
- route protection
- session handling
- low-maintenance production path

### Recommended initial access tables

- `users`
- `players`
- `user_player_access`
- `uploads`
- `processing_jobs`
- `subscription_status`

## Trust Boundary

### Hosted edge system may own

- auth identity
- session cookies
- password or magic-link flow
- subscription/customer ids
- access gating

### Canonical poker backend must own

- parsed hands
- evidence
- memory
- derived interpretation
- Today / Review / Brain
- operator review overlays

## Routing Model

### Public routes

- `/`
- `/login`
- `/signup`
- `/pricing`

### Protected routes

- `/app`
- `/app/upload`
- `/app/today`
- `/app/review`
- `/app/brain`
- `/app/account`

### Operator routes

- `/operator`
- `/operator/uploads`
- `/operator/review`
- `/operator/golden-rules`

Operator routes must require explicit role checks.

## Entitlement Model

Entitlement should not be inferred from frontend state.

Minimum entitlement checks:

- can upload?
- upload limit reached?
- can access historical review?
- can access premium pattern surfaces?
- can access operator routes?

## Minimal-Input Principle

The user should not have to repeatedly explain identity mapping or plan state.

The system should:

- auto-link the primary player where possible
- preserve account state across sessions
- preserve upload ownership automatically
- require operator-only intervention only when identity mapping is ambiguous

## Phase Decisions Still Needed

### Decision 1

Pick the auth provider.

### Decision 2

Decide whether the first public beta is:

- single-player only
- or multi-user from day one

### Decision 3

Decide whether operator/admin lives:

- in the same app with role checks
- or in a separate protected surface

## Recommended Default

If minimizing input and maximizing progress is the goal:

- use one auth provider only
- support one player per user initially
- keep operator/admin in the same deployed app but behind strict role gating
- defer coach / shared access until after first public beta
