# TASK
Move the OPB MVP beyond local-only operation and deploy the current frontend to production for `www.onepercentbetter.poker`.

# WHAT I CHANGED
- Added a production upload service boundary:
  - Frontend uploads now call `OPB_BACKEND_BASE_URL` when configured.
  - Production upload attempts fail clearly when backend service configuration is missing.
  - Python backend service now exposes `POST /v1/players/{player_id}/uploads` for `.txt` and `.zip` GG packet ingestion.
- Added production fallback guardrails:
  - `OPB_REQUIRE_BACKEND_SERVICE=1` disables local Python fallback from the Next.js frontend.
  - Upload status/viewer lookup paths avoid local subprocess reads when production backend service mode is required.
- Added Vercel deployment hygiene:
  - `.vercelignore` excludes local data, build artifacts, `node_modules`, and Vercel metadata from upload.
  - `.gitignore` ignores Vercel project metadata.
  - `.env.example` documents backend service env vars.
- Patched the existing Vercel project `one-percent-better-poker-site` to use the Next.js framework and redeployed production.

# ARCHITECTURE IMPACT
- This keeps the MVP aligned with the service-boundary decision: Vercel frontend must not rely on local SQLite/Python subprocesses in production.
- Upload is now shaped for live service ingestion instead of local-only filesystem ingestion.
- The frontend is live, but full live user upload-to-Matrix requires a reachable backend URL and canonical storage behind `OPB_BACKEND_BASE_URL`.

# DECISIONS MADE
- Use the existing `one-percent-better-poker-site` Vercel project because it owns `onepercentbetter.poker`.
- Keep `OPB_REQUIRE_BACKEND_SERVICE=1` enabled in production so broken backend configuration fails honestly instead of pretending local data exists.
- Alias the successful production deployment to both `onepercentbetter.poker` and `www.onepercentbetter.poker`.

# RISKS / OPEN QUESTIONS
- `OPB_BACKEND_BASE_URL` is not configured yet, so live upload/Matrix data activation is intentionally blocked until the backend service is deployed.
- The backend upload route currently supports the stdlib Python service boundary; it still needs a managed production runtime and Postgres connection.
- New user ownership/provisioning still needs a production path beyond env/manual mapping.

# OUT OF SCOPE
- Deploying the Python backend runtime.
- Provisioning managed Postgres and migrating Hero/local data into it.
- Stripe membership gating and upload limits.
- Consumer onboarding copy polish beyond the existing app surfaces.

# TEST / VALIDATION
- `python3 tests/service_boundary_tests.py` passed.
- `npm run build` passed locally.
- Vercel production deploy succeeded:
  - Deployment: `one-percent-better-poker-site-bmuusk99o-sukmincs-projects.vercel.app`
  - Vercel status: `Ready`
  - Alias confirmed: `www.onepercentbetter.poker`

# RECOMMENDED NEXT STEP
Deploy the Python backend service with `V2_STORAGE_BACKEND=postgres`, `DATABASE_URL`, and `OPB_BACKEND_API_TOKEN`, then set `OPB_BACKEND_BASE_URL` on the Vercel frontend production project.
