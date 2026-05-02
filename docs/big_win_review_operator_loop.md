# Big-Win Review Operator Loop

## Purpose

Big winning tournaments should stand out in OPB, but they should not automatically rewrite Hero memory as if every rewarded decision was repeatable.

The loop is:

1. official GG tournament summary marks the result as high-weight context,
2. linked hand-history session provides decision evidence,
3. deterministic review candidates identify spots worth operator inspection,
4. operator tags each spot,
5. only reviewed repeatable execution should later be promoted into durable Hero memory.

## Current Tags

- `repeatable_execution`: Hero did something worth keeping or studying as a positive baseline.
- `run_good`: result was heavily helped by variance; preserve context but avoid over-crediting.
- `cooler`: high-impact outcome but not useful as a behavioral adjustment.
- `unclear`: not enough context yet; keep visible but do not promote.

## MVP Scope

The current implementation focuses on tournament `6408385`, Hero's `Mini Thursday Throwdown $25 [Bounty]` 2nd-place finish for `$1,098.28`.

The operator page now exposes:

- official result context,
- linked 296-hand session context,
- high-weight candidate hands,
- reasons each hand was selected,
- Hero action snippets,
- and a tag form that writes operator overlays.

## Truth Policy

Operator tags are overlays.

They do not mutate raw hands, official results, session evidence, or existing memory items.

This keeps the system safe while allowing Hero/operator review to separate repeatable execution from run-good before Brain learns from the win.

## Next Step

Use the operator tags to create reviewed positive execution memory updates.

That next step should require explicit tags and should not promote unreviewed big-win spots automatically.
