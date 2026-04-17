# TASK

Replay the full discovered legacy raw GG corpus into the canonical V2 SQLite store and leave the repo in a state that another chat can resume without migration confusion.

# WHAT I CHANGED

- ran full replay of the currently discovered historical raw corpus into:
  - `/Users/chrisyoon/GitHub/opb-poker/data/hero-v2/hero_v2.sqlite3`
- fixed duplicate handling so duplicate archive files are skipped safely by file hash instead of failing the replay
- updated handoff/state/task docs to reflect that full replay is now complete

# ARCHITECTURE IMPACT

- V2 now has a populated canonical local truth store built from the old raw corpus
- duplicate archive trees no longer block full replay
- future work can shift from migration to interpretation on top of a real longitudinal base

# DECISIONS MADE

- treated the currently discovered corpus as the replay target and completed it in full
- preserved raw-replay architecture instead of importing V1 derived summaries
- kept the canonical local truth store as SQLite for cross-chat resumability and zero-server dependency

# RISKS / OPEN QUESTIONS

- the discovered corpus may still grow later if additional raw archives appear in the old repo
- some promoted memory is still sparse relative to the total evidence volume, so interpretation quality still needs product work
- re-running replay is safe but may still take noticeable time because duplicates must still be scanned before skipping

# OUT OF SCOPE

- Review / Brain implementation
- operator correction hooks
- UI changes
- non-local deployment/storage decisions

# TEST / VALIDATION

- `python3 tests/v2_smoke_tests.py`
- `python3 tests/legacy_corpus_tests.py`
- full replay:
  - `PYTHONPATH=. SQLITE_DB_PATH=/Users/chrisyoon/GitHub/opb-poker/data/hero-v2/hero_v2.sqlite3 python3 scripts/backfill_legacy_gg_corpus.py --apply`
- read validation:
  - `PYTHONPATH=. SQLITE_DB_PATH=/Users/chrisyoon/GitHub/opb-poker/data/hero-v2/hero_v2.sqlite3 python3 app/api/command_center.py`
  - `PYTHONPATH=. SQLITE_DB_PATH=/Users/chrisyoon/GitHub/opb-poker/data/hero-v2/hero_v2.sqlite3 python3 app/api/memory_graph.py`

# RECOMMENDED NEXT STEP

Use the replayed 268-session corpus to improve interpretation quality, especially around underperforming hand classes, field distortion persistence, and when watch-stage signals should promote into stronger Today / Review / Brain output.
