# 055 Billing And Entitlement Foundation Report

## TASK

Add billing and entitlement foundation to the public MVP shell.

## WHAT I CHANGED

- added billing plan definitions in `frontend/lib/billing/plans.ts`
- added account entitlement helpers in `frontend/lib/billing/account.ts`
- added Stripe billing config scaffold in `frontend/lib/billing/stripe.ts`
- expanded `frontend/.env.example` with Stripe env vars
- upgraded `/pricing` to render the first plan model
- upgraded `/app/account` to render plan state and billing configuration readiness
- added free-vs-paid explanatory gating copy to `/app/review` and `/app/brain`
- updated phase docs to point next at launch operations

## ARCHITECTURE IMPACT

- establishes the first product boundary between free access and paid value
- keeps billing as a separate app concern from canonical poker interpretation truth
- prepares the public shell for later checkout/webhook wiring without requiring it yet

## DECISIONS MADE

- Stripe is the chosen billing provider
- first plan model uses:
  - `free_beta`
  - `pro_monthly`
- compact Today / Review / Brain remain visible on free access
- deeper review/brain/pattern value is reserved for paid entitlement

## RISKS / OPEN QUESTIONS

- live checkout is not wired
- plan state currently defaults from cookie/local foundation logic rather than persistent billing truth
- exact pricing strategy may still change before beta launch
- upload limits are defined but not yet enforced in runtime

## OUT OF SCOPE

- Stripe checkout
- webhook ingestion
- subscription persistence
- launch operations

## TEST / VALIDATION

- `npm run build` passed in `frontend/`
- pricing and account routes compile
- entitlement helpers compile

## RECOMMENDED NEXT STEP

Add launch operations foundation so the public MVP can be run as a limited beta with clear support and failure-handling discipline.
