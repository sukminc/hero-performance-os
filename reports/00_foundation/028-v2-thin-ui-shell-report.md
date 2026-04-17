# TASK

Add a thin local UI shell inside the current repo so V2 can be used through Command Center, Session Lab, and Memory Graph before cutting over to an independent repo.

# WHAT I CHANGED

- Added a lightweight local dev server:
  - `app/dev_server.py`
- Added a thin static UI shell:
  - `app/ui/index.html`
  - `app/ui/styles.css`
  - `app/ui/main.js`

The shell now exposes:

- `/api/today`
- `/api/command-center`
- `/api/session-lab`
- `/api/memory-graph`

and a simple local UI with three panels:

- Command Center
- Session Lab
- Memory Graph

# ARCHITECTURE IMPACT

V2 now has an operator-facing shell that sits on top of the already-built read models without introducing a heavy framework dependency.

This is the right pre-cutover step because it proves:

- the read models are useful enough to look at regularly
- the product can be operated as a coherent system
- the eventual independent repo has a usable entrypoint, not only backend contracts

# DECISIONS MADE

- Used a thin Python stdlib HTTP server instead of adding a large frontend stack.
- Reused existing app-layer APIs instead of creating a separate transport layer.
- Kept the UI intentionally simple and inspection-oriented.

# RISKS / OPEN QUESTIONS

- This shell is local-first and not yet production-grade.
- The UI is intentionally thin and will likely evolve after the repo cutover.
- If the project later adopts a dedicated web framework in the standalone repo, this shell may become a temporary bridge rather than the final app shell.

# OUT OF SCOPE

- production deployment
- auth
- polished design system
- multi-user UX

# TEST / VALIDATION

- Python syntax validation should be run for `app/dev_server.py`
- The shell reuses existing API packets and should be tested locally by running the server and loading the UI in a browser

# RECOMMENDED NEXT STEP

The next major move should be the independent repo cutover for V2, using the already-defined cutover doc and carrying this shell forward as the first usable interface.
