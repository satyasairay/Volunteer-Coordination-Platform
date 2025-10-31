# UI / Nav / Map Polish — Plan (Nov 2025)

This plan reflects the current, reverted codebase (tag `v2025.10.31-m2-preclip`) and the finalized design direction:
- Two themes (Ocean, Grass). The pink theme is retired.
- No search (defer to Phase 4). No union boundary. No pin changes.

## Phase 1 — Navbar + Dock (no search)
Scope
- Brand name: "Volunteer Management Platform" across templates.
- Hamburger pinned far right; hover has no movement.
- Theme toggle in a small bottom‑left dock on the map page.
- Add small "Bhadrak" label bottom‑left, outside the map boundary, HTML overlay (does not scale with zoom).

Checklist
- [x] Replace brand text in templates (about, dashboard, field_worker_new, index, login, register).
- [x] Remove floating search block from `index.html`.
- [x] Ensure `.hamburger-btn:hover` has no transform.
- [x] Add bottom‑left theme dock + Bhadrak label on map page.
- [x] Smoke test: `/api/map-settings`, `/api/villages/pins`, `/api/blocks`.

## Phase 2 — Map Presentation (two themes)
Scope
- Background lighter than village ramp for both themes; villages remain readable.
- Keep existing non‑scaling strokes. Avoid stacking depth cues (stroke OR mild bevel, not both strong).
- Pins unchanged; labels remain gated for later polish.

Checklist
- [x] Lighten background gradient.
- [x] Validate edges and readability in Ocean/Grass.

## Phase 3 — Controls + Footer (0.5–1 day)
Scope
- Zoom +/- only; reset hidden.
- Footer copy/contrast consistent across themes.

Checklist
- [x] Reset control hidden on map page.
- [x] Footer remains legible under both themes.

## Phase 4 — Search (deferred)
- Left‑expanding search beside brand; debounced `/api/villages` typeahead; keyboard `/` focus, ESC/blur close.
- Not in scope now.

## Backlog
- Optional boundary union + clip path for perfect seams (only if seam complaints increase).
- Label collision/halo tuning at k≥6.

## How to Test (quick)
- Theme toggle: Ocean/Grass switch; background clearly lighter than fills.
- Navbar: brand left, hamburger right, no search.
- Bottom‑left: theme dock + Bhadrak label present; no overlap with zoom/footer; label does not move on zoom.
- APIs: `/api/map-settings`, `/api/villages/pins`, `/api/blocks` → 200.
