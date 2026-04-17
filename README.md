# Hero Performance OS

Hero Performance OS is a personal poker performance system built to improve decision quality, track drift, separate field distortion from contamination, and generate the next best adjustment before the next session.

This repository is the standalone V2 codebase. It is focused on one high-signal operator-grade user flow first, not broad consumer productization.

## What exists now

- V2 storage/schema
- V2 ingest/parsing
- V2 evidence generation
- V2 cumulative memory updates
- Today surface generation and read path
- Command Center read model
- Session Lab read model
- Memory Graph read model
- thin local UI shell
- end-to-end V2 smoke test

## Fast start

Read in this order:

1. `docs/legacy_data_handoff.md`
2. `docs/current_state.md`
3. `docs/v2/reentry_start_here.md`
4. `docs/v2/product_principles.md`
5. `docs/v2/architecture.md`
6. `docs/v2/mvp_big_steps.md`
7. `docs/runbook.md`

## Run

Smoke test:

```bash
python3 tests/v2_smoke_tests.py
python3 tests/legacy_corpus_tests.py
```

Thin local UI shell:

```bash
python3 app/dev_server.py
```

Then open `http://127.0.0.1:8765`.

## Product rule

This system should answer:

- what hand classes are underperforming
- where Hero is drifting
- what stable strengths are holding or regressing
- what field distortions characterize the current pool
- where adaptation is becoming contamination
- what the next best adjustment is
