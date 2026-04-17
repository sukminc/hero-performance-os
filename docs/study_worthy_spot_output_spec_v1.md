# Study-Worthy Spot Output Spec V1

## Purpose

This document defines how Hero Performance OS should surface study-worthy repeated spots from Hero's historical hand data.

The goal is not to output the hands that simply lost the most money.
The goal is to output the spots that are most worth studying because they reveal a repeated approval pattern, a threshold mistake, or a belief-driven tendency that can actually change future play.

## Core Rule

The product must distinguish between:

- a big result event
- a repeated decision pattern

Only repeated decision patterns should become high-priority study outputs.

This means:

- `AA vs KK` coolers should not automatically become study priorities
- one-off high-loss premium collisions should not dominate the queue
- repeated proactive approvals in the same strategic family should stand out

## The Three Things That Must Clearly Show

The output should clearly separate three kinds of spots:

### 1. Clear Repeated Mistakes

These are spots where Hero repeatedly approves an action that is likely too aggressive or too loose for the lane.

Typical product feeling:

- this is not just variance
- this is not just a thin threshold node
- this pattern keeps showing up and should be corrected

Output should include:

- spot family label
- repeated count
- positions observed
- formats observed
- why this is clearly suspicious
- recent examples
- recommended study action

### 2. Threshold Study Spots

These are spots where the main value is learning the boundary correctly.

Typical product feeling:

- this is worth studying because Hero needs a cleaner continue or jam threshold
- this may not be an obvious punt every time
- but the boundary is important enough to lock down

Output should include:

- spot family label
- repeated count
- current action mix
- why the threshold matters
- what exact boundary needs study

### 3. Belief-Driven Patterns

These are spots where Hero appears to attach a recurring strategic belief to a hand class or family.

Typical product feeling:

- Hero seems to trust this hand as pressure more than baseline would suggest
- Hero seems to approve this family because of blocker or fold-equity logic
- this is not random distribution; it reflects a repeated belief

Output should include:

- belief family label
- repeated count
- positions / formats
- interpretation of the underlying belief
- whether the pattern looks stable, improving, or unresolved

## What Must Not Stand Out By Default

The system should suppress or down-rank:

- premium coolers
- one-off all-in collisions
- top-loss outliers without repetition
- structurally negative garbage hands

These may still be inspectable, but they should not outrank true repeated study spots.

## Output Priority Rule

When multiple candidates exist, priority should favor:

1. repeated action-family distortion
2. repeated threshold uncertainty
3. repeated belief expression
4. pure result outliers

This is the product's anti-noise rule.

## Minimum Evidence Requirement

A spot should not become a study-worthy surfaced item unless at least one of these is true:

- the exact same family appears at least `3` times
- a broader family appears at least `5` times across nearby positions or adjacent hand classes
- the same action pattern appears across multiple formats

This avoids overreacting to one screenshot or one result.

## Current Historical Findings To Preserve

Based on the current canonical Hero corpus, three study-worthy spot families are already visible enough to preserve as explicit product targets:

### 1. `KJo` Early / Mid Under-15bb Pressure Approval

This family shows repeated proactive approvals with `KJo` under `15bb`, including:

- `UTG` unopened jams
- `HJ` unopened raises
- `HJ` unopened jams

This should surface as a threshold-and-belief family, not as a single result card.

### 2. `KQo` Early / Mid Under-15bb Pressure Approval

This family shows repeated proactive approvals with `KQo` under `15bb`, including:

- `UTG` unopened raises
- `HJ` unopened raises
- `HJ` unopened jams

This should surface as a threshold study family because Hero already thinks in terms of:

- `3bet okay`
- `4bet jam continue not okay`

The product should help lock that boundary.

### 3. Low `Ax` Offsuit Under-15bb Early Pressure Family

The historical corpus already shows repeated low offsuit ace proactive approvals, especially through:

- `A3o` `UTG` unopened jams
- `A3o` `HJ` unopened jams
- `A7o` `UTG` unopened raises
- `A7o` `HJ` unopened raises
- `A4o` `UTG` unopened raises

This should surface as a belief-driven family rather than a single-hand result anomaly.

## Honesty Rule

If a hand family does not actually repeat in the data, the product must not pretend it does.

For example:

- `22` early under-15bb jam is a valid example of the kind of obvious mistake that should stand out
- but if the current Hero corpus does not repeat that exact pattern strongly enough yet, the product should say so directly
- and should instead surface the closest real repeated family that the data actually supports

## Product Language Rule

The output should not sound like a solver grading transcript.
It should sound like:

- here is the repeated spot
- here is how many times it happened
- here is why it matters
- here is what to study next

## Next Product Step

The next implementation layer after the exploratory `13x13` matrix should be a deterministic study-worthy output layer that:

- groups repeated spots by family
- separates repeated mistake vs threshold vs belief
- suppresses variance-dominated noise
- and produces a short ranked study queue
