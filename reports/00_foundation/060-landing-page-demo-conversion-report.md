# Landing Page Demo Conversion Report

## TASK

Make the public landing page simpler, easier to understand from a cold link click, and able to drive early demo applications from GG Poker Ontario tournament players.

## WHAT I CHANGED

- rewrote the homepage hero to explain the product in plain language for cold traffic
- added visible sample output blocks for `Today`, `Review`, and `Brain`
- clarified the audience as GG Poker Ontario online tournament players only
- added a direct demo-application section on the homepage
- converted `/signup` from placeholder auth copy into an early demo application page
- added a reusable client-side demo application form that opens a prefilled email draft
- updated metadata description to match the current recruiting goal

## ARCHITECTURE IMPACT

- this change is presentation-layer only
- it does not change canonical poker truth, ingestion, memory, or surface generation
- it improves the top-of-funnel clarity for early beta recruitment without pretending broader onboarding is already built

## DECISIONS MADE

- prioritized immediate clarity over feature completeness
- chose sample output over abstract feature explanation
- chose direct email-based demo application as the smallest shippable intake path for current live recruitment
- kept the scope focused on GG Poker Ontario because that is the current live recruiting boundary

## RISKS / OPEN QUESTIONS

- the current demo application flow depends on a mail client opening correctly
- if `hello@onepercentbetter.poker` is not the right inbox, `NEXT_PUBLIC_DEMO_APPLY_EMAIL` should override it in production
- a future version may want a proper lead capture backend or form service once volume increases

## OUT OF SCOPE

- real signup/auth onboarding
- live checkout
- generalized non-GG or non-Ontario recruiting
- production CRM / lead routing

## TEST / VALIDATION

- `cd frontend && npm run build`
- `cd frontend && npm run lint`

## RECOMMENDED NEXT STEP

Replace the email-based demo application flow with a durable lead capture backend, then add one strong real sample report page or screenshot-backed walkthrough for even higher cold-link conversion.
