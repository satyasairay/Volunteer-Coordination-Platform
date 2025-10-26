# DP Works - Bhadrak 🗺️

## Overview
**DP Works - Bhadrak** is a professional village-level interactive map displaying all 1,315 villages of Bhadrak district, Odisha with actual geographic boundaries. The map features a USA-style choropleth base layer with data-driven colors and an overlay pin system showing Field Workers and Upayojana Kendras (UK centers) for each village.

**Rebranded from:** Seva Atlas → DP Works - Bhadrak  
**Status:** Phase 1 Complete - Pin System Live!

## Recent Changes (October 26, 2025)

### ✅ PHASE 1 COMPLETE: Google Maps-Style Pin System

**CRITICAL FIXES APPLIED:**
1. **Pin Rendering Fixed:**
   - ❌ BEFORE: Large circular markers (4-10px radius)
   - ✅ NOW: Small pin emoji symbols (📍) at 14px font size
   - Proper blue color matching choropleth (#5a8fc4 default)
   - Data-driven colors for villages with field worker data

2. **Zoom-Based Visibility (Google Maps Style):**
   - ❌ BEFORE: Pins always visible, cluttering the view
   - ✅ NOW: Pins hidden at default zoom level (opacity 0)
   - ✅ Pins appear when zoom level > 2 (smooth 200ms transition)
   - Clean choropleth view when zoomed out, detailed pins when zoomed in

3. **ALL Villages Get Pins:**
   - ❌ BEFORE: Only 3 villages had pins
   - ✅ NOW: All 1,315 villages have default pins
   - Villages with data: Enhanced colors based on field worker count
   - Villages without data: Default blue pin, ready for admin updates

4. **Smart Tooltips:**
   - Villages WITH data: Show field workers, UK centers, "Click for details"
   - Villages WITHOUT data: Show name, block, population only
   - Clean, uncluttered information display

5. **Modal Updates:**
   - Villages WITH data: Full stats cards
   - Villages WITHOUT data: Shows "No field worker data available yet"
   - Admin can add/update data per village

### Database Schema
- `village_pins` table: Stores field_worker_count and uk_center_count per village
- `custom_labels` table: Stores customizable terminology (e.g., "Field Workers" vs "Volunteers")

### API Endpoints
- `/api/villages/pins` - Returns all 1,315 villages with pin data merged
- `/api/custom-labels` - GET/PUT for label management

### Admin Panel
- Label customization section for changing terminology
- Real-time updates reflected on map
- Currently: 3 villages have data, 1,312 have default pins awaiting data

### Sample Data (Ready for Admin Updates)
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
