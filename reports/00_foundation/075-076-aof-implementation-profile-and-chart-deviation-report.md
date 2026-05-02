# TASK

Implement Task 75 and Task 76:

- Task 75: AOF Implementation Profile
- Task 76: AOF Chart Deviation Review

# WHAT I CHANGED

- Added `core/surfaces/aof_implementation_profile.py`.
- Added repository read methods for fetching player hand rows with session context.
- Built a deterministic AOF v1 spot detector for:
  - `<=15bb`
  - `5+` active seats
  - unopened Hero preflop decisions
  - normalized hand class
  - normalized action family
  - format profile
  - simplified baseline action
  - verdict
- Added frontend bridge `getAofImplementationProfile(...)`.
- Added an operator-page AOF section with:
  - total AOF opportunities
  - Hero's jam median stack
  - 12bb hypothesis status
  - 12-15bb danger-zone rates
  - stack breakdown
  - format breakdown
  - repeated pattern cards
- Added `docs/aof_implementation_profile_v1.md`.
- Updated `DECISIONS_LOG.md`.

# ARCHITECTURE IMPACT

AOF now exists as a real product surface, not just a report or chat interpretation.

The layer remains deterministic and inspectable:

- raw hands remain source truth,
- AOF spots are derived read-model truth,
- baseline verdicts are v1 heuristics,
- no solver-grade EV claims are made.

# DECISIONS MADE

- Treat `open_jam` and `open_almost_all_in` as separate but both relevant to Hero's AOF implementation.
- Preserve `special_context_defer` for PKO and satellite cases instead of forcing naive chart grading.
- Show stack-depth and format evidence before coaching language.
- Keep verdicts conservative because many positions still parse as `unknown`.

# CURRENT FINDINGS

Current corpus output:

- AOF opportunities: `1691`
- average opportunity stack: `10.63bb`
- median opportunity stack: `11.28bb`
- average jam / near-jam stack: `9.45bb`
- median jam / near-jam stack: `10.08bb`
- Hero `12bb` AOF hypothesis: `supported`
- match rate: `77.8%`
- too tight rate: `1.8%`
- too loose rate: `5.9%`
- awkward raise rate: `1.3%`
- special context defer rate: `12.1%`

Stack breakdown:

- `0-8bb`: `343` spots, jam rate `35.6%`, match rate `71.7%`
- `8-12bb`: `636` spots, jam rate `25.2%`, match rate `78.8%`
- `12-15bb`: `712` spots, jam rate `15.0%`, match rate `79.8%`, too-loose rate `8.4%`

Repeated pattern candidates include:

- `55` in satellite / PKO contexts as `special_context_defer`
- `KJo` as a repeated `too_loose` family
- `A3o` as a repeated satellite-heavy `special_context_defer`
- `KQo` as a repeated `too_loose` family under the v1 baseline

# RISKS / OPEN QUESTIONS

- Position inference is incomplete, so many cards show `position: unknown`.
- The current baseline is intentionally simple and should not be treated as final GTO truth.
- Some hands that look too loose may be valid in late position once position extraction improves.
- Chip-result outcome is not EV; it only shows won/lost/folded context.

# OUT OF SCOPE

- Exact GTO Wizard chart ingestion.
- Exact PKO bounty math.
- Exact satellite / ICM math.
- Facing-open reshove trees.
- Facing-jam calloff trees.
- Automatic memory promotion from AOF verdicts.

# TEST / VALIDATION

- `python3 -m py_compile core/surfaces/aof_implementation_profile.py core/storage/sqlite_repository.py core/storage/postgres_repository.py`
- `npm run typecheck`
- `npm run build`
- Ran the profile against Hero's local corpus and verified `1691` in-scope AOF opportunities.

# RECOMMENDED NEXT STEP

Next two tasks:

1. Improve GG position inference from button/seat metadata so AOF verdicts can become position-aware.
2. Add an operator-approved AOF baseline table for `0-8bb`, `8-12bb`, and `12-15bb` by position and hand class before turning verdicts into durable coaching truth.
