# Milestone Checkpoint — v2025.10.31-m1

Date: 2025-10-31 10:37:34
Commit: b319eaa

Scope
- Pins: single deep bulgy dot (mercury_deep), unified color #0b1220.
- Zoom: start k=1; extent [1,10]; pins hidden until zoom > 2; slight shrink toward max.
- Polygon styling: crisp borders, inner shadow at k>=6.
- Tooltip: micro tooltip for polygon hover; modal unchanged.
- Layout: map lowered by 8px under navbar.

Validation
- Backend smoke: /api/map-settings, /api/villages/pins, /api/villages/field-worker-counts, /api/blocks → 200 OK.
- Manual: no double-pin artifact; pins consistent across themes; clean load.

Notes
- Next: etched labels at k>=6 with contrast-aware halo.

