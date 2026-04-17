# V2 Independent Repo Cutover

## Why split V2 into its own repo

V2 is now conceptually different enough from V1 that it should be treated as an independent product codebase.

Reasons:

- V1 is a valuable historical/research base
- V2 has a narrower and cleaner architecture
- mixing both in one active repo increases confusion
- future work should not require re-orienting through legacy structure every time

The split should happen in a way that preserves V1 history while making V2 easier to run, understand, and continue.

## Cutover principle

The new repo should contain:

- only the active V2 product
- only the docs needed to continue V2
- only the tests and fixtures needed to trust V2

The old repo should remain as:

- V1 archive
- migration reference
- historical context base

## What moves to the new repo first

### Required code

- `core/`
- `app/`
- `tests/v2_smoke_tests.py`

### Required docs

- `docs/v2/README.md`
- `docs/v2/reentry_start_here.md`
- `docs/v2/product_principles.md`
- `docs/v2/architecture.md`
- `docs/v2/mvp_big_steps.md`
- `docs/v2/independent_repo_cutover.md`
- `docs/v2/migration_plan.md`
- `docs/v2/module_map.md`

### Required fixtures

- `fixtures/gg_session_sample.txt`
- `fixtures/gg_session_empty.txt`

### Required top-level context

- a new V2 README
- a minimal AGENTS or contributor guide for V2
- a run/test quickstart

## What does not need to move immediately

- legacy `operator/`
- legacy `runtime/`
- legacy `frontend/`
- legacy `ingestion/`
- legacy `actions/`
- legacy `context/`
- the full historical `reports/` tree

Those remain reference material in the old repo unless a specific file is still needed by active V2 code.

## Recommended cutover sequence

### Step 1. Stabilize current V2 in this repo

Before the split:

- keep the smoke test green
- finish the first thin UI shell or enough app entrypoints to prove the shape
- make sure docs explain the system without chat replay

### Step 2. Create the new repo with only V2 active assets

Initial folder target:

```text
repo-root/
  README.md
  AGENTS.md
  core/
  app/
  tests/
  fixtures/
  docs/
```

### Step 3. Copy, do not over-migrate

Bring only what V2 currently executes or needs to explain itself.
Do not drag the entire old repo forward.

### Step 4. Re-run smoke tests in the new repo

The split is not done until:

- imports resolve
- fixtures load
- `tests/v2_smoke_tests.py` passes

### Step 5. Mark the old repo clearly

Add a clear note that:

- V1 lives here
- V2 moved there
- this repo remains the archive/reference base

## Backdating / continuity rule

The new repo should always be understandable by someone reopening it later.

That means each major step should leave behind:

1. one current-state summary
2. one next-step summary
3. one report for the step just completed

Recommended minimum docs to keep current:

- `README.md`
- `docs/reentry_start_here.md`
- `docs/current_state.md`
- `docs/mvp_big_steps.md`

## Definition of a good cutover

A good V2 repo split means:

- Hero can open the repo later and immediately know what it is
- the next implementation step is obvious
- the smoke test still passes
- the repo no longer depends on remembering the whole V1 story
