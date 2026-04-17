# DECISIONS_LOG.md

## Fixed Decisions

### Product
- Product is a paid poker performance system for serious tournament players, beginning with Hero.
- The product analyzes the player, not just the hand.
- The key promise is Many Inputs -> One Brain -> One Next Move.
- The product is not a test of how much GTO Hero has memorized.
- The product should use AOF analysis, `13x13` hand-class analysis, and EV / actual-result analysis to build Hero's personal baseline.
- The product should help Hero get more value from later GTO Wizard study rather than trying to replace that study.
- The highest-priority product job is persistent Hero-specific interpretation across uploaded GG Poker session packets.
- A GG Poker `.txt` upload is treated as a session packet, not as an isolated single-spot review input.
- The system must not behave like stateless hand review.
- OPB is a post-hoc poker intelligence workbench, not real-time assistance and not RTA.
- Frontend remains blocked until backend truth is trustworthy.

### Architecture
- Postgres remains the canonical source of truth for core product state, pattern memory, and action surfaces.
- Supabase may be used for lead capture, access control, and other edge operational workflows, but not as canonical player/session/memory truth.
- Vector/RAG is secondary retrieval only.
- Source systems are metadata, not core business entities.
- raw / normalized / derived separation is mandatory.
- state / pattern / action is the core product loop.
- Tournament sample meaning must be modeled deterministically, not inferred later from raw all-events listings.
- Core performance, non-core noise, and seat-acquisition context must remain distinct tournament truth categories.
- Alpha filter profiles and review priority should consume canonical tournament truth rather than freeform or sidecar logic.
- GG session-packet parsing and cumulative Hero-memory updates are core MVP architecture priorities.
- Different uploaded GG files must not collapse into the same session identity.
- Duplicate GG session files must not be processed twice.
- Zero-hand parse results must not emit fake summaries, fake pattern evidence, fake cumulative updates, or fake Today / Review / Brain implications.
- GG anonymized opponent IDs are not valid cross-tournament persistent identity keys.
- Opponent memory uses tournament-scoped ephemeral identity plus cross-session archetype memory.
- Smart HUD is snapshot / delta / trend based, not static cumulative only.
- Hero analysis is decision-node and hand-class based, not result-only hand review.
- Economic and phase-aware interpretation uses deterministic proxy layers, not exact solver / ICM / PKO truth.
- Positive execution memory is first-class product memory, not only leak memory.
- Today / Review / Brain are canonical operator-facing assembly surfaces built from deterministic derived layers.
- Tournament segmentation, relevance weighting, review units, alpha surfaces, and validation runs must read from canonical Postgres tables rather than local JSON mirrors.
- Local JSON tournament artifacts are allowed only as explicit debug/export mirrors written after canonical Postgres persistence succeeds.

### MVP
- MVP surfaces are Today, Review, Brain.
- Operator-facing inspection and tuning come before consumer-facing frontend work.
- Real GG session parsing, session-level interpretation, cumulative Hero-specific memory, and calibration-driven action output are part of the MVP core.
- Tournament-scoped opponent memory, Smart HUD trend memory, Hero decision memory, and phase/economic judgment are all part of the backend truth stack that feeds MVP surfaces.
- Tournament segmentation, relevance weighting, retry-chain interpretation, and alpha tournament insight surfacing are part of the operator-first MVP truth stack.
- Do not expand planner / wearables / coach overlays / speculative integrations into MVP core unless done as compatible extensions.

### Today Philosophy
- Today is no longer generic advice.
- Today should become a pre-tournament action surface.
- Today should use cumulative calibration rather than one-session noise alone.
- Repeated leaks should outweigh low-confidence observations.
- Stable strengths should be treated as baseline context rather than overpraised every session.
- Bounded action language is acceptable when evidence supports it.
- Do not fake precision when evidence does not support it.

### Review Philosophy
- Review must stay grounded, cumulative, and inspectable.
- Review should separate strategic truth, result significance, and Hero-specific recurring patterns.
- Review should not collapse into generic hand grading.

### Brain Philosophy
- Brain is not generic self-help commentary.
- Brain is not just a leak list.
- Brain is the cumulative Hero-specific interpretation surface.
- Brain should use recent-state plus long-term-baseline comparison.
- Brain should favor Standard and Unusual as structural categories over naive strengths vs weaknesses alone.
- Stable strengths should become baseline/default rather than being overpraised every session.
- Unusual shifts should be surfaced when they matter.
- Brain tournament sample-mix summaries should reflect true include-level serious sample members, not down-weighted context that remains visible only for operator inspection.

### Positive Adjustment Principle
- The product should not feel like pure right/wrong grading.
- The product should not feel like pure GTO scolding.
- The product should not amplify self-blame.
- The system should diagnose clearly and convert diagnosis into next adjustment direction.
- The product is an adjustment engine, not a judgment engine.
- Only today’s Hero can be changed, so usable next adjustments matter more than harsh grading.

### Tracking / Intervention Loop
- The intended loop is recommendation -> application -> verification -> model update.
- The backend should auto-judge first where possible.
- Operator correction remains available.
- This loop is not just a checklist; it is intervention tracking.
- Generation-time surface-emphasis snapshots for Today / Review / Brain are immutable historical truth artifacts.
- Operator-reviewed surface emphasis must be stored as a separate overlay, not by mutating the original snapshot.
- Downstream logic may use reviewed emphasis status, but must preserve original snapshot truth.
- Operator review of emphasis itself is part of the truth-management model, not a side-channel note system.

### Development Display Mode
- During development, the backend should expose more, not less.
- The current mode is deep operator mode.
- Verbose internal detection is acceptable while backend truth is still being proven.
- Filtering and consumer-facing simplification come later.

### Interpretation
- High emotional weight events must be modeled separately from ordinary hand reviews.
- Strategic truth and emotional/career significance must be separable.
- Official pattern scoring must remain deterministic / structured, not pure LLM output.
- Repeated pattern plus real result should be treated as more important than isolated solver-style hand judgment.
- Strategic beliefs behind repeated hand-class usage should be inspectable when the evidence supports them.
- Spot review alone is insufficient; sessions should be interpreted as cumulative evidence.
- The backend must answer what repeated leaks, stable strengths, unusual shifts, and model updates a session adds to Hero.
- Interpretation should join hand class, stack depth, tournament phase, bounty context, cover / covered geometry, villain type, and Hero history where support exists.
- Positive execution examples should be preserved alongside leak patterns so the model remembers what to keep, not only what to cut.

### Field Understanding Direction
- Hero model comes first.
- Field model comes second, with importance increasing as more online data accumulates.
- For online GG, future field understanding may include anonymous action-driven pool interpretation, limp density, passive field texture, fish density, stake ecology signals, and exploitability patterns.
- These are current direction targets, not claims of full implementation.

### Coach / Role-Model Compatibility
- Coach or role-model overlays may exist later.
- Coach overlays must not alter truth.
- Coach layers should change explanation style, not canonical interpretation.

### Operating Protocol
- ChatGPT acts as CTO / reviewer.
- Implementation agent must provide structured reports after each meaningful task.
- No feature expansion without explicit architecture review.
- Conversational context alone is not the canonical execution record once implementation begins.
- Durable task briefs and report artifacts are the default execution truth layer.
- Revision should stay attached to the same active task when the underlying business question is unchanged.
- Slack or other chat tools may become interface layers later, but they must not replace repo-based execution truth.

### Truth Management
- Approved truth remains the only blocking regression truth.
- Pending drafts must never silently become approved truth.
- Golden Rules are operator-authored backend truth guidance, not diary notes.
- Golden Rules, gold cases, translated fixtures, and operator-authored truth assets must remain structured, inspectable, deterministic, and auditable.
- Original historical surface-emphasis snapshots must remain inspectable, deterministic, and auditable.
- Reviewed emphasis overlays must remain separately inspectable and auditable.

### Current Priority Rule
- When priorities conflict, prefer stronger backend truth, stronger GG session parsing, stronger cumulative Hero memory, stronger operator inspection/tuning, stronger actionability in Today / Review / Brain, and stronger QA determinism over consumer-facing polish or speculative expansion.
