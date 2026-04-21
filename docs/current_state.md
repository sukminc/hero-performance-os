# Current State

## What this repo is

This is the standalone V2 repo for Hero Performance OS.

It already includes:

- ingest -> evidence -> memory -> surfaces
- Today / Command Center / Session Lab / Memory Graph read models
- thin local UI shell
- end-to-end smoke test

## What is true right now

- V2 is independent enough to continue without replaying the V1 repo history
- V2 is still operator-grade and local-first
- V2 is not yet a polished shipped product
- V2 now has a thin UI shell on top of Command Center / Session Lab / Memory Graph
- V2 has an executable smoke test that covers ingest -> evidence -> memory -> surfaces
- V2 can now inventory and backfill the legacy local GG hand-history corpus from the old repo without relying on Supabase
- the canonical local V2 store should now be treated as the SQLite file in this repo's `data/hero_v2.sqlite3`, which after local repo rebasing will live at `/Users/chrisyoon/GitHub/opb-poker/data/hero_v2.sqlite3`
- the full currently discovered legacy raw corpus replay has been completed into the canonical SQLite store

## Current active task

The current active task is:

- freeze the public MVP planning layer and rebase execution around productization-first phases

See:

- `docs/active_task.md`
- `docs/next_up.md`

## Next major objective

Use this repo to tighten the actual usefulness of the system:

1. improve parsing quality
2. improve evidence quality
3. improve memory ranking and state logic
4. tighten Today usefulness
5. refine Session Lab and Memory Graph
6. only then deepen Review / Brain and broader productization

## What changed most recently

- real-style GG parser coverage improved
- parse quality now distinguishes real parser success from simplified fixture fallback
- smoke coverage now includes a stronger real-style GG fixture path
- evidence quality is now more conservative on tiny samples and more explicit about positive execution discipline
- memory promotion now depends more on repetition, and Today ignores watch-stage noise for direct adjustments
- Today now surfaces fewer, clearer pre-session actions with more specific state headlines
- Session Lab and Memory Graph now expose direction/maturity-oriented inspection summaries for operator review
- Command Center, Session Lab, and Memory Graph now expose structured interpretation groundwork readiness for future Review / Brain assembly
- Command Center and Memory Graph now expose explicit cumulative interpretation summary blocks grounded in the replayed canonical SQLite corpus
- Command Center, Session Lab, and Memory Graph now expose explicit operator review hooks, and read-only canonical SQLite reads are safe again
- the first reviewed overlay path now exists on top of canonical interpretation emphasis without mutating source truth
- the next priority is making repeated patterns and correction progress more explicit than reviewed overlay mechanics
- Hero has now clarified that the first concrete strategic scoring layer should be AOF under `15bb`
- Hero has also clarified that AOF must be format-aware across standard MTT, PKO, and satellite contexts
- near-jam opens must not be auto-graded as mistakes because some are intentional pressure-sizing structures
- the next concrete product surface is a `13x13` hand-class / result analysis layer
- online seat-by-seat ante structures mean garbage-hand negativity must not be auto-read as a leak
- the first browser-viewable `13x13` operator implementation is now underway on top of the thin local shell
- the next interpretation layer is now defined as a study-worthy spot output that must separate repeated mistakes, threshold spots, and belief-driven patterns
- a first browser-viewable HUD trend operator surface now exists with tournament-level metric trend, legend, and interpretation groundwork
- a first browser-viewable Conviction Review surface now exists to rank likely overtrust / undertrust / context-sensitive hand classes across the corpus
- a first browser-viewable Tournament Timing + Stack Comfort operator surface now exists to test entry timing, bullet proxy, stack-band comfort, AOF leak queue, conviction pressure, and field/HUD context together
- legacy-corpus discovery and backfill tooling now exists so the old local GG archive can be reused directly
- a canonical local SQLite path is now fixed for V2 backfill work and a first 100-file historical batch has already been ingested successfully
- the full discovered-corpus replay now yields 368 unique sessions, 18,442 hands, 1,039 evidence rows, and 34 cumulative memory items
- the next repo-level move is to treat this V2 repo as the continuing `opb-poker` codebase rather than a sidecar experiment
- a first public-app `frontend/` shell now exists with landing, login, signup, pricing, protected `/app` routes, and operator-gated route foundation
- Supabase Auth has now been chosen as the Phase 1 auth provider for the public MVP shell
- the first public upload foundation now exists on `/app/upload`, with GG `.txt` packet submission, duplicate-safe ingest invocation, and latest upload status inspection
- the first public-safe Today / Review / Brain pages now read canonical outputs through a thin frontend layer without exposing the full operator shell
- Stripe has now been chosen as the Phase 4 billing provider, and the first pricing/account/entitlement foundation now exists in the public shell
- launch operations foundation docs now exist for production env, support flow, rollback discipline, and private beta gating
- the public upload shell now points back at the restored Hero canonical corpus and exposes the real current cutoff date before new batch intake
- the public uploader now supports large multi-file intake and zip expansion so post-cutoff GG packet dumps can be loaded in one batch
- summary-only GG tournament export files are now classified as skipped summary artifacts rather than hard ingest failures
- the public shell viewer scope is no longer hardcoded to Hero; auth identity now has to map to an allowed player scope before Today / Review / Brain / dashboard data resolves
- unmapped authenticated users now get safe blank states instead of silently reading Hero data through the public shell
- the public landing page now explains the product in cold-traffic language, shows sample Today / Review / Brain output, and lets GG Poker Ontario players apply for demo access immediately

## Core active areas

- `core/`
- `app/`
- `tests/v2_smoke_tests.py`
- `docs/v2/`
- `docs/active_task.md`
