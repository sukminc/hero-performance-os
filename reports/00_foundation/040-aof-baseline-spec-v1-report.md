# TASK

Write the first AOF baseline spec before implementation.

# WHAT I CHANGED

- Added [docs/aof_baseline_spec_v1.md](/Users/chrisyoon/GitHub/hero-performance-os/docs/aof_baseline_spec_v1.md)
- Defined AOF v1 around:
  - `effective_stack_bb <= 15`
  - `active_seat_count >= 5`
  - Hero unopened preflop spots only
  - tournament-format-aware baseline profiles
  - action families of `fold`, `open_raise_small`, `open_jam`, and `open_almost_all_in`
- Defined the first verdict set:
  - `match`
  - `too_tight`
  - `too_loose`
  - `awkward_raise`
  - `intentional_pressure_sizing`
  - `special_context_defer`
  - `mixed`
  - `excluded`
- Defined the first operator-facing numeric outputs for AOF scoring and action-shape tracking.
- Revised the spec to reflect Hero's clarification that:
  - PKO, standard MTT, and satellite baselines cannot be treated as one chart
  - near-jam opens are not auto-fails
  - some near-jam actions are intentional pressure-sizing structures

# ARCHITECTURE IMPACT

- No code or schema changes.
- This creates the first stable implementation contract for AOF work.
- It narrows the product from broad interpretation to a concrete, measurable tournament fundamental.
- It also prevents naive chart grading from mislabeling format-aware or intentional deviations as mistakes.

# DECISIONS MADE

- AOF v1 is preflop-only.
- AOF v1 is limited to `15bb` or lower.
- AOF v1 excludes short-handed exceptions below 5 active seats.
- AOF v1 begins with unopened Hero decision spots rather than reshove/calloff trees.
- AOF v1 should favor readable action-family judgment over fake exactness.
- AOF v1 must be format-aware across:
  - `standard_mtt`
  - `pko`
  - `satellite`
- `open_almost_all_in` is a required category, but it is not auto-fail.
- Near-jam deviations must separate:
  - true awkward raises
  - intentional pressure sizing
  - special-context deferred spots

# RISKS / OPEN QUESTIONS

- The exact baseline source is still open and must be fixed before implementation.
- Position mapping may be incomplete in some parsed hands and should not be guessed aggressively.
- Exact tournament/PKO/ICM pressure is intentionally excluded from v1, which means the first pass will be structurally useful but not context-perfect.
- Tournament-format tagging must be reliable enough before implementation or grading quality will drift.

# OUT OF SCOPE

- No code implementation
- No parser updates
- No DB schema updates
- No postflop logic
- No reshove or calloff tree implementation yet

# TEST / VALIDATION

- No tests run because this task intentionally avoided code changes.
- The spec was grounded against the current canonical SQLite corpus and current parsed hand structure.

# RECOMMENDED NEXT STEP

Implement the deterministic AOF spot detector for unopened Hero preflop decisions under `15bb` with `5+` active seats, then surface:

- opportunity count
- match rate
- too tight / too loose / awkward raise rates
- intentional pressure sizing and deferred-context rates
- position and hand-class breakdowns
- broken out by `standard_mtt`, `pko`, and `satellite` profiles

# HANDOFF

- The AOF implementation target is now explicitly documented in [docs/aof_baseline_spec_v1.md](/Users/chrisyoon/GitHub/hero-performance-os/docs/aof_baseline_spec_v1.md).
- Do not start with reshove/calloff trees.
- Start with unopened Hero spots only.
- Keep the first implementation numeric and deterministic.
- Do not auto-grade all near-jam opens as mistakes.
- Respect tournament format differences from the first implementation.
