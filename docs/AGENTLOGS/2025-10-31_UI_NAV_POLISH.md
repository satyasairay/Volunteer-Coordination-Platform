# Agent Log — UI/Nav/Map Polish (2025-10-31)

## Decisions
- Keep single villages payload; avoid zoom-based endpoints.
- Pins unified to deep color `#0b1220`, hidden until zoom > 2.
- Zoom extent `[1,10]`; etched labels planned at k≥6.

## Actions
- Reworked pin HTML to single-element radial gradient (fixed double-pin artifact).
- Restored stable zoom init; added `PIN_VISIBILITY_MIN_ZOOM` knob.
- Lowered map container by 8px.

## Next Up
- Implement glass nav + expanding search; theme switch harmonized across pages.
- Etched labels with halo; group filter only.

## Checks
- TestClient smoke: all 200 OK (map settings, pins, FW counts, blocks).
- Manual: no mixed pin colors; crisp polygons.

## Notes
- Use one `<defs>` filter for villages; avoid per-feature filters to keep GPU time low.
