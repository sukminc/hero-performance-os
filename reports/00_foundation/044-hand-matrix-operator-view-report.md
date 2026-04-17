# TASK

Implement the first browser-viewable `13x13` operator surface so Hero can inspect hand-class result patterns directly in the local UI shell.

# WHAT I CHANGED

- added a new read-only API at `app/api/hand_matrix.py`
- extended the thin dev shell to serve `/api/hand-matrix`
- added a new `Hand Matrix Lab` tab to the local operator UI
- added filter controls for:
  - window
  - tournament format
  - position
  - stack band
  - minimum active seats
- rendered a clickable `13x13` matrix with:
  - hands played
  - actual `bb net`
  - average `bb` per hand
  - sample-band styling
- added right-side detail surfaces for:
  - selected hand-class summary
  - position breakdown
  - recent hand examples
  - suspicious hands
  - standout hands
- updated current-state and task docs so the repo now reflects that the first `13x13` operator implementation has started

# ARCHITECTURE IMPACT

- this is an operator-first read model layered on top of the canonical SQLite corpus
- it does not mutate canonical truth
- it reconstructs hand-class, position, format tag, active seats, and `bb` outcome directly from stored raw hand blocks when the normalized layer is not yet rich enough
- this keeps the current implementation small while preserving compatibility with a future deterministic derived layer in Postgres

# DECISIONS MADE

- used the existing thin shell instead of creating a separate frontend app
- kept the feature read-only and local-first
- treated `5+` active seats as the default exploratory floor
- defaulted the view to the recent `90d` window because that matches Hero's current review horizon better than lifetime-only output
- included a `selected_hand` detail card because the product direction depends on evidence-backed hand-class interpretation, not only a heatmap
- allowed `UTG+2` to appear when reconstructing 9-max positions rather than forcing an incorrect collapse into the 8-position spec

# RISKS / OPEN QUESTIONS

- current `bb net` is reconstructed from action text and should be treated as operator-grade, not final accounting-grade truth
- the detail panel currently emphasizes actual results, not expected-value delta
- format tagging still uses deterministic string heuristics from tournament names and headers
- the current UI is exploratory and functional, but not yet the final product-card language layer

# OUT OF SCOPE

- solver EV
- expected-value baselines
- all-in adjusted EV
- HUD trend integration
- AOF overlay integration
- consumer-facing frontend polish

# TEST / VALIDATION

- exercised the new API directly via local command-line payload generation
- verified the dev server route wiring
- verified the browser shell can request and render the new payload structure
- kept the implementation read-only against the canonical SQLite store

# RECOMMENDED NEXT STEP

Use this operator view to identify the first high-signal hand-class cards worth formalizing, then add one deterministic study-card layer on top of this matrix instead of broadening UI scope first.
