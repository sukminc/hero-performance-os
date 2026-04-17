# Founder Origin

OPB was not created as a trend-chasing AI demo.
It came from real pressure, repeated poker pattern recognition, and a belief that a serious player should have a system that actually remembers.

Hero spent years in QA, data, and systems-oriented work while also taking poker seriously as a long-term performance pursuit.
The product insight is simple:

- poker creates repeated strategic and emotional mistakes,
- those mistakes are often reviewed in isolation,
- and isolated review is not enough to change a player over time.

OPB exists to close that gap.

---

# Current Product Identity

OPB is:

- backend-first,
- operator-first,
- truth-first,
- Hero-model-first.

It is not:

- a generic poker chatbot,
- a solver clone,
- a live action advisor,
- a real-time assistance system,
- a hand-history browser,
- a stateless hand-review tool,
- or a polished consumer frontend product.

At the current stage, the product must behave like cumulative Hero-specific poker memory.

---

# Current Product Promise

The product is moving toward a usable loop that Hero would actually want before and after the next tournament:

1. parse real GG Poker session packets,
2. extract session-level evidence,
3. accumulate Hero-specific memory across sessions,
4. produce Today / Review / Brain outputs,
5. support operator review, tuning, Golden Rule drafting, and QA loops,
6. and become a real adjustment engine rather than a generic review toy.

The first user is Hero.
The first standard is usefulness, not presentation.

---

# Product Principle

The product is not trying to prove how much GTO Hero has memorized.

It is trying to:

- capture Hero's repeated patterns,
- measure the real outcomes of those patterns,
- interpret the beliefs behind those patterns,
- and build a personal strategic baseline that makes later study more grounded.

That means AOF analysis, `13x13` hand-class analysis, and EV / actual-result analysis are not optional side features.
They are core tools for building Hero's baseline.

The intended study loop is:

1. detect repeated pattern,
2. measure real result,
3. interpret the underlying belief,
4. tighten the personal baseline,
5. then study GTO material from a much stronger foundation.

The product is therefore not a GTO Wizard replacement.
It is the baseline-building layer that helps Hero get far more value from later GTO Wizard study.

---

# MVP Core Input Rule

The highest-priority real input is a GG Poker session packet.

A GG `.txt` file is treated as:

- one session packet,
- containing multiple hands,
- containing multiple pieces of evidence,
- and contributing to persistent Hero-specific memory.

It is not treated as isolated spot review.

The backend must try to answer:

- What happened in this session?
- What repeated leaks or stable strengths did it reveal?
- What does this add to Hero's model?
- What should Hero do differently next?

---

# Product Truth

OPB is a poker performance system for serious tournament players, beginning with Hero.

Its core job is:

- many inputs,
- one player model,
- repeated diagnosis,
- cumulative memory,
- one next adjustment.

The system must:

- remember what prior GG session packets added to Hero's model,
- separate strategic truth from emotional carryover,
- preserve raw, normalized, and derived truth layers,
- keep core player/session/memory truth in Postgres,
- allow Supabase for edge operational systems such as lead capture, access control, or tester operations without promoting it into core player/session/memory truth,
- model opponents as tournament-scoped anonymous identities plus longer-horizon archetype memory,
- model Hero through decision nodes, hand classes, stack bands, and context rather than result-only hand review,
- interpret bounty vs non-bounty thresholds, cover / covered geometry, and tournament phase through deterministic proxy layers when exact truth is unavailable,
- use AOF analysis and `13x13` hand-class/result analysis as first-class operator surfaces for baseline-building,
- preserve positive execution memory as well as leak memory,
- assemble operator-facing Today / Review / Brain surfaces from the derived layers,
- and produce inspectable outputs rather than opaque AI commentary.

The product must not behave like stateless hand review.
The product must not behave like live in-hand assistance.

---

# Positive Adjustment Principle

OPB is not intended to feel like:

- pure right/wrong grading,
- pure GTO scolding,
- negative failure tracking,
- or self-blame amplification.

Instead, it should:

- diagnose clearly,
- preserve the truth of what was good and bad,
- and convert diagnosis into usable next adjustment.

Core philosophy:

- some things were right in that spot,
- some things were wrong in that spot,
- the past cannot be changed,
- other people cannot be changed,
- only today’s Hero can be changed.

Therefore the product should emphasize adjustment direction over harsh grading.

---

# Brain Philosophy

Brain is not generic self-help commentary.
Brain is not just a leak list.

Brain is the cumulative Hero-specific interpretation surface.
It should create the feeling:

"the system has read my sessions, understands my tendencies, and will remember this."

Brain should evolve around:

- situation-aware headline,
- Hero Standard,
- Hero Unusual,
- repeated leaks + fixes,
- positive patterns worth reinforcing,
- field understanding,
- situation/context interpretation,
- phase / bounty / geometry interpretation,
- longitudinal update.

Stable strengths should become baseline/default rather than getting overpraised every session.
Unusual shifts should be surfaced when they matter.

---

# Today Philosophy

Today is no longer generic advice.
It should become the pre-tournament action surface.

Today should:

- use cumulative calibration,
- prioritize repeated leaks over one-off noise,
- treat stable strengths as baseline context,
- include positive reminders when they protect against over-correction,
- surface economic and phase-sensitive cautions when evidence supports them,
- allow bounded action language when justified,
- and include both the action and why that action matters.

Examples are acceptable when evidence supports them:

- defend BB more,
- look for 1-3 more river pressure opportunities,
- reduce threshold over-commitment,
- preserve baseline discipline without over-focusing on it.

But the product must not fake precision if the evidence does not support it.

---

# Tracking / Intervention Loop

The intended loop is:

recommendation -> application -> verification -> model update

This is not meant to be a static checklist.
It is an intervention tracking loop.

The backend should:

1. propose an action,
2. parse the next session or sessions,
3. try to detect whether the intervention was actually applied,
4. let the operator review or correct that judgment,
5. and update Hero's model accordingly.

---

# Development-Stage Display Principle

During development, the backend should expose more, not less.

The current mode is deep operator mode.
That means:

- verbose detection is acceptable,
- internal evidence should stay visible,
- operator inspection comes before user-facing simplification,
- filtering and compression come later,
- and the current goal is to prove that the system remembers and accumulates meaning.

---

# Field Understanding Direction

Current priority remains:

1. Hero model first
2. field model second

Field understanding matters more as more online GG data accumulates.
For online GG, future field understanding may include:

- anonymous action-driven pool interpretation,
- limp density / passive field texture,
- fish density,
- stake ecology signals,
- exploitability patterns.

This is a direction and interpretation target, not a claim that the field model is fully implemented today.

---

# Current Interpretation Scope

The current backend is expected to support interpretation across:

- tournament-scoped opponent memory,
- archetype-driven field understanding,
- Smart HUD snapshots, deltas, and trends,
- tournament-context tagging,
- Hero decision-node and hand-class memory,
- shove-drift and repeated-spot memory,
- phase-aware and bounty-aware economic judgment,
- positive execution memory,
- and operator-facing Today / Review / Brain assembly.

These layers must remain deterministic, inspectable, and confidence-aware.
When exact monetary or equilibrium truth is unavailable, the system should prefer explicit proxy language over fake precision.

---

# Coach / Role-Model Compatibility

The current system is Hero-centric.

Future expansion may include:

- coach overlays,
- role-model overlays,
- alternate explanation voices.

Those future layers must stay compatible with the current model, but they must not change truth.
Current implementation priority remains Hero + GG online session understanding.

---

# MVP Boundaries

Current MVP surfaces:

- Today
- Review
- Brain

Current MVP core capabilities:

- real GG session-packet ingestion,
- hand splitting and parsing,
- session-level evidence extraction,
- cumulative Hero-memory updates,
- tournament-scoped opponent memory and archetype analysis,
- Smart HUD snapshot / delta / trend memory,
- Hero decision-node, hand-class, and repeated-spot memory,
- phase-aware and bounty-aware economic interpretation,
- positive execution reinforcement memory,
- deterministic Today / Review / Brain assembly,
- operator review / tuning,
- Golden Rule and QA loops,
- grounded Today / Review / Brain outputs.

Out of scope for MVP core:

- polished consumer-facing frontend,
- branding-first work,
- generic assistant behavior,
- overbuilt solver infrastructure,
- speculative integrations that do not strengthen memory, diagnosis, or next action.

Frontend remains blocked until backend truth is trustworthy.

---

# Non-Negotiable Rules

Do not weaken these rules:

- backend-first / operator-first / truth-first
- GG session-packet priority
- cumulative Hero-specific memory over stateless review
- duplicate-safe ingestion
- zero-hand fake output prohibition
- approved truth vs pending truth distinction
- frontend blocked until backend truth is trustworthy

---

# Success Criteria

The MVP is successful if:

- Hero wants to use it repeatedly,
- real GG session packets parse reliably,
- cumulative memory becomes believable,
- Today / Review / Brain become genuinely useful,
- repeated mistakes are diagnosed and tracked,
- next adjustments become clearer before the next tournament,
- and the operator/QA loop makes backend truth stronger over time.

The MVP does not need investor-demo polish.
It needs to become trustworthy first.
