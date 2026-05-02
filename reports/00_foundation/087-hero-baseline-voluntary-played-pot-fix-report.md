# Task 87: Hero Baseline Voluntary Played-Pot Fix

## TASK

Verify and fix whether Hero Baseline was counting forced blind / ante / big-blind free-check hands as played pots.

## WHAT I CHANGED

- Inspected `72o` played-pot examples.
- Confirmed several `72o` rows were big-blind `other` paths, including free-check/showdown or forced-blind hands.
- Updated played-pot policy so only `call`, `raise`, and `jam` count as voluntary participation.
- Excluded `other` from performance metrics, matrix counts, stack realization, hover breakdowns, and correction queues.
- Updated Hero Baseline docs.

## ARCHITECTURE IMPACT

This strengthens the Hero Baseline derived truth layer.

The matrix now better matches the product question: how Hero performs when he voluntarily enters or escalates a pot with a hand class.

## DECISIONS MADE

- Antes are not participation.
- Posted blinds alone are not participation.
- Big blind free-check / no voluntary action is not participation.
- `other` is excluded until it can be safely decomposed into meaningful voluntary actions.

## RISKS / OPEN QUESTIONS

- Some rare `other` cases may include meaningful actions that the parser failed to classify.
- A later parser improvement should split `check_free_play`, `blind_forced_showdown`, and true unknown actions explicitly.

## OUT OF SCOPE

- No parser schema change.
- No database migration.
- No postflop street decision analysis.

## TEST / VALIDATION

Validation should confirm `72o` played count drops after excluding `other`.

## RECOMMENDED NEXT STEP

Add explicit `free_play_bb` and `forced_blind_only` categories as exposure context, separate from played-pot performance.
