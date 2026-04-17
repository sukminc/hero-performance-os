# 049 Conviction Review Operator Report

## TASK

Add a browser-viewable `Conviction Review` tab that automatically surfaces likely overtrust / undertrust / context-sensitive hand classes from the full corpus.

## WHAT I CHANGED

- added `app/api/conviction_review.py`
- refactored `app/api/hand_matrix.py` so hand-class scoring can be reused outside the matrix payload
- wired a new `/api/conviction-review` route in `app/dev_server.py`
- added a new `Conviction Review` tab and panel in `app/ui/index.html`
- added rendering and filter wiring in `app/ui/main.js`
- added minor supporting styles in `app/ui/styles.css`
- updated `docs/current_state.md`
- updated `docs/active_task.md`

## ARCHITECTURE IMPACT

- keeps interpretation deterministic and SQLite-backed
- extends the existing operator shell rather than creating a sidecar analysis path
- reuses the same hand observation truth as `13x13`, which keeps conviction review and matrix detail aligned
- introduces a belief-level review surface without pretending to be solver truth

## DECISIONS MADE

- conviction scoring is based on repeated usage plus realized outcome, not single coolers
- the first release groups findings into:
  - `overtrust`
  - `undertrust`
  - `context_sensitive`
- context-sensitive cards are kept separate so the product does not collapse into "this hand is bad"
- example chips route back into the `Hand Matrix Lab` selection flow for manual drilldown

## RISKS / OPEN QUESTIONS

- current scoring is heuristic, not yet baseline-family + solver calibrated
- high-variance premium hands may still need more de-cooler logic later
- undertrust detection is weaker than overtrust detection because absence/skip behavior is only partially visible from played-hand data
- future iterations should likely add:
  - family-normalized z-scores
  - position-split conviction cards
  - stack-band-specific conviction overlays

## OUT OF SCOPE

- solver integration
- true expected-value engine
- final product card language
- consumer-facing UX polish

## TEST / VALIDATION

- route-level validation via local dev shell payload read
- browser shell integration validation after refreshing the local UI
- no separate automated test file added in this pass

## RECOMMENDED NEXT STEP

Use the new conviction cards to identify 2-3 genuinely suspicious hand classes, then tighten the scoring so those cards can be filtered by position and stack band before adding any solver comparison layer.
