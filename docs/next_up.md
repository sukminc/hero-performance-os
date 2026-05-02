# Next Up

## Immediate next phase

Phase 6: Hero-first private beta hardening

## Recommended first task packet

### Title

Run a real Hero hand-history update check through login, upload, and changed outputs.

### Objective

After durable lead capture and provisioning exist, prove the actual Hero workflow against real post-cutoff GG hand histories.

### Scope

- run local app login path
- upload a real GG hand-history batch from Hero
- compare corpus counts and latest upload readout
- compare Today / Review / Brain before and after
- document parser/output credibility gaps

### Out of scope

- full multi-tenant production auth stack
- checkout
- broad non-Hero onboarding implementation

### Validation target

- upload is tied to viewer ownership
- real hand histories ingest or fail honestly
- output deltas are captured clearly

### Report destination

- `reports/00_foundation/069-hero-real-hand-history-update-check-report.md`

## After that

1. choose the next backend credibility gap from the real upload results
