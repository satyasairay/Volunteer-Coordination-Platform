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
- Added a required “Block” dropdown in `templates/field_worker_new.html` populated from `/api/villages`; falls back to the static GeoJSON when the API has no rows yet.
- Autocomplete suggestions now display `Village – Block`, store both fields, and ensure the block list always contains the selected value.
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
\n## Follow-up Fix (Oct 30, 2025 PM)\n- Resolved a regression in the field-worker submission pipeline where queries referenced non-existent \Village.village_name\/\Village.block_name\ attributes; the selects now alias \Village.name\/\Village.block\ so admin dashboards render submissions without Pydantic errors.\n- Reconfirmed coordinator submission flow end-to-end (auto-created village + admin approvals).\n\nLatest code in commit \38b25b2\.
