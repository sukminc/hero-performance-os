# Master Plan

## Purpose

This file is the durable big-picture execution map for `Hero Performance OS`.

It exists so future sessions do not need to reconstruct the project from chat history.
If there is any confusion about what matters next, this file wins over vague remembered context.

## Product goal

Reach an operator-grade MVP where Hero can:

1. ingest a session packet,
2. inspect how it parsed,
3. inspect what evidence it generated,
4. inspect what cumulative memory it updated,
5. read the current state of the game,
6. carry 1-3 next-session adjustments,
7. and trust the system enough to use it repeatedly.

## Big tasks

### 1. Repo stability and operating discipline
- keep docs, runbook, and re-entry flow current
- keep one active task at a time
- preserve report-first handoff discipline

### 2. Parsing quality
- improve real GG parsing coverage
- tighten parse quality and failure reporting
- keep zero-hand and partial-parse behavior honest

### 3. Evidence quality
- improve hand-class evidence
- improve style drift evidence
- improve stable strength evidence
- improve field distortion and contamination logic

### 4. Memory quality
- improve memory status transitions
- improve ranking and cumulative confidence
- make repeated vs one-off behavior more believable

### 5. Today usefulness
- improve current-state computation
- improve next-adjustment ranking
- reduce generic output and increase actionability

### 6. Session Lab usefulness
- improve per-session inspection
- make evidence and memory deltas easier to read
- rank more important hands for inspection

### 7. Memory Graph usefulness
- improve cumulative memory grouping
- add clearer trend/direction reading
- prepare for future transition snapshots

### 8. Thin UI shell usability
- make the shell easier to refresh and inspect
- improve empty/error/loading states
- ensure the shell is good enough for regular use

### 9. Operator correction loop
- add correction paths for evidence and memory
- preserve canonical truth while enabling review overlays

### 10. MVP hardening
- broaden smoke coverage
- add more fixtures
- define must-pass acceptance checks

## Current status

Already built:

- V2 storage/schema
- V2 ingest/parsing
- V2 evidence layer
- V2 memory layer
- Today surface
- Command Center read model
- Session Lab read model
- Memory Graph read model
- thin local UI shell
- end-to-end V2 smoke test

## Active execution rule

Only one active task should be in progress at a time.

Supporting docs:

- `docs/active_task.md`
- `docs/next_up.md`
- `docs/current_state.md`
- `docs/runbook.md`

## Near-term sequence

1. Improve parsing quality on real GG-style files
2. Improve evidence quality so surfaces become more believable
3. Tighten Today usefulness
4. Tighten Session Lab and Memory Graph usefulness
5. Add operator correction loop
6. Harden toward MVP acceptance
