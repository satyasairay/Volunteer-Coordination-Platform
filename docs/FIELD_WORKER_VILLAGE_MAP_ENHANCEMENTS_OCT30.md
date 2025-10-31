# Field Worker Village & Map Enhancements (Oct 30, 2025)

## Overview
- Enabled block coordinators to submit field workers for villages that are not yet stored in the database.
- Added resilient block metadata lookup backed by the Bhadrak GeoJSON so newly created villages inherit precise centroid coordinates and extents.
- Refined the public map presentation with deeper theme palettes and high-precision village labels that render cleanly at zoom.

## Backend Updates
- Introduced async helpers in `main.py` to cache and query the static `static/geojson/bhadrak_villages.geojson` file. The helpers normalise block names (with fuzzy matching) and compute lat/lng bounds once per block.
- `POST /api/field-workers` now accepts free-form village submissions:
  - Keeps the selected block in the payload, linking to existing villages when ids are supplied.
  - Generates a new `Village` + `VillagePin` when the block/name pair is missing, pre-populating map metadata via the static cache.
  - Retrofits placeholder coordinates whenever a previous submission used generic fallback coordinates.
- Coordinator dashboard view injects the user profile and block assignments into the field worker form template so the new selector defaults correctly.

## Frontend Updates (Field Worker Form)
- Added a required "Block" dropdown in `templates/field_worker_new.html` populated from `/api/villages`; falls back to the static GeoJSON when the API has no rows yet.
- Autocomplete suggestions now display `Village - Block`, store both fields, and ensure the block list always contains the selected value.
- Submit handler trims/validates `village_name`, `village_block`, and `village_id` before POSTing JSON.

## Map Presentation
- Adjusted the purple/ocean/grass themes in `templates/index.html` to deeper tones and toned-down glows.
- Added a dedicated SVG label layer: village names render with outline + fill, fade in beyond zoom level 3, and scale to avoid pixelation.
- Pin intensity now varies smoothly with zoom; labels sit above pins and share cached centroids.

## QA Summary
1. Registered a fresh block coordinator, approved via admin flow, and submitted a field worker for a previously unknown village (`Laser Crafted Village`).
2. Verified the API created `Village(id=1, block="Chandbali")` with the precise centroid/extent from the static GeoJSON and a pending field worker row.
3. Exercised `/api/villages` to confirm the new village is returned even when the SQL table was initially empty.
4. Manually inspected the map to ensure village labels appear crisp at high zoom and themes reflect the scaled palette.

All changes committed in `7351290`.

## Follow-up Fixes (Oct 30, 2025 PM)
- Resolved a regression in the field-worker submission pipeline where queries referenced non-existent `Village.village_name`/`Village.block_name` attributes; the selects now alias `Village.name`/`Village.block` so admin dashboards render submissions without Pydantic errors.
- Reconfirmed coordinator submission flow end-to-end (auto-created village + admin approvals).
- Adjusted admin approval queries and new-village pipeline to reference SQLModel `Village.name`/`Village.block` consistently, preventing pydantic attribute errors during approvals.
- On startup, the app now indexes `static/geojson/bhadrak_villages.geojson` into the `Village` table and maps geo features to database IDs so pins/labels stay in sync, with fallback markers for DB-only villages.
- Stabilized map bootstrap by defining fallback arrays upfront (e.g., `unmatchedVillages`) so the error banner no longer flashes when the map loads successfully.

## Planned Visual Polish (Draft)
- Rebalance the zoomed-in choropleth so village polygons retain subtle tone shifts without overpowering the pins; consider a faint inner shadow to separate adjacent villages.
- Replace the generic circular pins with etched badges that display village initials at max zoom while preserving the glow for quick scanning.
- When zoom level exceeds ~6, render crisp village name lettering anchored to polygon centroids, wrapped in a contrast-aware halo for readability.
- Add a hover outline plus micro-tooltip that previews `Village · Block` before opening the modal, reusing the new professional typography.
- Run a final audit so legend, footer, and zoom controls echo the sharpened aesthetic prior to hand-off.

## Oct 31, 2025 — Step 2: Etched Badges + Mercury Dots

Summary
- Introduced theme-aware etched badge pins with village initials that appear at close zoom, and replaced larger dots with smaller, glossy “mercury” micro-dots for wider views.

Pin color choices (by theme)
- Purple theme (default): `#94a3b8` (slate-silver) — harmonizes with purple gradients without overpowering choropleth.
- Ocean theme: `#7fb7d6` (sea blue) — sits softly over ocean palette.
- Grass theme: `#9cd5b4` (moss green) — complements green tones while remaining legible.

Changes
- templates/index.html
  - New helper `getPinBaseColor()` selects the base pin color per active theme.
  - Switched pin rendering to `dotStyle = 'mercury'` with a 5px glossy micro-dot that reads like a mercury droplet.
  - Added `badgeLayer` rendering SVG badge pins: 8px etched circle, white rim, inner shadow, gloss highlight, and two-letter initials.
  - Zoom behavior: micro-dots fade out at zoom ≥ 6; badges fade in from zoom 5 to 6. Labels continue to fade in beyond zoom 3.
  - Badge events: hover shows compact “Village · Block” tooltip; click opens the village modal (same as existing pins).

QA / Smoke
- FastAPI TestClient (venv) smoke unchanged and passing:
  - GET `/api/map-settings` → 200 OK
  - GET `/api/villages/pins` → 200 OK
  - GET `/api/villages/field-worker-counts` → 200 OK
  - GET `/api/blocks` → 200 OK
- Frontend verification:
  - Micro-dots appear at low/medium zoom, smaller and less distracting.
  - At zoom ≥ 6, etched badges with initials become visible and stay anchored at centroids.
  - Hover micro-tooltip and click-to-modal work from both polygon and badge interactions.

Notes
- Theme toggle persists existing behavior (reload applies new colors). Pins adopt new base color automatically after reload.
- Dots are intentionally subtle to “sit with the background”; badges carry the identity at close inspection.

## Oct 31, 2025 — Step 1: Carved Village Edges

Summary
- Added crisp, non-scaling village borders and a subtle inner shadow that activates at high zoom for a “laser-carved” separation between adjacent polygons.

Changes
- templates/index.html:548
  - `.village-polygon` now uses `vector-effect: non-scaling-stroke` and `paint-order: stroke fill markers` so borders stay sharp at high zoom and render above fills.
  - Unified hover state via `.village-polygon:hover, .village-polygon.hovered` with a subtle stroke emphasis instead of heavy darkening.
- templates/index.html:842
  - Injected an SVG `<defs><filter id="innerShadow">…</filter></defs>` and wired a GaussianBlur + arithmetic composite to create a light inner shadow effect.
- templates/index.html:989, 1002–1013
  - Kept default polygon filter as a soft drop-shadow for performance; added event handlers for hover outline + micro-tooltip scaffold.
- templates/index.html:1526–1536
  - In `zoomed()`, polygons switch to `url(#innerShadow) drop-shadow(...)` at zoom ≥ 6; otherwise revert to the original drop-shadow.
- templates/index.html:1360–1378
  - Added `showMicroTooltip(event, d)` and `moveTooltip(event)` helpers that render a compact “Village · Block” tooltip on polygon hover.

QA / Smoke
- FastAPI TestClient (venv) smoke:
  - GET `/api/map-settings` → 200 OK
  - GET `/api/villages/pins` → 200 OK
  - GET `/api/villages/field-worker-counts` → 200 OK
  - GET `/api/blocks` → 200 OK
- Manual sanity checks in the template:
  - Borders remain consistent while zooming (no excessive thickening).
  - At zoom ≥ 6, inner shadow subtly enhances polygon edges without overpowering fill.
  - Hover outline is visible; micro-tooltip shows “Village · Block”.

Notes
- Inner shadow is applied via SVG filter only at higher zoom to avoid cost at wide views.
- Labels and badge pins are untouched in this step; they will be addressed next.

## Oct 31, 2025 — Step 2R: Pin Restyle Rollback + Dark Mercury Dots

Summary
- Rolled back etched initial badge pins. Adopted small, dark micro-dots that “sit with” background palettes and fade as you zoom in.

Changes
- templates/index.html
  - Removed `badgeLayer` and all badge rendering/toggling logic.
  - Set unified dark neutral pin color `#111827` (slate-900) across themes.
  - Kept the compact “mercury” dot (≈5px) but without bright glow, for subtle presence.
  - Pins fade out at zoom ≥ 6 to declutter close-inspection views.

Validation
- FastAPI TestClient smoke:
  - GET `/api/map-settings` → 200 OK
  - GET `/api/villages/pins` → 200 OK
  - GET `/api/villages/field-worker-counts` → 200 OK
  - GET `/api/blocks` → 200 OK
- Visual: pins are subdued on all three themes and disappear at high zoom.

Next
- Step 3 will “etch” village names inside polygons at zoom ≥ 6 with a contrast-aware halo. This is documented below and will be implemented next.

## Oct 31, 2025 — Zoom Policy Update (Prune + Extend)

Summary
- Set zoom range to `[2, 10]` and initialize at `k=2` (prunes the first, widest level). Pins remain visible through `k=end` so users can retain positional context at all close zooms.

Changes
- templates/index.html
  - `d3.zoom().scaleExtent([2, 10])` and initial transform `scale(2)`.
  - `resetZoom()` returns to `k=2`.
  - Pins stay visible across the entire range (opacity ~0.6, ~0.5 beyond `k≥8`).

Rationale
- Keeping pins through the full range improves continuity while we finalize the etched label experience at high zoom.
- Pruning the first zoom reduces wide-view overdraw and aligns the default view with practical usage.

Validation
- No API changes; smoke tests unchanged and passing.

## Oct 31, 2025 — Zoom Policy Rollback

Summary
- Reverted zoom extent and behavior to the previously stable configuration to restore map load reliability.

Changes
- templates/index.html
  - `scaleExtent([1, 20])` restored.
  - Removed initial `scale(2)` transform.
  - `resetZoom()` returns to identity.
  - Pins again fade out at high zoom (≥ ~6), match prior behavior.

QA / Validation
- Backend smoke (unchanged endpoints) passing.
- Frontend: verified no early `zoomed()` transform runs before layers are initialized.

## Oct 31, 2025 — Zoom + Pins (Finalize per UX)

Summary
- Clamp zoom to `[2, 10]`, apply initial `k=2` only after all layers render.
- Pins: single bulgy deep color (navy-slate `#0b1220`) using `mercury_deep` style; remain visible through `k=end`.
- Layout: lowered map container by 8px to create breathing room under the navbar.

Changes
- templates/index.html
  - `scaleExtent([2, 10])`; initial transform applied at end of `loadMap()` via `requestAnimationFrame`.
  - Pin color unified; `dotStyle = 'mercury_deep'` with 8px glossy dome.
  - `zoomed()` keeps pin opacity ~0.6 across the range; no fade-out at high zoom.
  - `#map-container` height reduced and `margin-top: 8px` added.

Validation
- FastAPI TestClient smoke: OK (no API changes).
- Frontend sanity (manual):
  - No mixed pin colors (white vs black) — all pins share the deep neutral.
  - Initial view starts at k=2 without interfering with layer creation.
  - Map sits slightly lower; footer unchanged.

Notes
- Next step remains etched labels at k≥6 with a contrast-aware halo.

## Oct 31, 2025 — Retry Adjustments (Start as before; prune end)

Summary
- Reverted start to default k=1 (no first-zoom pruning). Set max zoom to 10 only.
- Pins hidden on start; appear when zoom > `PIN_VISIBILITY_MIN_ZOOM` (config line in template).
- Unified pin color to deep neutral `#0b1220` and ensured both main and extra pins use the same renderer.
- Pins shrink slightly toward k=10 via CSS variable `--pin-scale` for a tidy high-zoom view.

Changes
- templates/index.html
  - `d3.zoom().scaleExtent([1, 10])` and removed post-load `scale(2)`.
  - Added `const PIN_VISIBILITY_MIN_ZOOM = 2;` (tweakable).
  - Dot wrapper now uses `transform: scale(var(--pin-scale, 1))`; `zoomed()` sets `--pin-scale` from 1 → ~0.6 across k=2..10.
  - `mercury_deep` base size set to 6px; highlight kept subtle; color forced to `#0b1220` for all pins.

Validation
- FastAPI TestClient smoke: OK.
- Manual sanity: pins are hidden at start, appear after zooming beyond threshold, no white/black discrepancy, and shrink at max zoom.

## Pending / Not Yet Implemented (To Track)
- Etched village names fixed at k≥6 with contrast-aware halo; collision/overlap handling.
- Unified glass navbar + expanding search on index page (and make consistent on admin pages where applicable).
- Theme switcher UI inside navbar with 3 backgrounds fully harmonized across all pages.
- Neumorphic control buttons (plus/minus/reset) with consistent shadows, keyboard shortcuts tooltip.
- Final legend/footer aesthetic pass to match new glass style.

## Oct 31, 2025 — Pin Artifact Fix (Double Pins)

Summary
- Eliminated the “two pins per village” appearance. The lighter “second pin” was caused by separate overlay highlight elements within each dot. Replaced with a single radial-gradient highlight inside one element.

Changes
- templates/index.html
  - `getDotHTML('mercury_deep')`: removed nested highlight divs; now uses a single radial-gradient background + subtle inner shadow. Ensures exactly one dot per village visually.

Validation
- Manual: pins now render as a single bulgy deep dot with soft highlight; no adjacent light dot. Color consistent across all pins.
- Backend smoke: unchanged and passing.

## Pending / Not Yet Implemented (Nov 2025)
- Apply branding “Volunteer Management Platform” uniformly across all templates (plan approved; to verify per page after Phase 1 run).
- Map page: bottom‑left theme dock (small glass button) and “Bhadrak” label (HTML overlay) — implement with theme‑aware color.
- Lighter background gradients for Ocean/Grass so village ramp reads clearly; avoid stacked depth cues.
- Keep zoom +/- only; ensure any reset control is removed/hidden across UIs.
- Labels polish (k≥6): contrast‑aware halo and overlap handling (defer until presentation stabilizes).
- Search UI is deferred to Phase 4: left‑expanding beside brand, `/api/villages` typeahead, keyboard shortcuts.
- Boundary union and clip path moved to Backlog; static boundary is acceptable unless seam complaints increase.
