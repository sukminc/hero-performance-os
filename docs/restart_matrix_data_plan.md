# Matrix Data Restart Plan

## Current Phase

Research and data-processing phase.

The goal is not to produce deep analytics yet. The goal is to make sure user
dumped files become a clean, deduplicated, cumulative, processable dataset.

## Product Loop

```text
dump files -> preserve raw source -> classify input -> expand archives -> parse text hands
-> dedupe files/hands -> append new hands -> update cumulative counts -> rebuild Matrix dataset
```

## Why This Matters

GG Poker hand histories are only exportable for a limited window. OPB's first
value is preserving the user's personal poker record before it disappears.

If the data corpus grows cleanly, later analytics become possible. If the data
corpus is messy, duplicate-heavy, or lossy, later analytics will not be trusted.

## MVP Cut Line

Build only enough to prove:

- source files are preserved,
- text/zip/image inputs are classified,
- zip contents are expanded safely,
- duplicate files are skipped,
- duplicate hands are skipped,
- extracted hands are appended,
- cumulative counters increase correctly,
- 13x13 Matrix source data can be rebuilt from the processed hands.

## Explicitly Later

- hand advice,
- leak interpretation,
- Today / Review / Brain,
- solver comparison,
- AOF coaching,
- public polish,
- role-model or coach overlays.

## Next Implementation Slice

Create a small ingestion ledger around the current preserved data:

- raw file manifest,
- dump id,
- file hash,
- input kind,
- processing status,
- extracted hand count,
- duplicate hand count,
- created normalized hand ids.

This should be deterministic and inspectable before any interpretation layer is
reintroduced.
