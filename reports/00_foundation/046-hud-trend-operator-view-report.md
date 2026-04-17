# TASK

Prototype a browser-viewable HUD trend operator surface that shows tournament-by-tournament changes with legend-backed interpretation.

# WHAT I CHANGED

- added a new read-only API at `app/api/hud_trend.py`
- added a new `HUD Trend` tab to the local operator shell
- implemented tournament-level aggregation for:
  - `VPIP`
  - `PFR`
  - `ATS`
  - `3BET`
  - `Flop CB`
  - `Turn CB`
  - `River Agg`
  - `WTSD`
  - `W$SD`
- added a metric legend so the surface explains what each number means
- added simple sparkline trend rendering for recent tournaments
- added interpretation text for each metric, with explicit emphasis on river passivity

# ARCHITECTURE IMPACT

- the new HUD trend surface is read-only and local-first
- it re-derives tournament-level metrics from stored raw hand blocks instead of depending on a precomputed HUD table
- this keeps the implementation compatible with future canonical derived layers without blocking operator exploration today

# DECISIONS MADE

- used tournament-level aggregates instead of only lifetime HUD values so change can be felt
- prioritized metrics that can be derived deterministically enough from current raw hand text
- used recent-window average vs previous-window average deltas to show meaningful movement
- made river aggression a first-class interpreted metric because that is one of Hero's explicit concerns

# RISKS / OPEN QUESTIONS

- current HUD metrics are operator-grade heuristics, not a final commercial HUD engine
- `Flop CB` and `Turn CB` are currently inferred from initiative and action order, not a full solver-precise state engine
- a future version may want stake, format, and field-strength splits directly inside HUD trend

# OUT OF SCOPE

- full commercial Smart HUD parity
- advanced line charts
- final design polish
- longitudinal win-rate or ROI overlays

# TEST / VALIDATION

- compiled the new API and server modules
- validated payload generation against canonical SQLite
- integrated the new route into the local UI shell
- verified the UI markup exposes the new HUD Trend panel and controls

# RECOMMENDED NEXT STEP

Add format-specific HUD split views and a direct `why river still feels passive` breakdown so Hero can see whether the change is real in PKO, satellite, and standard MTT separately.
