# Task 099: Daily Matrix Quiz

## TASK

Implement Daily Hero Baseline Quiz V1 as an operator-only study surface on top of the existing 13x13 Matrix payload.

## WHAT I CHANGED

- Added `app/api/matrix_quiz.py` with deterministic daily quiz card generation from:
  - mandatory correction cards,
  - hidden value cards,
  - study panels,
  - and Matrix-cell fallback cards only when high-signal candidates are short.
- Added a Matrix Quiz service wrapper and `GET /v1/players/{player_id}/matrix/quiz?date=YYYY-MM-DD`.
- Added `getHeroBaselineQuiz(...)` to the frontend read boundary.
- Added `/operator/matrix/quiz` with a client-side recall flow:
  - partial stats first,
  - `Baseline / Watch / Leak / Value` answer choices,
  - answer reveal,
  - simple reaction logging.
- Added `logMatrixQuizAttempt(...)`, which writes attempts through the existing `operator_reviews` overlay path.
- Added a link from `/operator/matrix` to the Daily Quiz.
- Updated Matrix/decision docs to preserve the product rule that quiz attempts are learning overlays only.
- Added deterministic Matrix Quiz tests.

## ARCHITECTURE IMPACT

- Reuses Matrix as derived truth instead of duplicating hand parsing.
- Keeps quiz attempts as reviewed/learning overlays, not canonical player memory.
- Preserves raw / derived / reviewed-overlay separation.
- Keeps V1 Hero/operator-only and post-hoc; it is not live advice and not solver truth.

## DECISIONS MADE

- Daily quiz volume is fixed at 3 cards.
- Candidate source is high-signal Matrix candidates first, not random 169-hand noise.
- Quiz cards expose sample/context/action information before answer reveal but hide result metrics and grade until Hero chooses.
- `Watch` is the fallback grade for thin or mixed evidence to avoid fake precision.
- Attempt `decision` stores the selected grade; reaction and correctness live in `review_payload`.

## RISKS / OPEN QUESTIONS

- The frontend reveal is not meant as a secure exam boundary; this is an operator learning tool.
- Attempt history is stored, but the page does not yet show prior logged attempts for the same day.
- Reaction logging currently requires the user to click one reaction after revealing.
- Quiz attempts do not yet produce review candidates for repeated memory mismatch; that is intentionally deferred.

## OUT OF SCOPE

- No automatic Today / Brain / memory promotion from quiz misses.
- No consumer-facing quiz.
- No solver/GTO chart comparison.
- No new canonical schema table.
- No exact EV / ICM / PKO truth.

## TEST / VALIDATION

- `python3 -m py_compile app/api/matrix_quiz.py app/service/routes.py app/service/server.py`
- `python3 tests/matrix_quiz_tests.py`
- `python3 tests/service_boundary_tests.py`
- `python3 tests/v2_smoke_tests.py`
- `npm run build`
- Local payload smoke check returned 3 Hero-local cards for `2026-05-05`.

## RECOMMENDED NEXT STEP

Add same-day attempt readback so `/operator/matrix/quiz` can show which cards were already answered, then use repeated `memory_mismatch` reactions as operator-review candidates without automatically mutating Hero memory.
