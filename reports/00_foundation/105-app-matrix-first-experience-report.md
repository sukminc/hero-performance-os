# Task 105: App Matrix First Experience

## TASK

Make the Matrix the first product experience for authenticated users so the user flow becomes: sign up -> upload hand histories -> see personal preflop Matrix and interpretation.

## WHAT I CHANGED

- Added `/app/matrix` as the authenticated user-facing Matrix page.
- Changed `/app` to redirect to `/app/matrix`.
- Updated authenticated navigation so `Matrix` is the first item.
- Added a post-upload `View your Matrix` CTA.
- Revalidated `/app/matrix` after successful upload.
- Updated app sidebar copy to explain the product around upload -> Matrix.
- Reused the existing Matrix payload so the page remains per-player through `viewer.playerId`.

## ARCHITECTURE IMPACT

This moves the Matrix from operator-only inspection toward the primary user value surface without changing canonical truth.

The user-facing Matrix reads from the authenticated player's resolved `playerId`. It does not introduce a new multi-user model; it uses the existing player ownership mapping and upload pipeline.

## DECISIONS MADE

- The first product value is the personal Matrix, not Today/Brain/Quiz.
- `/operator/matrix` remains available for operator depth.
- `/app/matrix` becomes the standard user view.
- Upload success should send the user back to Matrix rather than leaving them in raw ingest details.

## RISKS / OPEN QUESTIONS

- The user-facing Matrix currently duplicates some operator Matrix markup. A follow-up should extract a shared Matrix surface component.
- Unmapped users still need provisioning before their Matrix can populate.
- This is still local/backend-first productization, not a full billing or account-isolation launch.

## OUT OF SCOPE

- No Stripe checkout.
- No membership/upload limit enforcement.
- No new canonical multi-tenant schema.
- No public marketing redesign.

## TEST / VALIDATION

- `npm run build` should include `/app/matrix`.

## RECOMMENDED NEXT STEP

Extract the duplicated Matrix page layout into a shared component and then tighten the upload success screen around a single action: `View your Matrix`.
