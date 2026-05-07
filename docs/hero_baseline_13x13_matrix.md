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

The matrix should also surface runout-noise / cooler-watch guardrails. Protected premium or standard baseline spots such as `KK` pressure lines, `AK` all-ins, or repeated standard BB defends may show ugly actual results without being automatic range reductions. These cards should say "bad result, review before over-correcting" and must be framed as actual-result proxy interpretation, not solver EV or all-in adjusted EV.

These guardrails should be trend-aware:

- Last 7 days
- Last 30 days
- All history

The recent windows should be anchored to the latest parsed hand timestamp in the current Matrix payload. This keeps recent painful runout clusters visible instead of diluting them inside the full historical baseline.

Matrix hover panels must not be clipped by parent cards. The operator page may keep a compact matrix, but the primary reading surface is now the dedicated `/operator/matrix` page where the grid, correction cards, hidden value cards, and selected-hand breakdown have room to breathe.

Matrix inspection should not depend on hover. The dedicated page now supports click-to-pin hand classes so Hero can keep one or two action breakdowns open while scanning the grid or comparing nearby classes.

Pinned detail should lead with a position-first situation diagnostic before action-frequency visuals. Hero should be able to answer "where does this hand win or lose?" before reading internal action labels. Action-frequency visuals may remain as secondary debug context, but the primary product view is now position + situation + result.

Pinned detail should also include a deterministic English hand read for every hand class. The read should translate actual-result splits into a next review action, not pretend to be solver EV. For baseline-capable hands such as suited broadways, negative BB defend results should produce "review this subset first" language before any range-reduction language.

Hand classes with less than 5% voluntary participation should be treated as exposure context, not core performance signals. Their Matrix cells should be neutralized visually, and pinned detail should avoid over-interpreting tiny played samples as wins, leaks, or value.

Pinned detail should also expose 3bet line structure when available. In particular, Hero wants to inspect common lines such as `2x open -> 6bb 3bet`, and whether Hero later folds after facing a 4bet. These are line-sequence facts, not automatic mistake judgments.

Pinned detail should also expose dealt-but-not-played fold context. Premium hands such as `TT` can be dealt far more often than they are voluntarily played, and some folds may be correct folds versus large pressure. These folds should remain exposure context unless later review proves a mistaken overfold.

## Dedicated Matrix Page

`/operator/matrix` is the focused Hero Preflop Baseline reading surface.

`/app/matrix` is the authenticated user first-value surface. A user should be able to sign up, upload GG hand histories, and immediately see a personal preflop Matrix with actual-result interpretation. Operator depth remains available separately under `/operator/matrix`.

It should organize the same deterministic payload into:

- preflop sizing summary:
  - total parsed hand histories,
  - Hero first-action open size average,
  - Hero first-action open size mode and median,
  - 2x open discipline rate,
  - clean non-all-in-like 3bet sizing average,
  - raw 3bet count and near-all-in / 20bb+ pressure count,
  - 3bet sizing by position,
  - single-open 2x 3bet size versus squeeze sizing with callers,
- AOF baseline summary:
  - Hero first-action preflop jam count,
  - average and median effective stack BB,
  - separate 25bb-or-less baseline,
  - jam stack depth by action type and position,
  - deterministic interpretation of the AOF baseline,
- runout-noise guardrails:
  - premium or standard baseline hands with repeated bad actual results,
  - Last 7 days / Last 30 days / All history trend tabs,
  - confidence reminder language to prevent result-driven fear,
  - example-review framing before any range shrink,
- overview counts,
- compact interpretation legend,
- top five review-first correction candidates,
- full-width 13x13 hand-class grid,
- click-to-pin one/two hand-class detail,
- position-first situation/result summary for pinned hand classes,
- optional action-frequency visual/debug summary for pinned hand classes,
- 3bet / 4bet-response line facts where available,
- and dealt-but-not-played fold exposure.

This keeps the operator dashboard from becoming the only place to read deep hand-class interpretation.

## Daily Matrix Quiz

`/operator/matrix/quiz` is the Hero Baseline recall surface.

It turns high-signal Matrix candidates into daily post-hoc study cards:

- partial context and sample stats first,
- Hero chooses `Baseline`, `Watch`, `Leak`, or `Value`,
- then the real Matrix-derived grade, result metrics, explanation, and study takeaway are revealed.

Quiz attempts are learning logs only. They are stored as operator review overlays and must not automatically promote quiz misses, surprise, or memory mismatch into Today, Brain, or durable Hero memory.

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
