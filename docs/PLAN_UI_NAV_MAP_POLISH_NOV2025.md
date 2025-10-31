# UI/Nav/Map Polish — 3‑Phase Plan (Nov 2025)

## Goals
- Unify the three themes (Purple, Ocean, Grass) across backgrounds, navbar, map, and controls.
- Add compact search that expands left in navbar, and theme switcher.
- Preserve performance (single villages payload, group filters only).

## Phase 1 — Navbar + Theming (1–2 days)
- Glass nav bar (blur 20–24px, inner highlight + outer border, soft shadow).
- Search icon → expands left to 260px input; ‘/’ focuses, ESC collapses; debounced `/api/villages` typeahead.
- Theme switcher (3 presets) reusing current body classes; persists in `localStorage`.
- Background gradients per theme (radial + vignette) via CSS variables.

Checklist
- [ ] Add nav HTML: brand, search button+input, theme button, menu.
- [ ] CSS: glass tokens, spacing, icon button states, responsive collapse.
- [ ] JS: search toggle, debounce(180ms), keyboard shortcuts, ARIA roles, outside‑click.
- [ ] Theme token map for 3 palettes (bg, ramp, borders, glow).
- [ ] Non‑blocking load; no layout shift when expanding.

Acceptance
- 60fps nav expand/collapse on mid‑tier laptop.
- Theme change < 100ms; persists after reload.

## Phase 2 — Map Polish (1–2 days)
- District silhouette layer with soft shadow; villages inside with 6–7 ramp.
- Non‑scaling 0.7–0.9px stroke; bevel via dual stroke (inner light, outer dark) or one group filter.
- Hover micro‑outline + tooltip consistent with nav style.
- Pins: current deep 6px dots, hidden until `PIN_VISIBILITY_MIN_ZOOM`; shrink near k=10.

Checklist
- [ ] One `<defs>` filter for villages group only (no per‑feature filters).
- [ ] Quantize label sizing; etched labels at k≥6 with halo (contrast‑aware).
- [ ] Verify stroke crispness at k=1–3.
- [ ] Keep GPU time stable (< 12ms at k=2 on mid‑tier).

Acceptance
- Labels readable at k≥6, no overlap explosion; polygons crisp at k=1.

## Phase 3 — Controls + Footer (0.5–1 day)
- Neumorphic +/−/reset; bottom‑right caption harmonized.
- Small help/about in menu; keyboard: +/−/0, / for search.

Checklist
- [ ] Control shadows (ambient + directional), focus rings.
- [ ] Caption font/spacing consistent with nav.
- [ ] Keyboard map documented in footer tooltip.

## QA Plan
- Smoke: `/api/map-settings`, `/api/villages/pins`, `/api/blocks`.
- Visual snapshots: k=1, k=3, k=6, k=10 for 3 themes (9 images).
- Accessibility: color contrast (WCAG AA) for labels/tooltips; tab order for search.

## Rollback Strategy
- Feature flags in `mapSettings` for: labels_etched, glass_nav, new_controls.
- Revert CSS variables to previous palette if perf drops.

