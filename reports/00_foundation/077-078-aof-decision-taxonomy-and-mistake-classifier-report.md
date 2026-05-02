# TASK

Implement Task 77 and Task 78:

- Task 77: AOF Situation Taxonomy + Detector
- Task 78: AOF Mistake vs Cooler Classifier

# WHAT I CHANGED

- Added `core/surfaces/aof_decision_system.py`.
- Added AOF v2 short-stack situation taxonomy:
  - `unopened_open_decision`
  - `premium_induce_candidate`
  - `facing_open_decision`
  - `facing_open_reshove`
  - `facing_jam_calloff`
  - `multiway_after_open`
  - `multiway_all_in_decision`
  - `other_short_stack_decision`
- Added decision quality buckets:
  - `standard`
  - `mistake_candidate`
  - `non_mistake`
  - `operator_defer`
- Added mistake family classification:
  - `too_wide_open_jam_12_15bb`
  - `premium_missed_induce`
  - `too_tight_premium_fold`
  - `too_wide_reshove`
  - `bad_calloff_candidate`
  - `satellite_survival_violation`
  - `multiway_overcommit`
  - `too_tight_monster_fold`
- Added `getAofDecisionSystem(...)` frontend bridge.
- Added AOF Decision System v2 section to `/operator`.
- Added `docs/aof_decision_system_v2.md`.
- Updated `DECISIONS_LOG.md`.

# ARCHITECTURE IMPACT

AOF is now moving from chart-adjacent reporting into a true short-stack decision system.

The key architectural change is separation of:

- decision context,
- hand selection,
- action family,
- result/cooler/runout,
- mistake candidate,
- operator-defer context.

This prevents the product from turning standard lost all-ins into false coaching while still surfacing repeated GTO/baseline deviations.

# DECISIONS MADE

- Losing with a premium or standard calloff is protected as `non_mistake` unless the decision family itself is suspect.
- PKO, satellite, and multiway contexts are often `operator_defer` instead of hard-graded.
- `AA/KK` at `12-15bb` can be treated as a `premium_induce_candidate`; open-jamming monsters in that band can become `premium_missed_induce`.
- Mistake cards are grouped by mistake family + hand class rather than by one-off hand result.

# CURRENT FINDINGS

Current local Hero corpus:

- short-stack decisions: `3721`
- mistake candidates: `75`
- mistake candidate rate: `2.0%`
- non-mistake protected examples: `467`
- operator-defer spots: `1418`
- standard spots: `1761`
- cooler protection examples surfaced: `20`

Situation counts:

- `unopened_open_decision`: `1680`
- `facing_open_decision`: `736`
- `facing_jam_calloff`: `358`
- `multiway_after_open`: `258`
- `multiway_all_in_decision`: `149`
- `facing_open_reshove`: `147`
- `premium_induce_candidate`: `11`
- `other_short_stack_decision`: `382`

Top mistake candidates:

- `multiway_overcommit` with `QTo`
- `bad_calloff_candidate` with `AJo`
- `multiway_overcommit` with `KJo`
- `satellite_survival_violation` with `66`
- `too_wide_open_jam_12_15bb` with `KJo`

# RISKS / OPEN QUESTIONS

- This is still a deterministic v2 baseline, not exact GTO Wizard truth.
- Position inference is still incomplete.
- Opener position, opener stack, bounty cover/covered geometry, and table ICM are not fully modeled yet.
- `operator_defer` is intentionally high because the engine is avoiding fake certainty in PKO/satellite/multiway spots.

# OUT OF SCOPE

- Exact solver chart ingestion.
- Exact PKO bounty EV.
- Exact satellite ICM.
- Automatic Today/Brain memory promotion from mistake cards.
- Full hand replayer.

# TEST / VALIDATION

- `python3 -m py_compile core/surfaces/aof_decision_system.py core/surfaces/aof_implementation_profile.py`
- `npm run typecheck`
- `npm run build`
- Ran AOF v2 against Hero local corpus and verified `3721` short-stack decisions with mistake/cooler separation.

# RECOMMENDED NEXT STEP

Next two tasks:

1. Improve position and opener-position inference from GG seat/button metadata.
2. Add an operator-approved baseline table for v2 situations so mistake families can graduate from heuristic candidates to approved correction truth.
