# AGENTS.md — Working Agreements for This Repo (Nov 2025)

- Always create a lightweight checkpoint tag before nontrivial UI changes; revert cleanly if needed.
- One-pass-one-change: implement a single, testable change; take a screenshot; smoke endpoints.
- Pins are out of scope unless explicitly requested; do not change pin style/visibility/size.
- Use exact anchors for template edits; avoid broad regex replacements across large files.
- Navbar: prefer flex layout. Brand | spacer | hamburger. Search is deferred to Phase 4.
- Theme control: bottom-left dock; make it small and nonintrusive.
- Background: keep lighter than the village ramp for both themes. Avoid stacking strong depth cues.
- Boundary: do not switch to the union route unless explicitly asked; minor seam mismatch acceptable.
- If clip paths are used, set `clipPathUnits="userSpaceOnUse"` and feed a single feature path.
- Validate with: `/api/map-settings`, `/api/villages/pins`, `/api/blocks`.
