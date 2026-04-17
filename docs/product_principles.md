# Product Principles

## Core Product Principle

Hero Performance OS is not a software product that tries to prove how much GTO Hero has memorized.

It is a software product that:

- captures Hero's repeated poker patterns,
- measures the real outcomes of those patterns,
- interprets where those patterns are working or failing,
- and builds a personal strategic baseline that makes later study more grounded.

The product is therefore not a generic GTO grader.
It is a pattern-and-results operating system for one serious tournament player.

## What The Product Is Trying To Build

The software should help Hero answer:

- what patterns do I actually repeat?
- what results do those patterns produce?
- what strategic beliefs sit behind those patterns?
- where do those beliefs work?
- where do they overextend?
- what should I study next because of that?

This is different from asking:

- did this one hand match a solver output?

The product should care more about repeatable pattern truth than isolated hand judgment.

## Role Of GTO

GTO is important in this product, but it is not the product itself.

GTO should be used as:

- a baseline frame,
- a calibration reference,
- a study guide,
- and a way to explain where Hero is deviating.

GTO should not be used as:

- the only product voice,
- a scolding engine,
- a memoryless right/wrong machine,
- or a substitute for Hero's own repeated pattern history.

## AOF Principle

AOF analysis exists because short-stack preflop decisions are one of the cleanest strategic foundations in tournament poker.

The product should use AOF analysis to:

- show whether Hero's `<=15bb` structure is stable,
- identify repeated action-family deviations,
- separate clean baseline matches from repeated misses,
- and preserve intentional deviations when they are part of Hero's actual strategic pattern.

AOF should not be reduced to pure chart shaming.
Its job is to make Hero's baseline stronger and more inspectable.

## 13x13 Matrix Principle

The `13x13` starting-hand matrix is important because it makes hand-class behavior visible in a way Hero can understand quickly.

The product should use the matrix to show:

- where Hero repeatedly wins or loses real chips / bb,
- which hand classes are being overused or underused,
- how specific hand-class beliefs show up in actual performance,
- and where study should be focused next.

The matrix must remain ante-aware.
In online tournaments with seat-by-seat antes, garbage hands may show negative raw `bb net` simply because compulsory costs are being paid correctly.
The product must therefore separate:

- structural negative result,
- suspicious hand-class usage,
- and belief-driven repeated misuse.

This matrix should not be treated as decorative heatmap output.
It is a core operator surface for exposing repeated strategic behavior.

## EV / Actual Result Principle

The product should connect pattern analysis to outcomes.

That means:

- actual `bb net`,
- hand-class performance,
- stack-band performance,
- and later EV-style references where support exists

should all be used to test whether Hero's repeated beliefs are paying off.

This software should not stop at saying:

- Hero deviated from baseline.

It should continue to ask:

- what did that deviation produce over time?

## Belief Principle

The product must preserve that Hero is not making decisions from memorized charts alone.

Hero often plays from beliefs such as:

- this hand is an attack hand but not a calloff hand
- this blocker hand works when blinds defend or overfold a certain way
- this near-jam size is meant to shape the response tree

The software must therefore interpret:

- repeated action pattern,
- repeated result pattern,
- and repeated belief pattern

together.

The system should not flatten all deviations into mistakes.

## Study Principle

The software should help Hero study better later.

That means AOF analysis, `13x13` analysis, and EV/result analysis should all contribute to a stronger personal baseline.

The intended outcome is:

- Hero sees repeated pattern truth,
- Hero sees which beliefs are working,
- Hero sees where beliefs are overextending,
- Hero then studies tools such as GTO Wizard from a stronger baseline,
- and future study gets anchored to real repeated leaks instead of abstract curiosity.

In other words:

- the product is not GTO Wizard replacement,
- it is the baseline-building layer that makes GTO Wizard study far more useful.

## Product Promise

The product should eventually be able to say:

- here is how you actually play,
- here is what those patterns produce,
- here is where your baseline is strong,
- here is where your baseline is unstable,
- and here is what to study next.

That is the product promise.
