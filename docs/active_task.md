# Active Task

## Title

Cleanup after interrupted Claude run with 222 file changes.

## Why this is the active task

Claude stopped after a large working-tree rewrite that mixed useful product/UI work with risky repository hygiene changes.

The working tree included:

- deleted canonical root docs
- deleted live docs and reports
- duplicate archive folders
- a copied `.claude/worktrees` workspace
- useful frontend/operator changes
- useful compact summaries in `STATUS.md` and `DECISIONS.md`

The active job is to preserve useful work while restoring the repo's canonical operating structure.

## Scope

In scope:

- restore canonical docs and report locations
- remove interrupted-agent workspace noise
- keep useful product/UI changes for review
- align `STATUS.md`, `DECISIONS.md`, `docs/current_state.md`, and `docs/next_up.md`
- run smoke/build validation if feasible
- write a report

Out of scope:

- broad product redesign
- discarding useful Claude implementation work
- committing without explicit request
- solving production architecture for SQLite / Python subprocess coupling

## Target outcome

At the end of this task:

- no canonical docs are deleted
- no duplicate `.claude` or `_archive` worktree copies remain
- remaining changes are reviewable implementation/docs changes
- next task is clear

## First files to inspect

- `git status --short`
- `STATUS.md`
- `DECISIONS.md`
- `README.md`
- `docs/README.md`
- `frontend/app/app/`
- `frontend/app/operator/`
- `reports/00_foundation/`

## Validation target

Minimum:

- `python3 tests/v2_smoke_tests.py`
- `python3 tests/legacy_corpus_tests.py`
- `npm run build`

## Completion rule

This task is complete only when:

1. file-change noise is reduced and explained
2. canonical docs are present
3. validation is run or any blocker is reported
4. cleanup report is written
