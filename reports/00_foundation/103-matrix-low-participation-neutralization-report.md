# Task 103: Matrix Low Participation Neutralization

## TASK

Prevent very low participation hand classes, such as `83o` with `1 played / 219 dealt`, from looking like meaningful Matrix performance signals.

## WHAT I CHANGED

- Added `participation_rate_pct` to every Matrix cell.
- Added `low_participation` to every Matrix cell.
- Defined low participation as less than `5%` voluntary participation among dealt hands.
- Low-participation cells now use `style_tone = low-participation` and `stack_style_tone = low-participation`.
- Updated deterministic `english_read` so low-participation hands read as exposure context, not wins/leaks/value.
- Updated pinned detail to show Play Rate and mark low-participation hands as neutralized.
- Hid the position/result driver table for low-participation hands so tiny samples are not over-analyzed.
- Updated Matrix CSS so low-participation cells render as white/neutral instead of red/green.
- Added regression coverage for sub-5% participation neutralization.
- Updated Matrix docs and decision log with the low-participation rule.

## ARCHITECTURE IMPACT

This keeps Matrix interpretation deterministic and makes participation rate a first-class derived signal.

No canonical hand/session truth changes. The raw and derived result metrics remain available, but the visual emphasis now correctly prioritizes high-participation performance signals.

## DECISIONS MADE

- The Matrix should prioritize hands Hero actually plays.
- Less than `5%` participation is exposure context.
- Low-participation hands should not compete visually with red leak cells or green value cells.
- Pinned detail should not show a full position/result diagnostic for tiny played samples.

## RISKS / OPEN QUESTIONS

- The `5%` threshold is product-driven and may need adjustment later.
- Some rare but strategically important hands could be muted until enough participation accumulates.
- Future versions may need separate filters for `show all exposure` versus `performance only`.

## OUT OF SCOPE

- No solver/GTO comparison.
- No change to canonical hand parsing.
- No correction-candidate rewrite.
- No membership/upload gating.

## TEST / VALIDATION

- Local 83o payload smoke check:
  - `1 played`,
  - `219 dealt`,
  - `0.5% participation`,
  - `low_participation = True`,
  - `style_tone = low-participation`,
  - `english_read.stance = low_participation`.

## RECOMMENDED NEXT STEP

Add a Matrix toggle later for `Performance only` versus `All dealt exposure`, with `Performance only` as the default product view.
