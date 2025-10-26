# DP Works - Bhadrak 🗺️

## Overview
**DP Works - Bhadrak** is a professional village-level interactive map displaying all 1,315 villages of Bhadrak district, Odisha with actual geographic boundaries. The map features a USA-style choropleth base layer with data-driven colors and an overlay pin system showing Field Workers and Upayojana Kendras (UK centers) for each village.

**Rebranded from:** Seva Atlas → DP Works - Bhadrak  
**Status:** Phase 1 Complete - Pin System Live!

## Recent Changes (October 26, 2025)

### ✅ Phase 1 Completed: Pin System with Tooltips & Modal
1. **Database Schema Added:**
   - `village_pins` table: Stores field_worker_count and uk_center_count per village
   - `custom_labels` table: Stores customizable terminology (e.g., "Field Workers" vs "Volunteers")

2. **API Endpoints Created:**
   - `/api/villages/pins` - Returns all 1,315 villages with pin data merged
   - `/api/custom-labels` - GET/PUT for label management

3. **Interactive Pin Layer:**
   - Shining blue pin markers on choropleth base
   - Data-driven gradient colors (darker = more field workers)
   - Hover tooltip shows: Village name, block, field worker count, UK center count
   - Click modal displays detailed village information
   - Click-anywhere-to-close modal behavior
   - Fully responsive and touch-friendly

4. **Admin Panel Enhancement:**
   - Label customization section added
   - Admin can change terminology (e.g., "Field Workers" → "Volunteers")
   - Real-time updates reflected on map

5. **Sample Data:**
   - 3 villages populated with pin data for testing:
     - Apanda: 12 field workers, 3 UK centers
     - Nachhipur: 8 field workers, 2 UK centers
     - Bodhapur: 15 field workers, 5 UK centers

## Project Architecture

### Technology Stack
- **Backend:** FastAPI (Python)
- **Frontend:** D3.js for map rendering, Tailwind CSS
- **Database:** PostgreSQL (Neon)
- **Maps:** GeoJSON with Mercator projection

### Key Files
- `main.py` - FastAPI application with all endpoints
- `models.py` - SQLAlchemy models (VillagePin, CustomLabel)
- `db.py` - Database connection
- `templates/index.html` - Main map interface
- `templates/admin.html` - Admin dashboard
- `static/geojson/bhadrak_villages.geojson` - 1,315 village boundaries (13MB)
- `static/geojson/bhadrak_boundary.geojson` - District boundary

### Critical Technical Decisions
1. **NEVER load bhadrak_villages.geojson in frontend** - Always use API to prevent crashes
2. **Projection fitting:** `projection.fitExtent(..., villages)` fits to villages, NOT boundary
3. **Pin architecture:** Choropleth base layer + SVG pin overlay
4. **API enrichment:** Loads all 1,315 from GeoJSON, merges pin data where exists
5. **Database constraint:** village_pins has foreign key to villages (currently only 3 rows)

### Data Flow
```
GeoJSON (1,315 villages) 
    ↓
API (/api/villages/pins)
    ↓
Merge with database pin_data (where exists)
    ↓
D3.js renders: Choropleth base + Pin overlay
```

## Admin Credentials
- **Email:** admin@example.com
- **Password:** admin123

## User Preferences
- **Budget-conscious:** User spent $30, needs focused execution
- **No rectangular blocks:** Demands real Bhadrak geography
- **Professional appearance:** USA-style choropleth
- **Full admin control:** All terminology customizable

## Future Enhancements (Not in Phase 1)
1. Populate full villages table (1,315 rows) to enable pins for all villages
2. Add more sample pin data across different blocks
3. Admin interface for adding/editing village pins
4. Bulk import for field worker data
5. Search/filter villages by name or block
6. Export village data to CSV

## Deployment
- **Target:** Autoscale (stateless web app)
- **Command:** `uvicorn main:app --host 0.0.0.0 --port 5000`
- **Environment:** Requires `MAPBOX_ACCESS_TOKEN` and `SESSION_SECRET`

## Current Status
- ✅ Choropleth base layer: ALL 1,315 villages rendering
- ✅ Pin system: 3 villages with shining markers
- ✅ Tooltip interaction: Hover to preview
- ✅ Modal system: Click for details
- ✅ Label customization: Admin can change terminology
- ⏳ Full village data population: Pending
- ⏳ Production deployment: Ready to publish

## Footer Branding
`© 2025 @dpworks Bhadrak Team. All rights reserved.`

---

**Last Updated:** October 26, 2025  
**Phase 1 Status:** ✅ Complete and Verified
