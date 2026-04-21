# TASK

Restore Hero corpus visibility inside the public shell and upgrade the public uploader so Hero can drop in large post-cutoff GG packet dumps as `.zip` or multi-file batches.

# WHAT I CHANGED

- restored the current repo canonical SQLite from the archived Hero corpus so the public shell reads real historical data again
- added upload coverage summary reads so the public upload page shows:
  - total sessions
  - total hands
  - memory item count
  - first / last session date
  - latest ingest timestamps and filenames
- upgraded the public upload action from single-file `.txt` only to:
  - multiple `.txt` files
  - one or more `.zip` files
  - mixed batch intake
- added `core/ingest/zip_expand.py` so zip expansion uses deterministic Python stdlib behavior with no new package dependency
- upgraded the upload UI into a larger dropbox-style intake card with batch summary and per-source result inspection
- reclassified summary-only tournament exports so zero-hand placement recap files do not appear as parser failures

# ARCHITECTURE IMPACT

- the public shell now points at the same local canonical SQLite file as the restored Hero corpus in this repo
- zip handling stays outside canonical truth: archives are expanded into temp upload space, then each `.txt` packet is ingested through the same duplicate-safe ingest path
- no ingest truth rules changed; batch upload is only a wider intake wrapper around the existing ingest entrypoint

# DECISIONS MADE

- restore the archived Hero corpus into the current repo rather than leaving the public shell attached to an empty placeholder DB
- use Python `zipfile` instead of adding a frontend unzip dependency
- keep batch processing synchronous for local MVP usefulness rather than introducing queueing before the core intake path is trustworthy

# RISKS / OPEN QUESTIONS

- large zip batches are still processed inline; very large dumps may need background jobs later
- current upload UI is “large intake” but not yet full drag-and-drop event polish
- multi-user auth-to-player isolation is still not hardened; this task restores Hero-first usefulness, not final access control
- mixed GG exports can still bundle real hand packets together with tournament recap files, so batch results should continue showing both ingested and summary-only skipped counts

# OUT OF SCOPE

- cloud object storage
- queue workers
- final multi-tenant security model
- post-upload automatic refresh orchestration across all public surfaces

# TEST / VALIDATION

- restored DB verified locally:
  - `368` sessions
  - `18,442` hands
  - `34` memory items
  - session range `2025/12/30 19:41:13` through `2026/03/29 15:33:59`
- verified latest ingest timestamps exist in canonical store
- batch upload code path validated through TypeScript build next

# RECOMMENDED NEXT STEP

Run one real post-cutoff upload batch through the new public uploader, then verify that Today / Review / Brain and operator surfaces all reflect the newly extended corpus consistently.
