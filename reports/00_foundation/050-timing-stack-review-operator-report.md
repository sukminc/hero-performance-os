# 050 Timing Stack Review Operator Report

## TASK

Add a browser-viewable Tournament Timing + Stack Comfort operator view that helps Hero test whether entry timing, bullet state, and preferred stack depth actually produce cleaner decision quality.

## WHAT I CHANGED

- added `app/api/timing_stack_review.py`
- wired a new `/api/timing-stack-review` route in `app/dev_server.py`
- added a new `Timing + Stack` tab and panel in `app/ui/index.html`
- added rendering and filter wiring in `app/ui/main.js`
- updated `docs/current_state.md`
- updated `docs/active_task.md`

## ARCHITECTURE IMPACT

- extends the operator shell with a new deterministic interpretation surface
- reuses canonical hand observations rather than introducing separate parsing logic
- joins stack comfort, AOF leak queue, conviction review, field ecology, and HUD trend into one operator-facing read model
- keeps the product aligned with the goal of testing Hero-specific performance patterns rather than generic poker theory

## DECISIONS MADE

- entry timing is implemented as a deterministic proxy:
  - earliest session for a tournament id = `early`
  - latest session for a tournament id = `late`
  - middle sessions = `mid`
- bullet state is also deterministic:
  - first detected session = `first_bullet`
  - later sessions = `reentry_bullet`
- stack comfort is broken into:
  - `0-15bb`
  - `15-20bb`
  - `20-25bb`
  - `25-30bb`
  - `30-50bb`
  - `50-100bb`
  - `100bb+`
- the first release explicitly exposes the `20-25bb` hypothesis in the summary block

## RISKS / OPEN QUESTIONS

- entry timing is a proxy, not official late-reg truth from GG
- bullet state is based on detected session restarts, so some tournament continuity edge cases may still exist
- AOF leak queue remains heuristic and should later be aligned with the stronger baseline-family tagging work
- stack-band conclusions still use realized outcome, not true EV

## OUT OF SCOPE

- official tournament registration truth
- solver validation
- exact bullet psychology modeling
- consumer-facing UX polish

## TEST / VALIDATION

- local API payload validation against canonical SQLite
- browser-shell rendering validation after dev server restart
- no separate automated test file added in this pass

## RECOMMENDED NEXT STEP

Use the new Timing + Stack view to identify whether `20-25bb` or `25-30bb` is the true operating zone, then add stack-band-specific conviction cards so hands like `A5s` or `98s` can be reviewed in the exact depth where they drift.
