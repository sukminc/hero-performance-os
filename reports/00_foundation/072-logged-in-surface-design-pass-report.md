# TASK

Improve logged-in OPB app readability and standout hierarchy after Task 70 / 71.

# WHAT I CHANGED

- Reworked global authenticated-app visual styling in `frontend/app/globals.css`.
- Increased text contrast across dark cards, status lists, JSON blocks, forms, pills, and navigation.
- Fixed the main readability issue where `.status-item` used a white background with light global text.
- Added stronger card borders, top accent bars, tighter shadows, and clearer heading scale.
- Added a `standout-card` treatment for the operator Big-Win Review section.
- Replaced the Big-Win Review JSON header with three readable result cards:
  - official result
  - linked session
  - review queue
- Kept the existing product structure and backend outputs unchanged.

# ARCHITECTURE IMPACT

No poker truth, auth, ingestion, memory, or operator review behavior changed.

This is a frontend presentation pass only. It makes the existing backend meaning easier to inspect without changing canonical data.

# DECISIONS MADE

- Used a darker control-room/felt visual direction rather than a generic white SaaS look.
- Prioritized readability over polish-heavy animations.
- Made the `#6408385` Big-Win Review stand out because it is the current proof point for result-aware operator review.

# RISKS / OPEN QUESTIONS

- This is still a first design pass, not final brand design.
- Some JSON-heavy sections remain verbose because deep operator mode intentionally exposes backend meaning.
- Browser-level visual QA was limited to server/build checks; the user should review the in-app browser and point out anything still hard to read.

# OUT OF SCOPE

- Full product redesign.
- New charting or hand-replayer UI.
- Consumer-ready visual simplification.
- Mobile-specific interaction redesign beyond responsive CSS improvements.

# TEST / VALIDATION

- `npm run typecheck`
- `npm run build`
- Restarted local dev server on `http://localhost:3000`.

# RECOMMENDED NEXT STEP

Next two tasks:

1. Operator reviews the updated `/operator`, `/app`, `/app/review`, and `/app/brain` screens and flags the hardest-to-read blocks.
2. Promote reviewed `repeatable_execution` big-win tags into positive execution memory once at least a few spots are manually tagged.
