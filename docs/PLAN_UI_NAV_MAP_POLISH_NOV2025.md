# UI / Nav / Map Polish — Two‑Theme Plan (Nov 2025)

This plan is aligned to the reverted codebase (tag `v2025.10.31-m2-preclip`) and the reference UIs you shared. We are adopting two themes (Ocean, Grass) and retiring Pink. Search is deferred to Phase 4. No boundary union and no pin changes unless explicitly approved.

## Visual Analysis (from reference images)
- Backgrounds: soft multi‑stop radial/angle gradients + faint vignette; must stay lighter than the village ramp so shapes read clearly.
- Villages: 6–7 discrete shades with non‑scaling strokes; a single, tasteful depth cue (tiny inner bevel or crisp stroke) — never stacked.
- Chrome: glassmorphism navbar, compact icon buttons, consistent corner radii; neumorphic +/- zoom.
- Labeling: page caption text (e.g., “Bhadrak”) is outside the map silhouette; readable, theme‑aware, with subtle shadow.

## Phase 1 — Branding + Layout Baseline (no search)
Scope
- Brand: rename all pages to “Volunteer Management Platform”.
- Navbar: brand left; hamburger pinned far right; no hover motion.
- Theme control: bottom‑left dock on map page; small, glass button.
- Page caption: “Bhadrak” label bottom‑left, outside boundary; HTML overlay (does not scale with zoom).

Checklist
- [ ] Replace brand text in templates: index, about, dashboard, field_worker_new, login, register (and any page with `.nav-brand`).
- [ ] Ensure `.hamburger-btn:hover` has no transform/scale across templates.
- [ ] Add bottom‑left theme dock on map page only; verify no overlap with footer/zoom.
- [ ] Add small “Bhadrak” page label (HTML overlay) bottom‑left; theme‑aware color.
- [ ] Smoke: `/api/map-settings`, `/api/villages/pins`, `/api/blocks` → 200.
- [ ] Screenshot desktop/tablet/mobile.

Exit Criteria
- Navbar stable at all breakpoints; brand/hamburger positions correct; no search UI present.

## Phase 2 — Map Presentation (Ocean/Grass)
Scope
- Background: lighten gradients for both themes; add subtle vignette behind SVG.
- Villages: keep existing ramp and non‑scaling strokes; use only one depth cue (either mild bevel or crisp stroke) to avoid noisy seams.
- Boundary: keep current static boundary; minor seam mismatches are acceptable.

Checklist
- [ ] Lighten background for both themes so fills stand distinctly above bg.
- [ ] Confirm stroke width ~0.5–0.6 and opacity ~0.5–0.6; avoid stacked shadows.
- [ ] Keep pins unchanged; labels gated for later polish.
- [ ] Smoke + screenshots with themes toggled.

Exit Criteria
- Villages readable; no “cartooned” edges; background unmistakably lighter than ramp.

## Phase 3 — Controls + Footer
Scope
- Zoom +/- only; reset hidden.
- Footer caption and contrast consistent in both themes across pages.

Checklist
- [ ] Remove/reset any reset‑zoom button; keep +/- only.
- [ ] Validate footer alignment/contrast in Ocean/Grass.
- [ ] Final pass on nav/controls hover states (tint only; no motion).

Exit Criteria
- Controls and footer feel cohesive and polished under both themes.

## Documentation & Logs
- CHANGELOG: `docs/CHANGELOG_NOV2025.md` — dated entries with files changed, rationale, and QA notes.
- AGENTS: `docs/AGENTS.md` — working agreements (no union/pins; one‑change‑one‑test; anchors not regex).
- Operator Prompt: `docs/OPERATOR_PROMPT.md` — copy/paste brief for fresh sessions (rules + next actions).
- Agent Logs: `docs/AGENTLOGS/LOG_TEMPLATE.md` — template we’ll duplicate per workday.

## Backlog
- Optional: `/api/boundary/union` + clipPath for perfect seams (only if seam feedback increases).
- Label collision/halo tuning for k≥6 once map presentation stabilizes.
- Search (Phase 4): left‑expanding input beside brand; `/api/villages` typeahead; keyboard `/` focus, ESC/blur close.

## How to Test (quick)
- Theme toggle Ocean/Grass: background clearly lighter than fills; no pin changes.
- Navbar: brand left, hamburger right, no search.
- Bottom‑left: theme dock + “Bhadrak” label present; no overlap with footer/zoom; label does not move with zoom.
- APIs: `/api/map-settings`, `/api/villages/pins`, `/api/blocks` → 200.

### Encoding / Icon Failures — Root Cause & Fix
- Root cause: pasting emoji/icon glyphs into templates led to mojibake on some systems (non‑UTF8 round‑trips, CRLF normalization), producing unreadable characters and broken UI.
- Decision: remove non‑ASCII from all templates and replace decorative icons with inline SVGs only.
- Policy: no emoji fonts in HTML; only SVG or web icon sets, and ensure `meta charset="UTF-8"` is present.
- Status: non‑ASCII sanitized across `templates/*.html` as a recovery step. SVG replacements will be introduced progressively under Phase 3 (controls) or Phase 4 (search).
