# TASK

Prototype a browser-viewable field ecology operator surface that shows red-label pool behavior and Hero's limp-multiway response.

# WHAT I CHANGED

- added a new read-only API at `app/api/field_ecology.py`
- added a new `Field Ecology` tab to the local operator shell
- implemented first-pass ecology cards for:
  - limper rate
  - donk flop rate
  - limp-shove rate
  - open 4x rate
  - multiway flop rate
- added a `Hero In Limp-Multiway` block to summarize Hero reaction mix in limp-heavy multiway textures
- added last-7-days-by-format split for ecology context

# ARCHITECTURE IMPACT

- this is a read-only operator-grade surface built directly from canonical raw hand blocks
- it does not yet persist canonical field-snapshot tables
- it establishes the product direction for red-label field ecology without blocking future canonical field layers

# DECISIONS MADE

- focused on the clearest red-label markers first instead of trying to recreate a full commercial HUD ecology engine
- treated field ecology as context that should be inspectable alongside AOF, 13x13, and HUD trend
- included Hero limp-multiway reaction because the user explicitly wants field behavior and personal response in the same loop

# RISKS / OPEN QUESTIONS

- limp, donk, and open-size detection are heuristic from raw text rather than a dedicated state machine
- multiway classification is intentionally simple in v1
- `vpip 50+ fish density` still needs a stronger player-level anonymous-opponent estimator to be modeled exactly

# OUT OF SCOPE

- persistent opponent HUD tracking
- per-opponent red-label classification
- long-horizon anonymous pool clustering
- exact postflop node EV interpretation

# TEST / VALIDATION

- route and payload implemented against canonical SQLite
- local UI integration added
- feature remains read-only

# RECOMMENDED NEXT STEP

Connect field ecology to study outputs so repeated bad decisions can be reviewed with context such as `this happened in limp-heavy multiway pools` instead of being interpreted in isolation.
