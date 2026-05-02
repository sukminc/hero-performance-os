# Hero Baseline 13x13 Matrix

## Purpose

The 13x13 matrix is the first Hero Baseline hand-class surface.

It helps Hero answer:

- Which hands are actually winning or losing in my database?
- Which hands deserve review because I may be playing them poorly?
- Where do position, stack depth, and format change the meaning?
- Which apparent results are just small samples or ante-driven noise?

## Current Truth Level

The current matrix shows actual BB result per hand class.

It is not yet:

- solver EV,
- all-in adjusted EV,
- ICM EV,
- PKO EV,
- or proof that a hand is intrinsically good or bad.

It is a deterministic baseline-building layer that makes Hero's real outcomes visible.

## Product Surface

The operator screen now restores:

- all-history 13x13 matrix,
- selected-hand spotlight defaulting to `66`,
- actual BB net,
- average BB per hand,
- played-pot sample count,
- dealt-count exposure context,
- suspicious hands queue,
- and selected-hand position breakdown.

## Counting Policy

Performance metrics must use `played_count`, not raw dealt count.

`dealt_count` means Hero was dealt the hand class.

`played_count` means Hero voluntarily entered the pot or took a non-fold action.

The matrix may still expose dealt count as context, but default performance, suspicious queues, stack realization, and insight cards should be based on played pots.

Forced antes, posted blinds, and big-blind free-check paths do not count as played pots unless Hero voluntarily calls, raises, or jams. This prevents hands like `72o` from being treated as strategic participation only because Hero was in the big blind and saw a check-down.

## Preflop Entry Policy

Played pots should be decomposed by first Hero preflop entry type:

- open limp / complete
- limp behind
- call versus open
- call versus 3bet
- call versus 4bet+
- open raise / jam
- iso raise / jam
- 3bet
- 4bet
- 5bet+

This is required before saying a hand is overplayed. A hand may be fine as an open and bad as a calloff or 3bet candidate.

## Matrix Hover Rule

Every matrix cell should expose a quick action-depth breakdown on hover:

- dealt count
- played count
- top entry types
- raw BB per hand
- stack realization %

The matrix should also surface a separate mandatory correction queue for repeated hand/action pairs with severe stack-normalized losses.

Matrix hover panels must not be clipped by parent cards. The operator page may keep a compact matrix, but the primary reading surface is now the dedicated `/operator/matrix` page where the grid, correction cards, hidden value cards, and selected-hand breakdown have room to breathe.

## Dedicated Matrix Page

`/operator/matrix` is the focused Hero Baseline reading surface.

It should organize the same deterministic payload into:

- overview counts,
- compact interpretation legend,
- mandatory correction candidates,
- hidden value / positive execution candidates,
- 13x13 hand-class grid,
- and selected-hand action breakdown.

This keeps the operator dashboard from becoming the only place to read deep hand-class interpretation.

## Positive Execution Rule

Hero Baseline should not only find leaks.

When a non-premium hand/action pair repeatedly realizes positive stack-normalized value, it should surface as a hidden value or keep/study candidate. These cards do not prove solver correctness; they protect Hero from over-correcting away from patterns that may be working in the actual tournament pool.

## Interpretation Rule

If a hand such as `66` is losing, the product should not immediately say “66 is bad.”

The next question must be:

- Which positions lose?
- Which stack bands lose?
- Is this unopened aggression, calloff, flatting, or multiway commitment?
- Is the sample large enough?
- Is format context changing the baseline?

## Next Layer

The next Hero Baseline task should turn suspicious hand classes into product cards:

- likely execution issue,
- context that needs review,
- examples,
- what to test next session,
- and operator approval/rejection overlay.
