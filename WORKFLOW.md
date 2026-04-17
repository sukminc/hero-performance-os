# WORKFLOW.md

## Operating Model
- User = Product Owner / real-world pain provider / operator reviewer
- ChatGPT = CTO / architecture, prioritization, review, acceptance gate
- Claude Code or Codex = implementation engine

## Workflow Reset
The current bottleneck is not only implementation speed.
It is repeated conversational handoff overhead.

The workflow should therefore optimize for:

- less copy-paste,
- less conversational drift,
- clearer approval state,
- one active execution thread at a time,
- repo artifacts as truth instead of chat memory alone.

Chat is for direction, review, and escalation.
Repo files are for executable truth.

## Canonical Execution Artifacts
Every meaningful implementation loop should rely on three canonical artifacts:

1. task brief
2. implementation diff
3. report file

Chat conversation may help produce these artifacts, but chat itself is not the durable execution record.

If there is any conflict between remembered chat context and the current task brief / report pair, the task brief and report pair win until explicitly revised.

## Current Product Phase
The current phase is:

- backend-first,
- operator-first,
- truth-first,
- deep operator mode.

Consumer-facing frontend work remains blocked until the backend is trustworthy enough to:

- parse real GG Poker session packets reliably,
- preserve cumulative Hero-specific memory across uploaded sessions,
- produce usable Today / Review / Brain outputs,
- support operator review / tuning / Golden Rule / QA loops,
- and pass deterministic validation.

## Current Product Truth Rule
The system must not behave like stateless spot review.

The highest-priority product job is:

1. ingest one GG Poker session packet,
2. split and parse its hands,
3. extract session-level evidence,
4. connect that evidence to persistent Hero-specific memory,
5. accumulate meaning across sessions,
6. and update Today / Review / Brain accordingly.

The backend should answer:

- What happened in this session?
- What repeated leaks, stable strengths, or unusual shifts did it reveal?
- What should Hero do next because of it?

## Current Product Promise
The product is moving toward a workflow Hero would actually use:

- parse real GG session packets,
- remember them,
- calibrate repeated patterns,
- generate pre-tournament Today outputs,
- support post-session Review and cumulative Brain updates,
- and let the operator refine truth when the backend is partly right but not yet good enough.

The workflow should also preserve that:

- AOF analysis,
- `13x13` hand-class/result analysis,
- and EV / actual-result analysis

are baseline-building workflows for Hero.

They should help Hero study GTO material later from a stronger personal foundation rather than trying to replace that study layer directly.

## Development-Stage Display Rule
During development, expose more, not less.

Current mode is deep operator mode, which means:

- verbose evidence is acceptable,
- internal logic should remain inspectable,
- backend detection should be visible even if not yet elegant,
- and filtering or user-facing simplification should happen later.

The current goal is to prove that the system remembers and accumulates meaning.

## Positive Adjustment Rule
The product should not act like a judgment engine.

It should:

- diagnose clearly,
- preserve what was right and wrong,
- and convert diagnosis into next adjustment direction.

Working philosophy:

- the past cannot be changed,
- other people cannot be changed,
- only today’s Hero can be changed.

Therefore the workflow should prefer usable next adjustments over harsh grading.

The workflow should also prefer:

- repeated pattern plus result analysis

over:

- isolated memoryless solver-style scolding.

## Intervention Tracking Loop
The intended loop is:

recommendation -> application -> verification -> model update

That means:

1. the system proposes an action,
2. later sessions are parsed,
3. the backend tries to detect whether the recommendation was applied,
4. the operator can review/correct that judgment,
5. Hero's model is updated.

The operator loop now also includes reviewing the surface emphasis itself:

- original Today / Review / Brain emphasis is stored as immutable historical snapshot truth,
- the operator can confirm or correct that emphasis separately,
- reviewed emphasis is written as a lightweight overlay,
- cumulative summaries can reflect confirmed / corrected / unresolved emphasis status.

This is not merely a checklist.
It is an intervention tracking loop.

## Task Lifecycle
1. CTO writes or approves one scoped task brief.
2. The task brief must define:
   - business question
   - in-scope work
   - out-of-scope work
   - acceptance/validation expectation
   - required report path if execution proceeds
3. Implementation agent executes only scoped work.
4. Implementation agent updates code/docs, runs validation, and writes the required report file in `/reports/...`.
5. CTO reviews architecture impact, risks, determinism, and product fit using the report first.
6. User receives concise pass / reject / revise guidance.
7. If revised, the same task remains the active thread until accepted or explicitly superseded.

When architecture or product truth changes meaningfully, the implementation task should also update the core markdown context docs:

- `PROJECT_MASTER_CONTEXT.md`
- `AGENTS.md`
- `DECISIONS_LOG.md`
- and `WORKFLOW.md` when workflow truth changed

A task is not complete unless both are true:
- implementation files physically exist in the repo,
- and the exact required report file physically exists in `/reports/...`.

## Task Packet Rule
Do not rely on freeform conversational memory as the main task carrier once execution begins.

The active task should be understandable from its durable artifact set without replaying the whole conversation.

Minimum task packet:

- title
- objective
- scope
- constraints
- validation target
- report destination

If these are not clear, the task is not ready for execution.

## Execution Rule
Do not treat task creation as task completion.

Creating `tasks/...md` is only preparation.
A task is only considered executed when:

- code and/or docs are actually updated,
- validation is actually run,
- and the exact report file is actually written.

## Report-First Review Rule
The default loop is:

- task brief exists,
- implementation runs,
- report is generated,
- CTO reviews the report,
- user accepts, rejects, or narrows revision scope,
- then the next implementation step proceeds.

Prefer report review over long conversational recap.

## Revision Loop Rule
Revision should be narrow and stateful.

When a task is rejected or adjusted:

- revise the same active task if the business question is still the same,
- rewrite or extend the same report when appropriate,
- avoid spawning a brand-new conversational branch unless the objective materially changed.

The goal is to reduce repeated restatement of context.

## State Machine Rule
Each meaningful task should conceptually live in one of these states:

- proposed
- approved
- in_progress
- report_ready
- revision_requested
- accepted
- superseded

The workflow should minimize ambiguity about which state the active task is in.

## Multi-Task Planning Rule
It is acceptable to create several future task briefs in advance.
However:

- only one implementation task should be executed at a time unless explicitly planned otherwise,
- each executed task must still produce its own report,
- each task must still pass review before the next execution step is trusted.

Future tasks may be queued, but they should not compete with the currently active execution thread.

## Conversation vs Repo Truth Rule
Conversation is useful for:

- clarifying pain,
- discussing tradeoffs,
- approving direction,
- requesting revisions,
- choosing next steps.

Repo truth is required for:

- active task scope,
- implemented changes,
- validation evidence,
- architecture decisions,
- durable reports.

Do not let Slack, chat, or memory become the only place where execution truth lives.

## Slack / Automation Direction
Slack may later become an operator interface for:

- task submission,
- approval,
- report delivery,
- revision requests,
- next-step selection.

However, Slack should remain an interface layer, not the canonical system of record.

Any future automation should still write durable task/report artifacts into the repo or another structured truth layer before it is trusted.

## Operator Tuning Loop
The current MVP operator loop is:

1. Hero uploads one GG Poker session packet
2. Backend parses and splits hands
3. Backend produces:
   - session-level summary
   - session-wide evidence
   - repeated leak / strength candidates
   - cumulative Hero-model updates
   - Today / Review / Brain implications
4. Hero reviews output through operator tooling
5. Hero drafts or refines Golden Rules if needed
6. QA fixtures / evaluator coverage are updated as needed
7. Backend behavior is re-verified before any frontend work

## Today / Review / Brain Workflow Direction
- Today should become a pre-tournament action surface driven by cumulative calibration.
- Review should separate strategic truth, result significance, and recurring pattern meaning.
- Brain should become the cumulative Hero-specific interpretation surface, not generic self-help commentary.
- Today / Review / Brain may store immutable generation-time surface-emphasis snapshots.
- Operator-reviewed emphasis must remain a separate overlay rather than rewriting generation-time truth.

## GG Session Packet Rule
A GG Poker `.txt` upload is treated as a session packet, not an isolated single-spot input.

Required behavior:

- real file parsing must yield non-zero hands when the file contains hands,
- duplicate-safe ingestion must prevent the same file from being processed twice,
- different files must not collapse into the same session identity,
- zero-hand parse failures must not emit fake summaries, fake pattern evidence, fake cumulative updates, or fake Today / Review / Brain implications,
- repeated runs of the same file should remain materially stable.

## Golden Rule and Truth Management Rule
Golden Rules are operator-authored backend truth guidance, not diary notes.

Approved truth remains the only blocking regression truth.
Pending drafts must never silently become approved truth.
Operator-authored rules and real-case assets must remain:

- structured,
- inspectable,
- deterministic,
- auditable.

## Priority Order
### Tier 1 - Foundation
- schema
- ingestion model
- GG session parsing
- cumulative Hero memory
- context assembly model
- raw / normalized / derived separation

### Tier 2 - Product Core
- Today
- Review
- Brain
- operator-surface assembly and ranking
- session-level interpretation
- action generation
- operator inspection / tuning
- QA / evaluator / Golden Rule loops

### Tier 3 - Expansion
- field-model refinement
- live poker expansion
- planning domain
- coach / role-model overlays
- broader context inputs

### Tier 4 - Nice To Have
- consumer-facing frontend polish
- branding-first work
- low-value dashboards
- speculative integrations

## Frontend Blocking Rule
Consumer-facing frontend work remains blocked until the backend can reliably:

- ingest real GG session packets,
- accumulate Hero-specific memory across sessions,
- expose inspectable Today / Review / Brain outputs,
- support operator review and correction,
- and pass QA / regression checks with trustworthy outputs.
