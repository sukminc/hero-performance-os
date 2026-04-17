# AOF Baseline Spec V1

## Purpose

This document defines the first operator-grade AOF baseline scope for Hero Performance OS.

The goal is not to build a full solver clone or exact tournament GTO engine.
The goal is to answer one practical question first:

- is Hero handling the <=15bb preflop baseline correctly often enough?

This first version is intentionally narrow so it can become readable, measurable, and useful fast.
It must also remain honest about tournament-format differences and intentional deviations.

## Product Question

Hero wants to know:

- when stack depth is 15bb or lower,
- in normal multi-seat tournament structures,
- is Hero choosing the right preflop action often enough?
- and when Hero deviates, is that a mistake or an intentional format/context adjustment?

The system should show this in numbers, not only commentary.

## Scope

In scope:

- effective stack `<= 15bb`
- tables with `5 or more active seats`
- Hero preflop decision only
- unopened preflop spots first
- tournament-format-aware baseline profiles
- action families:
  - `fold`
  - `open_raise_small`
  - `open_jam`
  - `open_almost_all_in`
- position-aware baseline analysis
- hand-class-based action review
- operator-facing numeric summary

Out of scope for v1:

- exact PKO bounty math
- exact ICM / payout ladder math
- exact final-table pressure math
- postflop analysis
- facing-open reshove trees
- facing-jam calloff trees
- blind-vs-blind special-case trees
- short-handed special tables below 5 players
- mixed-frequency exactness

## Why This Scope

This scope is chosen because it matches Hero's immediate question:

- at 15bb or lower,
- with normal tournament table sizes,
- does Hero open, jam, or fold correctly by position and hand class?
- and is Hero's deviation coming from strategic intent rather than sloppy short-stack structure?

This is the cleanest first AOF layer because:

- it is highly actionable
- it is easy to explain
- it maps closely to real tournament fundamentals
- it keeps format differences visible without pretending to solve exact bounty/ICM math

## Inclusion Rules

A hand is an AOF v1 candidate only if all conditions below are true:

1. `effective_stack_bb <= 15`
2. `active_seat_count >= 5`
3. Hero still has cards and a live decision preflop
4. No player has voluntarily entered the pot before Hero acts
5. The spot is a Hero unopened preflop decision

If any of these are false, the hand is excluded from AOF v1 scoring and may be handled in later versions.

## Active Seat Count

`active_seat_count` means the number of seated players dealt into the hand at the start of the preflop action.

This is used to keep v1 focused on normal tournament structures:

- 5-handed
- 6-handed
- 7-handed
- 8-handed
- 9-handed

This excludes more unusual short-handed endgame structures for now.

## Effective Stack

For v1, use Hero's effective stack band as the controlling stack input.

Primary stack bands:

- `0-8bb`
- `8-12bb`
- `12-15bb`

These bands are sufficient for first-pass baseline comparison and numeric reporting.

## Tournament Format Profiles

AOF v1 must not use one universal baseline for every tournament type.

The first implementation should support at least these baseline profiles:

- `standard_mtt`
- `pko`
- `satellite`

### `standard_mtt`

Use this profile for ordinary tournament spots where chip accumulation follows a normal MTT baseline.

### `pko`

Use this profile when bounty dynamics materially affect short-stack incentives.

The v1 system does not need exact bounty math, but it must preserve that PKO actions may differ from standard MTT baselines.

### `satellite`

Use this profile when survival pressure dominates ordinary chipEV accumulation.

The v1 system does not need exact bubble math, but it must preserve that fold decisions may be correct more often than in standard MTT profiles.

## Action Families

Hero's actual preflop action should be normalized into one of the following:

- `fold`
- `open_raise_small`
- `open_jam`
- `open_almost_all_in`

### `open_raise_small`

A non-all-in open raise that does not leave Hero trivially committed.

Example:

- Hero has 15bb
- Hero raises to around 2bb to 2.5bb
- Hero still has meaningful stack behind

### `open_jam`

Hero opens all-in preflop.

### `open_almost_all_in`

Hero does not technically move all-in, but the sizing is functionally jam-like.

Recommended v1 interpretation:

- raise uses `>= 80%` of Hero's pre-action stack
  or
- raise leaves `<= 1.5bb` behind

This category matters because near-jam sizing may mean very different things:

- a real short-stack process leak
- a deliberate pressure sizing pattern
- a special-context format deviation

## Positions

Position analysis should be grouped into the most readable operator categories available from parsed data:

- `UTG`
- `HJ`
- `CO`
- `BTN`
- `SB`
- `BB`

If seat-to-position mapping is incomplete in some hands, those hands should be excluded from position-specific scoring rather than guessed aggressively.

## Hand Classes

Hand classes should be normalized into standard labels such as:

- `AA`
- `QQ`
- `AKs`
- `AJo`
- `76s`

This is necessary because Hero wants to see patterns like:

- at `UTG 15bb`, is `AA` being raised correctly?
- is `QQ` being jammed enough?
- are medium-strength offsuit broadways being mishandled?

## Baseline Model

The v1 baseline should use a simple operator-approved tournament preflop baseline, not an exact solver engine.

Recommended v1 baseline philosophy:

- action labels should resolve to `fold`, `raise`, `jam`, or `mixed`
- the baseline should be position-aware
- the baseline should be stack-band-aware
- the baseline should be format-profile-aware
- the baseline should prioritize readability over false precision

This baseline is intended to answer:

- what was the preferred action family here?

Not:

- what is the exact EV difference to the fourth decimal place?

The system should therefore separate:

- `baseline family`
- `actual action family`
- `deviation interpretation`

## First-Pass Verdicts

Each in-scope AOF hand should receive one verdict:

- `match`
- `too_tight`
- `too_loose`
- `awkward_raise`
- `intentional_pressure_sizing`
- `special_context_defer`
- `mixed`
- `excluded`

### `match`

Hero's action matches the preferred baseline action family.

### `too_tight`

Hero chose a more conservative action than the baseline suggests.

Typical examples:

- fold instead of open-jam
- fold instead of open-raise

### `too_loose`

Hero chose a more aggressive action than the baseline suggests.

Typical examples:

- jam instead of fold
- raise instead of fold

### `awkward_raise`

Hero used a non-all-in raise or near-all-in raise where clean jam discipline is the preferred baseline behavior.

This remains an important v1 diagnosis, but it must not absorb all near-jam deviations automatically.

### `intentional_pressure_sizing`

Hero used a near-jam open that appears to be intentionally designed to shape the response tree.

Examples may include:

- inviting a reshove structure from shorter stacks
- discouraging wider calls from larger stacks
- creating a stack-geometry problem instead of choosing a pure jam line

This bucket exists because Hero explicitly uses some near-jam sizes as deliberate strategic pressure, not as accidental awkward sizing.

### `special_context_defer`

The deviation should remain inspectable but should not be auto-graded as a clean miss because tournament context may dominate the baseline.

Typical examples:

- PKO-specific pressure
- satellite survival pressure
- payout-jump-sensitive spots

### `mixed`

The baseline is mixed enough that Hero's action should not be treated as a clean miss.

### `excluded`

The hand is outside AOF v1 scope or is missing enough context to score reliably.

## Numeric Outputs

The first AOF surface should show numbers before commentary.

Minimum numeric summary:

- `aof_opportunity_count`
- `aof_match_rate`
- `too_tight_rate`
- `too_loose_rate`
- `awkward_raise_rate`
- `intentional_pressure_sizing_rate`
- `special_context_defer_rate`
- `mixed_rate`

Action-shape summary:

- `fold_rate`
- `open_raise_small_rate`
- `open_jam_rate`
- `open_almost_all_in_rate`

Breakdowns:

- by `stack_band`
- by `position`
- by `hand_class`

## First Operator Views

The first useful views should be:

1. overall AOF score summary
2. tournament-format-profile AOF summary
3. position-by-position AOF summary
4. jam map by position and hand class
5. near-jam interpretation summary
6. top repeated misses

## Example Questions This Should Answer

- at `UTG 15bb`, is Hero using premium hands correctly?
- is Hero over-jamming hands that should still raise small?
- is Hero under-jamming upper-tier hands that should usually shove?
- is Hero using awkward near-jam raises too often?
- which near-jam opens are intentional pressure sizing rather than mistakes?
- where should PKO or satellite context stop naive chart grading?
- which positions show the worst AOF discipline?

## Success Criteria

This spec is successful if the first implementation can answer:

- how many real AOF opportunities Hero had
- how often Hero matched the baseline
- where Hero is too tight
- where Hero is too loose
- where Hero's short-stack raise discipline is structurally messy
- where Hero is intentionally deviating from baseline
- where format context should defer naive grading

## Immediate Next Step

Implement a deterministic `AOF spot detector` for:

- `effective_stack_bb <= 15`
- `active_seat_count >= 5`
- unopened Hero preflop spots

Then attach:

- normalized hand class
- normalized action family
- tournament format profile
- baseline action family
- verdict

Only after this works cleanly should v2 expand into:

- facing-open reshove
- calloff trees
- blind-vs-blind
- short-handed exceptions
