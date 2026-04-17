# TASK

Analyze repeated AOF hand-class behavior and present it in product-style evidence cards rather than unsupported conclusions.

# WHAT I CHANGED

- Performed a provisional AOF re-read on `<=15bb`, `5+ active seats`, `Hero unopened preflop` spots from the canonical SQLite corpus.
- Re-tagged the sample into:
  - `standard_mtt`
  - `pko`
  - `satellite`
- Re-applied the provisional format-aware baseline family logic and focused on repeated hand-class families that had already been surfacing in discussion:
  - `KJo`
  - `low Ax offsuit`
  - `middling strength` hands such as `QJo`, `QTs`, `T9o`, `J8s`, `J9s`
- Converted the output into product-style evidence cards with:
  - repeated count
  - where observed
  - likely acceptable contexts
  - suspicious contexts
  - current confidence / validation status

# ARCHITECTURE IMPACT

- No code or schema changes.
- This report demonstrates how AOF analysis should become a product surface:
  - evidence-backed
  - count-backed
  - position-aware
  - format-aware
  - confidence-aware

# DECISIONS MADE

- Product-level pattern cards must not jump straight to verdict without counts.
- `KJo` must be split by position rather than treated as universally bad.
- `low Ax offsuit` must be treated as a mixed family, not a universal leak.
- `middling strength` hands should be treated as a family where early-position aggression is the main suspicion, not the hand class itself.

# RISKS / OPEN QUESTIONS

- This is still a provisional baseline read, not a final locked AOF engine.
- The baseline family itself still needs to be fixed in implementation, so current flags are evidence-backed hypotheses rather than final truth.
- Some contexts that surfaced as `special_context_defer` or `mixed` still need deeper validation before they should be turned into hard product coaching.

# OUT OF SCOPE

- No code implementation
- No UI implementation
- No parser changes
- No final baseline engine replacement

# TEST / VALIDATION

- No repo tests were run because this task was analysis/report only.
- Analysis was grounded in the canonical SQLite corpus:
  - `/Users/chrisyoon/GitHub/opb-poker/data/hero-v2/hero_v2.sqlite3`

# PRODUCT-STYLE EVIDENCE CARDS

## Card 1: `KJo` Usage Needs Position-Aware Validation

### Why this card exists

`KJo` was the clearest repeated hand-class family where the same aggressive approval pattern showed up across multiple positions and formats.

### Evidence summary

- total observed AOF spots with `KJo`: `15`
- provisional verdicts:
  - `too_loose`: `12`
  - `mixed`: `2`
  - `special_context_defer`: `1`

### Where it repeated

| Position | Repeated pattern |
|---|---|
| `HJ` | `5` `too_loose` spots |
| `UTG` | `3` `too_loose` spots |
| `cutoff` | `2` `too_loose`, `2` `mixed` |
| `UTG+1` | `1` `too_loose` |
| `LJ` | `1` `too_loose`, `1` `special_context_defer` |

### Format split

| Format | Read |
|---|---|
| `standard_mtt` | `5` `too_loose`, `2` `mixed` |
| `pko` | `4` `too_loose`, `1` `special_context_defer` |
| `satellite` | `3` `too_loose` |

### Likely acceptable contexts

- some `cutoff` usage appears inside a provisional `mixed` bucket
- one PKO near-jam spot surfaced as `special_context_defer` rather than clean miss

### Suspicious contexts

- `HJ` and `UTG` are the main concern
- the current read is not "KJo is always wrong"
- the current read is "early-position KJo aggression repeats often enough to require a stricter default"

### Product read

Hero appears to treat `KJo` as a pressure hand more often than the provisional baseline supports.

### Validation status

- `probable`
- requires final position-aware AOF baseline before being promoted to confirmed coaching truth

### Product-level adjustment candidate

- `KJo`: default back toward `fold` in early-position `<=15bb` unopened spots
- keep `cutoff/button` cases open for later validation rather than auto-rejecting them

## Card 2: Low `Ax` Offsuit Is Mixed, Not Universally Wrong

### Why this card exists

Low offsuit `Ax` was repeatedly discussed as a belief-driven attack family.
The corpus confirms that it is not a simple universal leak.

### Evidence summary

- total observed low `Ax offsuit` spots: `74`
- provisional verdicts:
  - `match`: `32`
  - `too_loose`: `25`
  - `special_context_defer`: `11`
  - `mixed`: `6`

### What this means

This family is split.
It is not strong evidence for "stop using low Ax."
It is stronger evidence for "stop approving low Ax automatically."

### Where it looks okay

- `UTG` and `UTG+1` contain a meaningful number of clean folds that scored as `match`
- several PKO spots surfaced as `special_context_defer`, which supports Hero's claim that some of these actions are format/context driven rather than random punts

### Where it looks suspicious

| Position | Repeated concern |
|---|---|
| `HJ` | `7` `too_loose` spots |
| `UTG` | `6` `too_loose` spots |
| `button` | `5` `too_loose` spots |
| `cutoff` | `3` `too_loose` spots |

### Format split

| Format | Read |
|---|---|
| `standard_mtt` | balanced but still `10` `too_loose` |
| `pko` | many deferred spots, supports contextual use |
| `satellite` | `10` `too_loose`, strongest overextension signal |

### Product read

Hero does not merely punt low `Ax`.
Hero uses it as a belief-driven exploit family.
That belief sometimes works, but it clearly overextends in some structures, especially `satellite`.

### Validation status

- `probable`
- should not be collapsed into one coaching sentence

### Product-level adjustment candidate

- low `Ax offsuit` should become:
  - `conditional attack family`
  - not `default approve family`
- strongest caution should be shown in `satellite`

## Card 3: Middling Strength Hands Are Mostly an Early-Position Problem

### Family definition

- `QJo`
- `QTs`
- `T9o`
- `J8s`
- `J9s`

### Evidence summary

- total observed spots in this family: `34`
- provisional verdicts:
  - `match`: `18`
  - `too_loose`: `13`
  - `mixed`: `3`

### Why this matters

This family is not universally wrong.
The repeated issue is more specific:

- early-position aggression is where the suspicion clusters

### Where it looks okay

- `cutoff`: `6` `match`
- `HJ`: `3` `match`
- multiple `UTG` folds also scored as `match`

### Where it looks suspicious

| Position | Repeated concern |
|---|---|
| `UTG` | `7` `too_loose` |
| `button` | `2` `too_loose` |
| `UTG+1` | `1` `too_loose` |
| `small blind` | `1` `too_loose` |

### Example suspicious patterns

- `UTG QJo open jam`
- `UTG J9s open jam`
- `UTG J8s open jam`
- `UTG T9o open jam`

### Product read

The family itself is not the leak.
The leak candidate is:

- approving "playable-looking" middling hands too early in the action order

### Validation status

- `probable`
- stronger than a vague suspicion because the repeated early-position cluster is visible

### Product-level adjustment candidate

- in `<=15bb` unopened spots, treat this family as:
  - `late-position conditional`
  - `early-position skeptical by default`

# SYNTHESIS

## What looks most product-ready right now

The best first product card is still:

- `KJo usage needs position-aware validation`

because it is:

- repeated enough
- cross-format
- clearly count-backed
- and still nuanced enough that it should not become an overconfident false conclusion

## What should not be over-simplified yet

- low `Ax offsuit`

This family is too mixed to flatten into one sentence.
It should be shown as a belief-driven conditional family, not a clean leak.

## Most credible current coaching sentence

If the product had to surface only one high-signal AOF coaching line from this report, it would be:

- `KJo is not a universal problem hand, but early-position KJo aggression under <=15bb keeps repeating often enough that it should default back toward fold until stricter baseline validation says otherwise.`

# RECOMMENDED NEXT STEP

Turn these into actual product cards with fields for:

- repeated count
- format split
- position split
- likely okay contexts
- suspicious contexts
- validation status
- default adjustment

# HANDOFF

- This report is the best example so far of how AOF analysis should become product output rather than chat-only interpretation.
- The next implementation should not just emit verdict counts.
- It should emit evidence-backed pattern cards in this structure.
