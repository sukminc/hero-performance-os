# Operator Auth Hardening And Handoff Realignment Report

## TASK

Remove `opb_role` as the remaining operator authorization source, make operator-only access resolve through auth-aware viewer context, and realign `active_task` / `next_up` handoff docs to the true current state.

## WHAT I CHANGED

- removed `opb_role` cookie usage from:
  - `frontend/proxy.ts`
  - `frontend/app/auth/dev-login/route.ts`
  - `frontend/app/auth/logout/route.ts`
  - `frontend/app/app/layout.tsx`
- changed `frontend/lib/viewer/session.ts` so dev-mode operator/user simulation derives from the existing `sb-auth-token` dev session value instead of a separate role cookie
- added `frontend/app/operator/layout.tsx` to enforce operator-only access through `getViewerContext()` on the server and redirect non-operators back to `/app`
- updated `docs/active_task.md` so it now points at the next real blocker: canonical ownership truth beyond Hero-first env mapping
- updated `docs/next_up.md` so the follow-on task now starts after that ownership-truth step instead of pointing at work that is already done
- updated `docs/current_state.md` to reflect that operator authorization no longer depends on the old display cookie path

## ARCHITECTURE IMPACT

- operator authorization now follows the same auth-aware viewer-resolution path as the public surface ownership boundary instead of using a weaker cosmetic cookie side-channel
- dev-login remains available, but it now rides on the existing dev session token rather than introducing a separate authorization cookie
- the repo handoff docs now better match the real execution state: viewer ownership hardening is done, operator cookie hardening is done, canonical ownership truth is next

## DECISIONS MADE

- chose server-side viewer-context enforcement for `/operator` rather than trying to do verified Supabase identity checks directly inside `proxy.ts`
- kept `proxy.ts` focused on coarse session gating only
- treated canonical ownership truth as the new active task because the cookie-hardening step is now complete enough to move the baton forward

## RISKS / OPEN QUESTIONS

- `npm run lint` still fails in this frontend because `.next/types/validator.ts` expects `./routes.js`; this appears to be an existing generated-types/tooling issue rather than a regression from this patch
- canonical ownership and operator/admin authorization still rely on env-driven mapping for Hero-first beta use; a durable backend truth record is still needed next
- this change hardens route access, but it does not yet implement a generalized non-Hero provisioning flow

## OUT OF SCOPE

- full canonical ownership schema implementation
- Supabase claims/RBAC rollout
- checkout or entitlement changes
- demo lead capture backend

## TEST / VALIDATION

- `cd frontend && npm run build` ✅
- `cd frontend && npm run lint` ❌ existing generated type error in `.next/types/validator.ts`: `Cannot find module './routes.js'`
- `rg -n "opb_role" frontend docs` confirms runtime/frontend references are removed and only historical/task-doc mentions remain

## RECOMMENDED NEXT STEP

Write the smallest canonical ownership-truth plan: a durable user-to-player ownership record plus a minimal operator/admin authorization record that can replace Hero-first env mapping without weakening the current safe blank-state behavior.
