# 13x13 Hand-Class / Result Analysis Spec V1

## Purpose

This document defines the first operator-grade `13x13` hand-class / result analysis scope for Hero Performance OS.

The goal is not to create a decorative matrix.
The goal is to show:

- how Hero is actually using starting-hand classes,
- what real outcomes those hand classes are producing,
- how those outcomes change by position,
- and which hand-class beliefs should be studied next.

## Product Question

Hero wants to know:

- which hand classes am I repeatedly using well?
- which hand classes am I repeatedly overusing or underusing?
- where are my real results weak by position?
- which hand classes should I study next?

This surface exists to build Hero's personal baseline, not to replace solver study.

## Scope

In scope:

- normalized `13x13` starting-hand classes
- cumulative hand-class result analysis
- position-aware hand-class result analysis
- actual result tracking using `bb`-normalized outcome
- sample-count-aware interpretation
- operator-facing hand-class cards
- study-queue generation from repeated weak hand-class behavior

Out of scope for v1:

- exact solver EV
- full all-in-adjusted EV engine
- postflop node decomposition
- villain-cluster-aware result decomposition
- exact ICM / payout-ladder weighting
- final-table-specific reweighting
- consumer-facing polish

## Core Principle

This feature must not behave like a naive heatmap that treats all negative raw `bb net` as strategic failure.

Online tournaments with position-by-position antes create structural negative drift for many weak hands.

For example:

- `72o`
- `83o`
- similar garbage classes

may be negative in raw `bb net` simply because they repeatedly pay antes and are correctly folded.

That means:

- raw `bb net` alone is not enough
- garbage-hand negativity is not automatically a leak
- interpretation must separate structural cost from suspicious misuse

## Input Unit

The base unit is one parsed hand with:

- normalized hand class
- position
- stack context when available
- tournament format when available
- actual result converted into `bb`

## Hand-Class Normalization

Hand classes should be normalized into standard matrix labels such as:

- `AA`
- `AKs`
- `AJo`
- `76s`
- `72o`

The matrix should support:

- overall aggregation
- position-filtered aggregation

## Position Split

The first position-aware views should support:

- `UTG`
- `UTG+1`
- `LJ`
- `HJ`
- `CO`
- `BTN`
- `SB`
- `BB`

If exact position mapping is missing, that sample should be excluded from position-specific comparison rather than guessed aggressively.

## Primary Metrics

Each `hand_class x position` cell should include at least:

- `hands_played`
- `actual_bb_net`
- `avg_bb_per_hand`
- `sample_band`

### `hands_played`

How many times the hand class was actually dealt and tracked in the given slice.

### `actual_bb_net`

Real cumulative `bb` result for that hand class in the given slice.

### `avg_bb_per_hand`

Average `bb` result per observed hand in the given slice.

### `sample_band`

A confidence-oriented bucket such as:

- `tiny`
- `small`
- `medium`
- `large`

This prevents overreacting to one-off outliers.

## Ante-Aware Interpretation Rule

The matrix must remain ante-aware.

In online ante structures:

- every seat contributes ante pressure,
- weak hands often lose small amounts structurally,
- and folding a garbage hand after posting ante is not evidence of misuse by itself.

Therefore v1 interpretation should distinguish between:

- `structural negative`
- `usage concern`
- `belief concern`

### `structural negative`

A hand class is negative mostly because it pays compulsory costs and is usually folded correctly.

Typical example:

- `72o` being negative across positions is not surprising on its own.

### `usage concern`

A hand class becomes more suspicious when:

- it is used aggressively more often than expected,
- it produces weak results in the positions where Hero keeps approving it,
- or its losses are meaningfully worse than surrounding comparable hand classes.

### `belief concern`

A hand class becomes a belief concern when:

- Hero appears to assign it a strategic role repeatedly,
- that role shows up in action choices and results,
- and the pattern remains visible over time.

Examples may include:

- `KJo` as a pressure hand
- low `Ax` as a blocker/exploit hand
- middling suited/broadway hands as overapproved attack hands

## First Product Views

### View 1: Overall Matrix

One `13x13` matrix across the whole corpus.

Recommended display logic:

- color by `avg_bb_per_hand` or normalized result strength
- opacity or badge by `sample_band`

### View 2: Position Filter

Allow the same matrix to be viewed by position:

- `UTG`
- `HJ`
- `CO`
- `BTN`
- `SB`
- `BB`

This is necessary because a hand class may be acceptable in one position and suspicious in another.

### View 3: Hand-Class Cards

The matrix should feed product cards for repeated signals.

Each card should include:

- `hand_class`
- `positions_observed`
- `hands_played`
- `actual_bb_net`
- `avg_bb_per_hand`
- `why_flagged`
- `likely_okay_contexts`
- `suspicious_contexts`
- `validation_status`
- `study_suggestion`

### View 4: Study Queue

The product should surface a short study queue such as:

- `Study KJo early-position usage`
- `Study low Ax offsuit by format`
- `Study suited wheel ace jam/open split`

## Flagging Logic

The first flagging logic should support at least these categories:

- `overused_and_losing`
- `position_distortion`
- `belief_hand`
- `structural_negative_only`

### `overused_and_losing`

The hand class is used often enough to matter and produces weak actual results.

### `position_distortion`

The hand class looks acceptable overall but performs poorly in one or two positions.

### `belief_hand`

The hand class appears tied to a repeated strategic belief rather than random distribution.

### `structural_negative_only`

The hand class is negative, but the negativity is not strong evidence of misuse.

This category is essential for garbage hands in ante-heavy environments.

## What This Feature Should Not Do

It should not:

- say `72o is a leak` just because it is negative
- flatten every negative hand class into a coaching error
- present tiny-sample outliers as truth
- replace AOF analysis

Instead, it should help Hero ask smarter follow-up questions.

## Success Criteria

This feature is successful if it can show:

- which hand classes are structurally bad but not interesting,
- which hand classes are truly suspicious,
- where position changes the interpretation,
- and which hand classes should be studied next.

## Immediate Next Step

Implement the first derived aggregation for:

- `hand_class`
- `position`
- `hands_played`
- `actual_bb_net`
- `avg_bb_per_hand`
- `sample_band`

Then add first-pass flagging for:

- `structural_negative_only`
- `overused_and_losing`
- `position_distortion`
- `belief_hand`
