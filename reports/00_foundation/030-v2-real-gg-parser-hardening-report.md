# TASK

Improve parsing quality so V2 handles real GG-style hand-history files more reliably and reports parse quality more honestly across real-style parses, simplified fixture fallback parses, and zero-hand failures.

# WHAT I CHANGED

- Updated [core/parsing/gg_parser.py](/Users/chrisyoon/GitHub/hero-performance-os/core/parsing/gg_parser.py) to:
  - accept a wider range of GG-style hand headers with optional spacing and optional button ante fields
  - parse Hero stack rows more robustly when seat rows include bounty text
  - count flop participants from action lines instead of hardcoding a generic value when flop actions are available
  - label parsed hands with `header_format` so real-style and simplified fallback paths stay explicit
  - emit richer parse quality metadata, including `parser_mode`, `real_style_block_count`, and `simple_block_count`
- Updated [core/parsing/parse_quality.py](/Users/chrisyoon/GitHub/hero-performance-os/core/parsing/parse_quality.py) to:
  - distinguish `fixture_fallback` from strong real-style parser success
  - preserve honest `failed_zero_hands` behavior
  - expose parser mode and block counts in the confidence summary
- Added a stronger real-style fixture at [fixtures/gg_session_sample_real.txt](/Users/chrisyoon/GitHub/hero-performance-os/fixtures/gg_session_sample_real.txt).
- Expanded [tests/v2_smoke_tests.py](/Users/chrisyoon/GitHub/hero-performance-os/tests/v2_smoke_tests.py) to:
  - assert the stronger real-style GG fixture parses through the primary parser path
  - verify parsed Hero position, stack-in-BB, and flop-player counting
  - verify the simplified sample remains clearly marked as `simple_fixture_fallback`

# ARCHITECTURE IMPACT

This keeps the current architecture intact while tightening truthfulness at the parser boundary.

- The ingest -> evidence -> memory -> surfaces chain remains unchanged.
- Parser output now carries clearer provenance about whether a session came through the real GG parser path or the simplified fallback path.
- Session confidence summaries are more inspectable, which is important for operator review and for preventing fake confidence on non-real fixtures.

# DECISIONS MADE

- Real GG-style parsing should be treated as the primary success path.
- Simplified fixture parsing should remain supported for smoke coverage, but it must be explicitly labeled as fallback rather than masquerading as full parser success.
- Parse quality should report partial success vs fallback vs zero-hand failure directly in structured metadata instead of relying on implicit interpretation.

# RISKS / OPEN QUESTIONS

- The parser is more tolerant now, but it is still a lightweight transition parser rather than a full GG grammar.
- More real exported GG files are still needed to pressure-test edge cases such as alternate seat text, unusual summary sections, and other tournament variants.
- `players_to_flop` remains a proxy derived from observed flop actions, which is useful but still not a full table-state reconstruction.

# OUT OF SCOPE

- evidence scoring changes
- memory ranking/state logic changes
- Today / Review / Brain logic changes
- UI changes beyond existing read-path exposure

# TEST / VALIDATION

- Ran `python3 tests/v2_smoke_tests.py`
- Result: `V2 smoke tests passed.`
- Verified the stronger real-style fixture parses as `gg_real`
- Verified the simplified sample remains explicitly labeled `fixture_fallback`
- Verified duplicate-safe and zero-hand-safe behavior still pass in smoke coverage

# RECOMMENDED NEXT STEP

Move to evidence quality improvement:

- tighten hand-class underperformance evidence
- improve style drift and contamination signals
- improve evidence ranking/explanation quality so memory and Today usefulness can improve on top of the stronger parser boundary
