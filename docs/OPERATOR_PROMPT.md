# Operator Prompt (copy/paste into a fresh session)

You are Codex, working on the Volunteer-Coordination-Platform repo. Read these rules and the current state before editing:

Rules
- No pin changes (style, size, thresholds) unless explicitly requested.
- Keep navbar minimal: brand left, hamburger far right, no search (Phase 4).
- Theme toggle sits bottom-left; small glass button.
- Background must be slightly lighter than the village ramp in both themes.
- Do not switch to union boundary unless instructed. Minor seam mismatch is acceptable.
- For any clipPath, use `clipPathUnits="userSpaceOnUse"` and a single path feature.
- One-pass-one-change with smoke tests (`/api/map-settings`, `/api/villages/pins`, `/api/blocks`).

Context to load
- Open `templates/index.html` and confirm: brand text, hamburger position, theme dock bottom-left, lighter background.
- Confirm search controls are absent.
- Validate API endpoints with a lightweight TestClient if available.

What to do next (if asked to implement)
- Phase 1: brand text, hamburger stability, bottom-left theme dock, Bhadrak label outside boundary.
- Phase 2: keep pins; tune background/value contrast only; avoid stacked shadows.
- Phase 3: zoom +/- only, reset hidden; footer polish.
- Phase 4: add expanding search (left of brand), debounced typeahead from `/api/villages`.
