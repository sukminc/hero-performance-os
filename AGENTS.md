# AGENTS.md

## Read First
Before making architecture, schema, product, parsing, QA, or workflow decisions, read:
- `PROJECT_MASTER_CONTEXT.md`
- `WORKFLOW.md`
- `DECISIONS_LOG.md`

## Product Identity
This repository is for a paid poker performance system for serious tournament players, starting with Hero as the first and highest-priority user.

It is not:
- a generic poker app
- a solver clone
- a live in-hand advisor
- an RTA system
- a generic chatbot
- a stateless hand-review tool

## Current Product Priority
At the current MVP stage, the highest-priority product job is persistent Hero-specific interpretation across uploaded GG Poker session packets.

A GG Poker `.txt` upload is treated as a session packet, not as an isolated single-spot review input.

The system must:
1. parse the uploaded session packet,
2. split and classify hands,
3. extract session-level evidence,
4. connect that evidence to persistent Hero-specific memory,
5. update cumulative interpretation instead of resetting review each time,
6. and surface operator-reviewable Today / Review / Brain outputs.

Current strategic emphasis should also recognize that:

- AOF analysis,
- `13x13` hand-class analysis,
- and EV / actual-result analysis

are core baseline-building tools, not optional extras.

They exist to help Hero understand repeated personal patterns first, then study GTO from a stronger base.

## Core Rule
The system must help one paying user:
1. capture many inputs,
2. structure them into one persistent player model,
3. diagnose recurring patterns,
4. interpret high-weight events,
5. preserve cumulative memory across sessions,
6. and generate one clear next action.

## Architecture Rules
- Model by entities, not by vendors or tools.
- Separate raw, normalized, and derived layers.
- Keep state, pattern, and action as the core product loop.
- Store source systems as metadata/provenance, not as core business objects.
- Use vector search only for contextual recall.
- Use Postgres as canonical product truth.
- Supabase may be used for lead capture, access control, and operator-side edge workflows, but must not become canonical player/session/memory truth.
- Use minimal raw SQL patterns rather than heavy ORM complexity unless explicitly required later.
- Use LLMs for explanation, summarization, extraction, and coaching language.
- Do not use LLM output as source of truth for official scores or state.
- GG session-packet parsing and cumulative Hero-memory updates are core MVP architecture priorities.
- Different uploaded GG files must not collapse into the same session identity.
- Duplicate GG session files must not be processed twice.
- Zero-hand parse results must not emit fake summaries, fake pattern evidence, fake cumulative updates, or fake Today / Review / Brain implications.
- GG anonymous opponent IDs must not be treated as cross-tournament persistent identity.
- Opponent memory should use tournament-scoped ephemeral identity plus cross-session archetype memory.
- Preserve provenance and confidence in surfaced outputs.
- Prefer deterministic post-hoc interpretation over fake exactness.
- Use proxy language explicitly when phase, payout, bounty, ICM, or PKO truth is only partially supported.

## Product Philosophy Rules
- The product is an adjustment engine, not a judgment engine.
- Diagnose clearly, but convert diagnosis into usable next adjustment.
- Do not reduce the system to right/wrong grading or GTO scolding.
- Do not build the product as a memory test for how much GTO Hero already knows.
- Use GTO as baseline calibration, not as the only product voice.
- AOF analysis and `13x13` hand-class/result analysis should help Hero build a personal strategic baseline for later study.
- Stable strengths should become baseline/default, not endless praise.
- Unusual shifts matter when they reveal something worth remembering.
- During development, expose more backend meaning rather than hiding it too early.
- Positive execution memory is first-class product memory, not just a nice-to-have after leak finding.

## Today / Review / Brain Rules
- Today should become a pre-tournament action surface driven by cumulative calibration.
- Today should prefer repeated leaks over one-off noise and may use bounded action language when evidence supports it.
- Today / Review / Brain should now be assembled from the canonical deterministic derived layers rather than improvised one-off summaries.
- Review should stay cumulative, grounded, and specific to Hero rather than generic grading.
- Brain is not generic self-help commentary and not just a leak list; it is the cumulative Hero-specific interpretation surface.
- Brain should support:
  - situation-aware headline
  - Hero Standard
  - Hero Unusual
  - repeated leaks + fixes
  - field understanding direction
  - situation/context interpretation
  - longitudinal update

## Tracking / Intervention Rule
The intended loop is:

recommendation -> application -> verification -> model update

The backend should auto-judge first where possible.
Operator correction remains available.

## MVP Scope
Prioritize only:
- Today
- Review
- Brain
- AOF baseline analysis
- `13x13` hand-class / result analysis
- GG session-packet ingestion
- hand splitting and session-level interpretation
- cumulative Hero-memory updates across sessions
- operator-facing inspection and tuning
- Golden Rule / QA / evaluator loops

## Frontend Rule
Consumer-facing frontend work is blocked until the backend can reliably:
- parse real GG Poker session packets,
- preserve cumulative Hero-specific memory across uploaded sessions,
- expose inspectable session summaries, pattern evidence, cumulative updates, and actionable Today output,
- support operator-side review, tuning, and Golden Rule formalization,
- and pass deterministic QA / regression checks.

## Expansion Rules
Future features such as:
- planning / travel
- coach overlays
- role-model overlays
- wearables
- external integrations

must extend the model without breaking canonical truth.

## Implementation Bias
Prefer the smallest shippable implementation that preserves future compatibility.
Prefer stronger backend truth, stronger GG session parsing, stronger cumulative Hero memory, stronger operator inspection/tuning, stronger Today / Review / Brain usefulness, and stronger QA determinism over consumer-facing polish or speculative expansion.
Prefer context-rich post-hoc interpretation through phase, bounty economics, stack geometry, villain type, hand class, and Hero history where those layers are available.

## Forbidden Patterns
- source-specific core tables (example: `chatgpt_notes`, `whoop_data`, `youtube_notes`)
- vector-first truth systems
- direct LLM answers without context assembly
- persona-specific truth tables
- overengineered integrations before core interpretation works
- stateless spot-review behavior that ignores prior Hero memory
- live in-hand assistance behavior or anything that could be interpreted as RTA
- fake pattern/summarization output when real parsing failed
- duplicate processing of the same GG session file
- fake precision when the evidence does not support it

## Required Thinking Pattern
Every change should answer:
- What business question does this table/service answer?
- Does it help Hero understand repeated personal patterns and their real outcomes?
- Does it strengthen Hero's personal baseline before later GTO study?
- Does it strengthen memory, diagnosis, or next action?
- Does it improve GG session parsing, cumulative Hero memory, or operator review quality?
- Does it help Today / Review / Brain become more useful and more believable?
- Can it support future expansion without schema rework?
- Does it preserve structured truth?
- Does it avoid turning the system into generic spot review?
- Does it preserve confidence, provenance, and post-hoc framing on surfaced outputs?

## Truth Management Rules
- Approved truth remains the only blocking regression truth.
- Pending drafts must never silently become approved truth.
- Golden Rules are operator-authored backend truth guidance, not diary notes.
- Golden Rules, gold cases, and translated fixtures must remain structured, inspectable, deterministic, and auditable.

## Operator-First Rule
Before any consumer-facing frontend work, the system must provide operator-facing tooling that lets Hero:
- upload GG session packets,
- inspect parsing quality,
- inspect session summaries,
- inspect repeated leak / strength candidates,
- inspect positive execution candidates,
- inspect phase / bounty / economic interpretations,
- inspect cumulative Hero-model updates,
- inspect pre-tournament Today actions,
- draft/refine Golden Rules,
- and approve, reject, or refine backend interpretation safely.

## Reporting Requirement
After each meaningful task, report back with:
- TASK
- WHAT I CHANGED
- ARCHITECTURE IMPACT
- DECISIONS MADE
- RISKS / OPEN QUESTIONS
- OUT OF SCOPE
- TEST / VALIDATION
- RECOMMENDED NEXT STEP

## Workflow Execution Rules
- Do not treat chat memory alone as the active task source once execution begins.
- Prefer a durable task brief plus report pair over repeated conversational restatement.
- If a task is being revised but the business question did not change, continue the same execution thread rather than branching into a brand-new task.
- If conversation, task brief, and report diverge, escalate and realign before continuing implementation.
