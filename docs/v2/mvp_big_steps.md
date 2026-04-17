# V2 MVP Big Steps

## MVP definition

V2 reaches MVP when Hero can reliably do all of the following in one coherent system:

1. ingest a session packet,
2. inspect how it parsed,
3. inspect what evidence it created,
4. inspect what cumulative memory it updated,
5. see the current state of his game,
6. get 1-3 next-session adjustments,
7. and trust that the chain is stable enough to use repeatedly.

The MVP is not a polished consumer product.
The MVP is a dependable personal operator-grade performance OS.

## Big Step 1. Truth chain exists end-to-end

Goal:

- ingest -> parse -> evidence -> memory -> surfaces is real and testable

Status:

- already substantially established in V2

Done means:

- a session fixture can run through the full chain
- duplicate-safe behavior exists
- zero-hand-safe behavior exists
- Today, Command Center, Session Lab, and Memory Graph can all read from V2 state

## Big Step 2. Core read models become daily-usable

Goal:

- make the existing read paths usable enough that Hero would actually open them regularly

Main surfaces:

1. Command Center
2. Session Lab
3. Memory Graph

Done means:

- Command Center tells Hero what state he is in
- Session Lab shows what the latest session added
- Memory Graph shows cumulative memory by status/type

## Big Step 3. Thin operator UI shell over the read models

Goal:

- stop treating the system as API-only and make it operable without manual inspection of code or JSON

Scope:

- thin shell only
- no design detours
- no broad consumer polish

Done means:

- Hero can open a single V2 interface
- navigate Command Center / Session Lab / Memory Graph
- read core outputs without manual scripting

## Big Step 4. Memory quality and evidence quality refinement

Goal:

- improve whether the outputs are actually useful, not just whether the pipeline runs

Focus:

- hand-class underperformance logic
- style drift logic
- field distortion logic
- contamination logic
- better ranking of top memory and top adjustments

Done means:

- the outputs feel more like calibrated poker judgment and less like generic tagging

## Big Step 5. Review / Brain / operator correction loop

Goal:

- restore the richer V1 operator strengths on top of the cleaner V2 core

Scope:

- operator review queue
- correction overlays
- reviewed vs unresolved interpretation
- Review and Brain rebuilt off cumulative V2 memory

Done means:

- Hero can correct bad emphasis, bad interpretation, or false positives without corrupting canonical truth

## Big Step 6. MVP hardening

Goal:

- make the system dependable enough to use continuously

Includes:

- broader smoke tests
- fixture growth
- regression gates
- explicit startup/run docs
- stable repo conventions

Done means:

- V2 is not just promising, it is trustworthy

## What not to do before MVP

Do not prioritize these before the six steps above are substantially real:

- broad productization
- general-user onboarding
- marketing polish
- public landing work
- speculative integrations
- multi-user abstraction beyond what keeps schema future-safe

## MVP success test

The real MVP question is not:

- "Does this look like a product?"

It is:

- "Would Hero trust this to help improve his game this week?"

If the answer is yes, MVP is close.
