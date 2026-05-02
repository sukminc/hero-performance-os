# Stack-Normalized Hero Baseline

## Purpose

Raw BB result alone can mislead Hero Baseline.

Winning 10bb from a 10bb stack is not the same as winning 10bb from a 125bb stack. The first can be a full tournament-life double-up; the second is a modest deep-stack gain.

The 13x13 matrix now keeps raw BB while adding stack-normalized result.

Performance calculations use played pots by default, not every time Hero was dealt the hand. Dealt counts remain exposure context only.

## Metrics

### Raw BB

`avg_bb_per_hand`

This answers:

- how many big blinds did Hero win or lose with this hand class?

### Stack Realization %

`avg_stack_realization_pct = bb_net / effective_stack_bb * 100`

This answers:

- how much of Hero's starting stack did this hand gain or lose?

### Full-Stack Loss Rate

Count/rate of observations where the hand lost at least 80% of the starting stack.

This highlights hands that may create tournament-life mistakes.

### Double-Up Rate

Count/rate of observations where the hand gained at least 80% of the starting stack.

This protects short-stack positive execution from being underrated by raw BB.

## Product Rule

Hero Baseline should compare both views:

- Raw BB matrix
- Stack-normalized matrix
- Raw-vs-stack mismatch queue
- Selected-hand insight card

No hand should be labeled as a true leak from raw BB alone.

## Current Limitation

This is still not:

- solver EV,
- all-in adjusted EV,
- ICM EV,
- or PKO bounty EV.

It is a better deterministic post-hoc result normalization layer.

## Next Step

The next useful layer is decision-node decomposition for suspicious hands:

- position,
- stack band,
- first preflop action,
- facing action,
- format,
- and example hands.
