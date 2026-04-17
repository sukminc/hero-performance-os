# TASK

Document how study-worthy spots should be surfaced and identify the first three real repeated spot families from Hero's historical corpus.

# WHAT I CHANGED

- added `docs/study_worthy_spot_output_spec_v1.md`
- documented the required separation between:
  - clear repeated mistakes
  - threshold study spots
  - belief-driven patterns
- preserved three real repeated families already visible in the canonical corpus:
  - `KJo` early / mid under-15bb pressure approval
  - `KQo` early / mid under-15bb pressure approval
  - low `Ax` offsuit under-15bb early pressure family

# ARCHITECTURE IMPACT

- this does not change storage or parsing
- it defines the next deterministic interpretation layer on top of the current operator-grade matrix
- it creates a product rule that repeated decision families outrank raw result outliers

# DECISIONS MADE

- chose honesty over forcing the exact `22 early jam` example into the output
- documented that the current corpus does not strongly repeat that exact pattern yet
- preserved the closest real repeated families that the data actually supports
- treated `KJo` and `KQo` as threshold-plus-belief families rather than naive leak cards
- treated low `Ax` offsuit as a family pattern rather than isolated hand-class anomalies

# RISKS / OPEN QUESTIONS

- the current evidence is still heuristic and operator-grade rather than final baseline-graded output
- this report uses repeated action-family evidence, not a final GTO chart engine
- small-pair early-jam families still need broader family scoring before they should outrank the current three preserved families

# OUT OF SCOPE

- automatic spot-family scoring implementation
- new frontend components
- final product-card copy
- EV engine or all-in adjusted truth

# TEST / VALIDATION

- re-read the canonical SQLite corpus under `<=15bb`
- inspected repeated proactive preflop approvals across `5+` active-seat hands
- confirmed the current corpus supports repeated `KJo`, `KQo`, and low `Ax` offsuit families
- confirmed the exact `22` early-jam example is not yet a strongly repeated current-corpus pattern

# RECOMMENDED NEXT STEP

Implement one deterministic study-worthy queue on top of the current `Hand Matrix Lab` so these three families are shown explicitly with counts, examples, and why-they-matter language.
